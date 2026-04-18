#!/usr/bin/env python3
"""Mechanical gate check for design-intake bundles.

Runs the seven gates defined in references/self-check-gates.md against a
design.tokens.yaml file and optionally rendered sample HTML. Emits a JSON
report that the skill pastes verbatim into upload-checklist.md.

Usage:
    gate-check.py <tokens.yaml> [--projection] [--samples <dir>]

Exit codes:
    0 — all gates pass or have complete structured overrides
    1 — one or more gates fail (structured override missing or malformed)
    2 — input file invalid or cannot be loaded
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
    sys.stderr.write(
        "PyYAML required: pip install pyyaml\n"
        "If running under Claude Code, the skill host should provide it.\n"
    )
    sys.exit(2)


SKILL_VERSION = "4.5"


# --- Color helpers ----------------------------------------------------------


def _hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    s = hex_str.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"bad hex: {hex_str}")
    r, g, b = (int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return r, g, b


def _relative_luminance(hex_str: str) -> float:
    r, g, b = _hex_to_rgb(hex_str)

    def _lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    lf = _relative_luminance(fg_hex)
    lb = _relative_luminance(bg_hex)
    light, dark = max(lf, lb), min(lf, lb)
    return (light + 0.05) / (dark + 0.05)


def _hsl_l_percent(hex_str: str) -> float:
    r, g, b = _hex_to_rgb(hex_str)
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx + mn) / 2.0 * 100.0


# --- Token resolution -------------------------------------------------------


TOKEN_REF = re.compile(r"\{([a-zA-Z0-9_.\-]+)\}")


def _walk(tree: dict, prefix: str = "") -> list[tuple[str, object]]:
    out: list[tuple[str, object]] = []
    for k, v in tree.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.extend(_walk(v, path))
        else:
            out.append((path, v))
    return out


def _defined_paths(tree: dict) -> set[str]:
    """Every leaf path AND every intermediate dict path.

    References can point to either a leaf value or a dict node (e.g.,
    {color.neutral.50} may resolve to {hex: ..., hsl: ...}). Both must
    count as defined.
    """
    leaves = {p for p, _ in _walk(tree)}
    intermediates: set[str] = set()
    for p in leaves:
        parts = p.split(".")
        for i in range(1, len(parts)):
            intermediates.add(".".join(parts[:i]))
    return leaves | intermediates


def _find_references(tree: dict) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for path, val in _walk(tree):
        if isinstance(val, str):
            for m in TOKEN_REF.finditer(val):
                refs.append((path, m.group(1)))
    return refs


def _resolve(tree: dict, path: str) -> object | None:
    node: object = tree
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def _resolve_to_hex(tree: dict, ref_path: str, visited: set[str] | None = None) -> str | None:
    visited = visited or set()
    if ref_path in visited:
        return None
    visited.add(ref_path)
    val = _resolve(tree, ref_path)
    if val is None:
        return None
    if isinstance(val, str):
        m = TOKEN_REF.search(val)
        if m:
            return _resolve_to_hex(tree, m.group(1), visited)
        if val.startswith("#"):
            return val
    if isinstance(val, dict) and "hex" in val and isinstance(val["hex"], str):
        return val["hex"]
    return None


# --- Override validation ----------------------------------------------------


REQUIRED_REASON_FIELDS = {"context-assumption", "why-default-insufficient", "upgrade-cost"}


def _validate_override(entry: dict) -> list[str]:
    errors: list[str] = []
    reason = entry.get("reason")
    if not isinstance(reason, dict):
        errors.append("reason must be a mapping with three fields")
    else:
        missing = REQUIRED_REASON_FIELDS - set(reason.keys())
        if missing:
            errors.append(f"reason missing fields: {sorted(missing)}")
        for field in REQUIRED_REASON_FIELDS & set(reason.keys()):
            val = reason[field]
            if not isinstance(val, str) or len(val.strip()) < 12:
                errors.append(f"reason.{field} too short or not a string")

    scope = entry.get("scope")
    if not isinstance(scope, list) or not scope:
        errors.append("scope must be a non-empty list of glob patterns")
    elif any(s == "*" for s in scope) and len(scope) == 1:
        errors.append("scope wildcard '*' alone is forbidden; use a companion override")

    return errors


# --- Gates ------------------------------------------------------------------


def gate_contrast(tree: dict, overrides: dict[str, dict]) -> dict:
    """Gate 1: tiered contrast check (text / ui / decoration)."""
    tiers = (tree.get("color", {}).get("contrast", {}).get("tier") or {})
    if not tiers:
        # Default tier assumption: text=AA
        tiers = {"text": "AA", "ui": "AA", "decoration": "free"}

    thresholds = {
        "AA": {"body": 4.5, "large": 3.0},
        "AAA": {"body": 7.0, "large": 4.5},
    }

    # Collect pairs declared in components — (fg, bg) from state entries
    comps = tree.get("components", {})
    failures: list[str] = []
    for comp_name, comp in comps.items():
        if not isinstance(comp, dict):
            continue
        variants = comp.get("variants", {})
        for vname, variant in (variants or {}).items():
            if not isinstance(variant, dict):
                continue
            for state_name, state in variant.items():
                if not isinstance(state, dict):
                    continue
                fg_ref = state.get("fg")
                bg_ref = state.get("bg")
                if not (isinstance(fg_ref, str) and isinstance(bg_ref, str)):
                    continue
                m_fg = TOKEN_REF.search(fg_ref)
                m_bg = TOKEN_REF.search(bg_ref)
                if not (m_fg and m_bg):
                    continue
                fg_hex = _resolve_to_hex(tree, m_fg.group(1))
                bg_hex = _resolve_to_hex(tree, m_bg.group(1))
                if not (fg_hex and bg_hex):
                    continue
                ratio = _contrast_ratio(fg_hex, bg_hex)
                tier = "text"  # components default to text tier
                required = thresholds.get(tiers.get(tier, "AA"), thresholds["AA"])["body"]
                if ratio + 0.05 < required:
                    failures.append(
                        f"component.{comp_name}.variants.{vname}.{state_name}: "
                        f"{fg_hex} on {bg_hex} = {ratio:.2f}:1 (< {required})"
                    )

    if not failures:
        return {"status": "pass"}
    if "contrast" in overrides:
        errors = _validate_override(overrides["contrast"])
        if errors:
            return {"status": "fail", "reason": "contrast override malformed", "errors": errors, "details": failures}
        return {"status": "override", "override_id": overrides["contrast"].get("id", "contrast-ovr"), "details": failures}
    return {"status": "fail", "details": failures}


def gate_neutral_scale(tree: dict, overrides: dict[str, dict]) -> dict:
    """Gate 2: neutral scale has ≥ 9 stops with ≥ 5% L* delta."""
    neutral = (tree.get("color", {}) or {}).get("neutral", {})
    stops: list[tuple[str, str]] = []
    for k, v in (neutral or {}).items():
        if isinstance(v, dict):
            hx = v.get("hex")
            if isinstance(hx, str):
                stops.append((str(k), hx))
        elif isinstance(v, str) and v.startswith("#"):
            stops.append((str(k), v))
    n = len(stops)
    if n >= 9:
        # Check monotonic L* with ≥ 5% delta between adjacent stops
        try:
            sorted_stops = sorted(stops, key=lambda s: _hsl_l_percent(s[1]))
            deltas = [
                _hsl_l_percent(sorted_stops[i + 1][1]) - _hsl_l_percent(sorted_stops[i][1])
                for i in range(len(sorted_stops) - 1)
            ]
            small = [(sorted_stops[i][0], sorted_stops[i + 1][0], d) for i, d in enumerate(deltas) if d < 5.0]
            if small:
                return {
                    "status": "warn",
                    "notes": f"{len(small)} adjacent stop-pair(s) with L* delta < 5%",
                    "pairs": small,
                }
            return {"status": "pass", "tier": n}
        except ValueError as e:
            return {"status": "fail", "error": str(e)}

    # Fewer than 9 — require override
    if "neutral-scale" in overrides:
        errors = _validate_override(overrides["neutral-scale"])
        if errors:
            return {"status": "fail", "reason": "neutral-scale override malformed", "errors": errors, "tier": n}
        return {"status": "override", "tier": n, "override_id": overrides["neutral-scale"].get("id", "neutral-ovr")}
    return {"status": "fail", "tier": n, "required": 9}


def gate_triad_x_5state(tree: dict, overrides: dict[str, dict]) -> dict:
    """Gate 3: triad + 3 composites × states, fully declared."""
    required_components = {"button", "input", "card", "nav-item", "list-row", "form-row"}
    state_sets = {
        "interactive-5state": {"default", "hover", "focus", "active", "disabled"},
        "form-5state": {"default", "hover", "focus", "disabled", "error"},
        "nav-selected": {"default", "active", "disabled"},
    }
    comps = tree.get("components", {}) or {}
    missing = [c for c in required_components if c not in comps]
    gaps: list[str] = []
    for cname in required_components & set(comps.keys()):
        comp = comps[cname]
        if not isinstance(comp, dict):
            gaps.append(f"{cname}: not a mapping")
            continue
        extends = comp.get("extends")
        declared_states: set[str] = set(comp.get("states", []))
        if extends and extends in state_sets:
            declared_states |= state_sets[extends]
        if not declared_states:
            gaps.append(f"{cname}: no extends and no explicit states")
            continue
        # Look for state entries at top level or inside variants
        present: set[str] = set()
        variants = comp.get("variants", {})
        if isinstance(variants, dict) and variants:
            for vname, v in variants.items():
                if isinstance(v, dict):
                    present |= set(v.keys())
        else:
            present |= {k for k in comp.keys() if k not in {"base", "variants", "extends", "states", "omit-states"}}
        omit = set(comp.get("omit-states", []))
        required_here = declared_states - omit
        diff = required_here - present
        if diff:
            gaps.append(f"{cname}: missing states {sorted(diff)}")

    if missing:
        gaps.append(f"missing components entirely: {sorted(missing)}")

    if not gaps:
        return {"status": "pass"}
    if "triad-x-5state" in overrides:
        errors = _validate_override(overrides["triad-x-5state"])
        if errors:
            return {"status": "fail", "errors": errors, "gaps": gaps}
        return {"status": "override", "override_id": overrides["triad-x-5state"].get("id", "triad-ovr"), "gaps": gaps}
    return {"status": "fail", "gaps": gaps}


def gate_dark_explicit(tree: dict, overrides: dict[str, dict]) -> dict:
    """Gate 4: every color.semantic.* has an explicit color.dark.semantic.*."""
    color = tree.get("color", {}) or {}
    if "dark" not in color:
        return {"status": "pass", "notes": "light-only product"}
    semantic = color.get("semantic", {})
    dark_semantic = (color.get("dark", {}) or {}).get("semantic", {})
    missing: list[str] = []
    for path, _ in _walk(semantic if isinstance(semantic, dict) else {}):
        if _resolve(dark_semantic if isinstance(dark_semantic, dict) else {}, path) is None:
            missing.append(f"semantic.{path}")
    # Also reject string "auto-invert" anywhere in dark.*
    bad_auto: list[str] = []
    for path, val in _walk(color.get("dark", {}) or {}):
        if isinstance(val, str) and "auto" in val.lower() and "invert" in val.lower():
            bad_auto.append(f"dark.{path} = {val!r}")

    if not missing and not bad_auto:
        return {"status": "pass"}
    return {"status": "fail", "missing_dark": missing, "auto_invert": bad_auto}


def gate_token_closure(tree: dict) -> dict:
    """Gate 5: every {...} reference resolves; components have no raw hex/px."""
    defined = _defined_paths(tree)
    refs = _find_references(tree)
    unresolved = [(src, tgt) for src, tgt in refs if tgt not in defined]
    raw_hex: list[str] = []
    raw_px: list[str] = []
    comps = tree.get("components", {}) or {}
    # Fields where raw "1px" / "2px" are idiomatic CSS border widths and
    # don't need a spacing-token reference. Exclude these from the raw-px
    # check; keep the check active on padding/gap/margin/size paths.
    border_idiom_fields = {"border", "border-bottom", "border-top",
                           "border-left", "border-right", "outline", "ring",
                           "hairline"}
    for path, val in _walk(comps):
        if isinstance(val, str):
            if re.fullmatch(r"#[0-9a-fA-F]{3,8}", val):
                raw_hex.append(f"components.{path} = {val!r}")
            leaf = path.rsplit(".", 1)[-1]
            if leaf in border_idiom_fields:
                continue
            # Flag raw px only when the value is a bare number + px (and no
            # token reference). Compound strings like "1px solid {...}" are
            # fine.
            if re.fullmatch(r"\s*\d+\s*px\s*", val) and "{" not in val:
                raw_px.append(f"components.{path} = {val!r}")
    if not unresolved and not raw_hex and not raw_px:
        return {"status": "pass"}
    # token-closure is never overrideable
    return {
        "status": "fail",
        "unresolved_refs": [f"{s} → {{{t}}}" for s, t in unresolved],
        "raw_hex_in_components": raw_hex,
        "raw_px_in_components": raw_px,
    }


def gate_affordance(tree: dict, overrides: dict[str, dict]) -> dict:
    """Gate 6 (v4.5): interactive default states have visible affordance."""
    comps = tree.get("components", {}) or {}
    interactive = {"input", "button", "nav-item"}
    failures: list[str] = []
    for cname in interactive & set(comps.keys()):
        comp = comps[cname]
        if not isinstance(comp, dict):
            continue
        default = comp.get("default")
        if default is None:
            variants = comp.get("variants", {})
            for v in (variants or {}).values():
                if isinstance(v, dict) and "default" in v:
                    default = v["default"]
                    break
        if not isinstance(default, dict):
            continue
        affordance_keys = {"border", "bg", "border-bottom", "border-top", "border-left", "border-right", "icon", "outline"}
        has_key = any(k in default for k in affordance_keys)
        label_always = default.get("label-always-visible") is True
        if not (has_key or label_always):
            failures.append(f"{cname}.default has no border / bg / icon / permanent label")
    if not failures:
        return {"status": "pass"}
    if "affordance" in overrides:
        errors = _validate_override(overrides["affordance"])
        if errors:
            return {"status": "fail", "errors": errors, "details": failures}
        return {"status": "override", "override_id": overrides["affordance"].get("id", "affordance-ovr"), "details": failures}
    return {"status": "fail", "details": failures}


def gate_viewport_type(tree: dict, samples_dir: Path | None) -> dict:
    """Gate 7 (v4.5): typography readability at primary viewport.

    Without a real headless renderer we perform a best-effort static check:
    verify scale sizes are above the readability floor for their role.
    """
    typo = (tree.get("typography", {}) or {}).get("scale", {})
    floors = {"body": 12, "caption": 10, "button": 13, "small": 12, "micro": 10}
    warnings: list[str] = []
    for role, entry in (typo or {}).items():
        if not isinstance(entry, dict):
            continue
        size = entry.get("size") or entry.get("px")
        if isinstance(size, (int, float)):
            floor = floors.get(role, 0)
            if floor and size < floor:
                warnings.append(f"typography.scale.{role}.size = {size}px below readability floor {floor}px")
    if not warnings:
        return {"status": "pass"}
    return {"status": "warn", "notes": warnings}


# --- Runner -----------------------------------------------------------------


def collect_overrides(tree: dict) -> dict[str, dict]:
    overrides = tree.get("overrides", [])
    if isinstance(overrides, list):
        return {o.get("gate"): o for o in overrides if isinstance(o, dict) and "gate" in o}
    return {}


def run(tokens_path: Path, projection: bool, samples_dir: Path | None) -> dict:
    with tokens_path.open("r", encoding="utf-8") as f:
        tree = yaml.safe_load(f) or {}
    overrides = collect_overrides(tree)

    gates = {
        "contrast": gate_contrast(tree, overrides),
        "neutral-scale": gate_neutral_scale(tree, overrides),
        "triad-x-5state": gate_triad_x_5state(tree, overrides),
        "dark-explicit": gate_dark_explicit(tree, overrides),
        "token-closure": gate_token_closure(tree),
        "affordance": gate_affordance(tree, overrides),
        "viewport-type": gate_viewport_type(tree, samples_dir),
    }

    decision = "advance"
    for name, result in gates.items():
        if result["status"] == "fail":
            decision = "block"
            break

    report = {
        "skill_version": SKILL_VERSION,
        "tokens_file": str(tokens_path),
        "gates": gates,
        "overrides": list(overrides.values()),
        "decision": decision,
    }

    if projection:
        report["projection_hint"] = (
            "Run token-lint.py and review design.md § out-of-schema for the "
            "full schema-projection report. gate-check.py only surfaces gate "
            "failures and overrides; projection tags live in references/"
            "schema-projection.md."
        )

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="design-intake gate-check")
    parser.add_argument("tokens", type=Path, help="path to design.tokens.yaml")
    parser.add_argument("--projection", action="store_true", help="include projection hint")
    parser.add_argument("--samples", type=Path, default=None, help="dir containing sample HTML")
    args = parser.parse_args(argv)

    if not args.tokens.is_file():
        sys.stderr.write(f"not a file: {args.tokens}\n")
        return 2

    try:
        report = run(args.tokens, args.projection, args.samples)
    except (yaml.YAMLError, ValueError) as e:  # type: ignore[attr-defined]
        sys.stderr.write(f"input error: {e}\n")
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "advance" else 1


if __name__ == "__main__":
    sys.exit(main())
