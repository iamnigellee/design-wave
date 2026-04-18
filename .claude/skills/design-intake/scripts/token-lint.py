#!/usr/bin/env python3
"""Positive-constraint linter for design-intake bundles.

Every positive constraint declared in design.tokens.yaml's
`positive_constraints:` block is enforced here. Unlike gates, positive
constraints cannot be overridden within a run — they are self-imposed brand
rules. A failure means either the token is wrong, or the constraint should be
removed from the bundle entirely.

Supported positive-constraint ids (extend by subclassing or adding handlers):
    palette-lock        — all color tokens subset of an external palette
    grid-N              — all sizing / spacing multiples of N
    motion-stepped-only — motion.timing-fn only uses type: steps
    radius-cap:<n>      — radius values ≤ n unless explicitly named exception
    material-policy     — material finish whitelist / blacklist
    palette-material-binding — material.*.color* references palette tokens
    weights-restricted  — typography weights drawn from a whitelist

Usage:
    token-lint.py <tokens.yaml> [--positive <id>] [--positive <id>] ...

If no --positive flags supplied, all constraints declared in the tokens file
are checked. Exit codes match gate-check.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)


TOKEN_REF = re.compile(r"\{([a-zA-Z0-9_.\-]+)\}")
HEX_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}")


# --- Generic helpers --------------------------------------------------------


def _walk(tree: dict, prefix: str = "") -> list[tuple[str, object]]:
    out: list[tuple[str, object]] = []
    for k, v in tree.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.extend(_walk(v, path))
        else:
            out.append((path, v))
    return out


def _glob_match(pattern: str, path: str) -> bool:
    """Support * and ** style globs."""
    regex = re.escape(pattern).replace(r"\*\*", ".+").replace(r"\*", r"[^.]+")
    return re.fullmatch(regex, path) is not None


def _paths_matching(tree: dict, globs: list[str]) -> list[tuple[str, object]]:
    walked = _walk(tree)
    return [(p, v) for (p, v) in walked if any(_glob_match(g, p) for g in globs)]


# --- Constraint handlers ----------------------------------------------------


def _palette_hex_set(tree: dict, source_hex: list[str] | None, palette_scope: list[str]) -> set[str]:
    """Collect the allowed hex set for palette-lock.

    If `source_hex` explicitly supplied, use it. Otherwise walk palette
    tokens under `palette_scope` globs and collect their hex values.
    """
    if source_hex:
        return {h.lower() for h in source_hex}

    allowed: set[str] = set()
    for _, val in _paths_matching(tree, palette_scope):
        if isinstance(val, str) and HEX_LITERAL.fullmatch(val):
            allowed.add(val.lower())
        elif isinstance(val, dict) and isinstance(val.get("hex"), str):
            allowed.add(val["hex"].lower())
    return allowed


def check_palette_lock(tree: dict, rule: dict) -> dict:
    """All hex values in scope must belong to the palette source set."""
    scope = rule.get("scope", ["color.*"])
    source = rule.get("source_hex")  # optional explicit allowed set
    palette_scope = rule.get("palette_scope", ["color.neutral.*", "color.accent.*", "color.primary.*", "color.bg.*", "color.ink.*", "color.signal.*"])
    allowed = _palette_hex_set(tree, source, palette_scope)

    violations: list[str] = []
    for path, val in _paths_matching(tree, scope):
        if isinstance(val, str) and HEX_LITERAL.fullmatch(val):
            if val.lower() not in allowed:
                violations.append(f"{path} = {val} not in palette")
        elif isinstance(val, dict) and isinstance(val.get("hex"), str):
            if val["hex"].lower() not in allowed:
                violations.append(f"{path}.hex = {val['hex']} not in palette")

    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_grid_n(tree: dict, rule: dict) -> dict:
    n = rule.get("n")
    if not isinstance(n, int) or n <= 0:
        return {"status": "fail", "error": "grid-N rule missing valid 'n'"}
    scope = rule.get("scope", ["spacing.*", "layout.*", "components.*.base.padding", "components.*.base.gap"])

    exceptions = set(rule.get("exceptions", []))
    violations: list[str] = []

    for path, val in _paths_matching(tree, scope):
        if path in exceptions:
            continue
        if isinstance(val, list):
            bad = [x for x in val if isinstance(x, (int, float)) and float(x) % n != 0]
            if bad:
                violations.append(f"{path} contains non-multiples of {n}: {bad}")
        elif isinstance(val, (int, float)):
            if float(val) % n != 0:
                violations.append(f"{path} = {val} not multiple of {n}")
        elif isinstance(val, str):
            for num_match in re.finditer(r"\b(\d+)(?:px|rem)?\b", val):
                num = int(num_match.group(1))
                if num % n != 0 and num not in {0}:
                    violations.append(f"{path} contains {num}{num_match.group(0)[len(num_match.group(1)):]} not multiple of {n}")
                    break

    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_motion_stepped_only(tree: dict, rule: dict) -> dict:
    fns = (tree.get("motion", {}) or {}).get("timing-fn", {})
    violations: list[str] = []
    for name, entry in (fns or {}).items():
        if isinstance(entry, dict):
            t = entry.get("type")
            if t != "steps":
                violations.append(f"motion.timing-fn.{name}.type = {t!r}, expected 'steps'")
        elif isinstance(entry, str):
            if "step" not in entry.lower():
                violations.append(f"motion.timing-fn.{name} = {entry!r} is not a steps function")
    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_radius_cap(tree: dict, rule: dict) -> dict:
    cap = rule.get("cap")
    if not isinstance(cap, (int, float)):
        return {"status": "fail", "error": "radius-cap rule missing 'cap'"}
    exceptions = set(rule.get("exceptions", []))
    radius = tree.get("radius", {}) or {}
    violations: list[str] = []
    for name, val in radius.items():
        if name in exceptions:
            continue
        if isinstance(val, (int, float)) and float(val) > cap and val != 9999:
            # 9999 / full is conventionally "pill" and always allowed
            violations.append(f"radius.{name} = {val} exceeds cap {cap}")
    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_material_policy(tree: dict, rule: dict) -> dict:
    """Whitelist / blacklist material finish types."""
    whitelist = set(rule.get("whitelist") or [])
    blacklist = set(rule.get("blacklist") or [])
    material = tree.get("material", {}) or {}
    declared = set(k for k in material.keys() if k != "composite")
    composite = material.get("composite", {}) or {}
    for comp in composite.values():
        if isinstance(comp, dict):
            for layer in comp.get("layers", []) or []:
                if isinstance(layer, dict) and "type" in layer:
                    declared.add(layer["type"])

    violations: list[str] = []
    if whitelist:
        extra = declared - whitelist
        if extra:
            violations.append(f"material uses non-whitelisted finishes: {sorted(extra)}")
    if blacklist:
        forbidden = declared & blacklist
        if forbidden:
            violations.append(f"material uses blacklisted finishes: {sorted(forbidden)}")
    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_palette_material_binding(tree: dict, rule: dict) -> dict:
    """Material layers must reference palette tokens, not raw hex."""
    material = tree.get("material", {}) or {}
    violations: list[str] = []

    def _scan(obj: object, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                _scan(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _scan(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            if HEX_LITERAL.fullmatch(obj):
                violations.append(f"material.{path} = {obj} should reference a palette token")

    _scan(material, "")
    return {"status": "pass" if not violations else "fail", "violations": violations}


def check_weights_restricted(tree: dict, rule: dict) -> dict:
    allowed = set(rule.get("allowed") or [])
    if not allowed:
        return {"status": "fail", "error": "weights-restricted rule missing 'allowed' set"}
    scale = (tree.get("typography", {}) or {}).get("scale", {})
    violations: list[str] = []
    for role, entry in (scale or {}).items():
        if isinstance(entry, dict) and "weight" in entry:
            if entry["weight"] not in allowed:
                violations.append(f"typography.scale.{role}.weight = {entry['weight']} not in {sorted(allowed)}")
    return {"status": "pass" if not violations else "fail", "violations": violations}


HANDLERS = {
    "palette-lock": check_palette_lock,
    "motion-stepped-only": check_motion_stepped_only,
    "material-policy": check_material_policy,
    "palette-material-binding": check_palette_material_binding,
    "weights-restricted": check_weights_restricted,
}


def dispatch(rule: dict, tree: dict) -> dict:
    rid = rule.get("id", "")
    if rid in HANDLERS:
        return HANDLERS[rid](tree, rule)
    if rid.startswith("grid-"):
        try:
            n = int(rid.split("-", 1)[1])
            rule.setdefault("n", n)
            return check_grid_n(tree, rule)
        except (ValueError, IndexError):
            return {"status": "fail", "error": f"malformed grid-N id: {rid}"}
    if rid.startswith("radius-cap"):
        # format: radius-cap:8 or radius-cap (cap in rule dict)
        if ":" in rid:
            try:
                rule.setdefault("cap", float(rid.split(":", 1)[1]))
            except ValueError:
                return {"status": "fail", "error": f"malformed radius-cap id: {rid}"}
        return check_radius_cap(tree, rule)
    return {"status": "skip", "notes": f"no handler for constraint id {rid!r}"}


# --- Runner -----------------------------------------------------------------


def run(tokens_path: Path, requested: list[str] | None) -> dict:
    with tokens_path.open("r", encoding="utf-8") as f:
        tree = yaml.safe_load(f) or {}

    rules = tree.get("positive_constraints", []) or []
    if not isinstance(rules, list):
        return {"error": "positive_constraints must be a list", "status": "fail"}

    if requested:
        rules = [r for r in rules if isinstance(r, dict) and r.get("id") in requested]

    results: list[dict] = []
    decision = "pass"
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        result = dispatch(rule, tree)
        result["id"] = rule.get("id")
        result["rule"] = rule.get("rule")
        results.append(result)
        if result["status"] == "fail":
            decision = "fail"

    return {
        "skill_version": "4.5",
        "tokens_file": str(tokens_path),
        "constraints_checked": len(results),
        "decision": decision,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="design-intake token-lint")
    parser.add_argument("tokens", type=Path)
    parser.add_argument("--positive", action="append", default=None,
                        help="run only this constraint id (repeatable)")
    args = parser.parse_args(argv)

    if not args.tokens.is_file():
        sys.stderr.write(f"not a file: {args.tokens}\n")
        return 2
    try:
        report = run(args.tokens, args.positive)
    except (yaml.YAMLError, ValueError) as e:  # type: ignore[attr-defined]
        sys.stderr.write(f"input error: {e}\n")
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("decision") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
