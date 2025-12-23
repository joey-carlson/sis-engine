from __future__ import annotations

# Ensure repo root is on sys.path when running via `streamlit run`.
import sys
from pathlib import Path as _Path
_REPO_ROOT = _Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from spar_engine.content import load_pack
from spar_engine.engine import generate_event
from spar_engine.models import Constraints, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.state import apply_state_delta, tick_state

from streamlit_harness.harness_state import HarnessState


DEFAULT_PACK = "data/core_complications_v0_1.json"


def split_csv(v: str) -> List[str]:
    if not v:
        return []
    return [x.strip() for x in v.split(",") if x.strip()]


def scene_preset_values(preset: str) -> Dict[str, Any]:
    preset = (preset or "").strip().lower()
    if preset == "dungeon":
        return {"env": ["dungeon"], "confinement": 0.8, "connectivity": 0.3, "visibility": 0.6}
    if preset == "city":
        return {"env": ["city"], "confinement": 0.4, "connectivity": 0.8, "visibility": 0.7}
    if preset == "wilderness":
        return {"env": ["wilderness"], "confinement": 0.3, "connectivity": 0.5, "visibility": 0.4}
    if preset == "ruins":
        return {"env": ["ruins"], "confinement": 0.6, "connectivity": 0.4, "visibility": 0.5}
    return {"env": ["dungeon"], "confinement": 0.5, "connectivity": 0.5, "visibility": 0.5}


def get_hs() -> HarnessState:
    """Get or initialize the harness state singleton."""
    if "hs" not in st.session_state or not isinstance(st.session_state.hs, HarnessState):
        st.session_state.hs = HarnessState()
    return st.session_state.hs


def load_entries(pack_path: str):
    p = Path(pack_path)
    if not p.exists():
        raise FileNotFoundError(f"Pack not found: {pack_path}")
    return load_pack(p)


def derive_tag_vocab(entries) -> List[str]:
    s = set()
    for e in entries:
        for t in e.tags:
            s.add(t)
    return sorted(s)


def event_to_dict(ev) -> Dict[str, Any]:
    d = ev.__dict__.copy()
    d["effect_vector"] = ev.effect_vector.__dict__
    d["fiction"] = ev.fiction.__dict__
    d["state_delta"] = ev.state_delta.__dict__
    return d


def summarize_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    severities = [int(e.get("severity", 0)) for e in events]
    cutoff_count = sum(1 for e in events if e.get("cutoff_applied"))

    buckets = {"1-3": 0, "4-6": 0, "7-10": 0}
    for s in severities:
        if s <= 3:
            buckets["1-3"] += 1
        elif s <= 6:
            buckets["4-6"] += 1
        else:
            buckets["7-10"] += 1

    tag_counts = Counter()
    id_counts = Counter()
    resolution_counts = Counter()
    for e in events:
        id_counts[e.get("event_id")] += 1
        resolution_counts[str(e.get("cutoff_resolution", "none"))] += 1
        for t in e.get("tags", []) or []:
            tag_counts[t] += 1

    return {
        "n": len(events),
        "cutoff_rate": (cutoff_count / max(1, len(events))),
        "severity_buckets": buckets,
        "severity_min": min(severities) if severities else None,
        "severity_max": max(severities) if severities else None,
        "severity_avg": (sum(severities) / len(severities)) if severities else None,
        "top_tags": tag_counts.most_common(15),
        "top_event_ids": id_counts.most_common(15),
        "cutoff_resolutions": dict(resolution_counts),
    }


def diagnostics(events: List[Dict[str, Any]]) -> None:
    if not events:
        st.info("No batch to analyze yet.")
        return

    s = summarize_events(events)
    st.write("**Cutoff rate:**", f"{s['cutoff_rate']*100:.1f}%")
    st.write("**Severity buckets:**")
    st.bar_chart(s["severity_buckets"])
    st.write("**Cutoff resolutions:**")
    st.write(s["cutoff_resolutions"])
    st.write("**Top tags:**")
    st.write(dict(s["top_tags"]))
    st.write("**Top event IDs:**")
    st.write(dict(s["top_event_ids"]))


def event_card(e: Dict[str, Any]) -> None:
    st.subheader(e["title"])
    st.caption(
        f"id={e['event_id']} | severity={e['severity']} | cutoff={e['cutoff_applied']} ({e['cutoff_resolution']})"
    )
    st.write("**Tags:**", ", ".join(e.get("tags", [])))
    st.write("**Effects:**", e.get("effect_vector", {}))

    fic = e.get("fiction", {}) or {}
    if fic.get("prompt"):
        st.write(f"**Prompt:** {fic['prompt']}")
    choices = fic.get("immediate_choice", []) or []
    if choices:
        st.write("**Choices:**")
        for c in choices:
            st.write(f"- {c}")

    followups = e.get("followups", []) or []
    if followups:
        st.write("**Followups:**", followups)

    with st.expander("JSON"):
        st.code(json.dumps(e, indent=2), language="json")


def run_batch(
    *,
    scene: SceneContext,
    selection: SelectionContext,
    entries,
    seed: int,
    n: int,
    starting_engine_state,
    tick_between: bool,
    ticks_between: int,
    verbose: bool,
) -> Dict[str, Any]:
    state = starting_engine_state
    rng = TraceRNG(seed=int(seed))
    events: List[Dict[str, Any]] = []

    for idx in range(int(n)):
        if idx > 0 and tick_between and int(ticks_between) > 0:
            state = tick_state(state, ticks=int(ticks_between))

        rng.trace.clear()
        ev = generate_event(scene, state, selection, entries, rng)
        state = apply_state_delta(state, ev.state_delta)
        events.append(event_to_dict(ev))

    summary = summarize_events(events)
    return {
        "seed": int(seed),
        "n": int(n),
        "final_state": state.__dict__,
        "summary": summary,
        "events": events if verbose else None,
        "events_sample": None if verbose else events[:10],
    }


def report_to_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Scenario Suite Report: {report.get('suite')}")
    lines.append("")
    lines.append(f"- Batch N: {report.get('batch_n')}")
    lines.append(f"- Base seed: {report.get('base_seed')}")
    lines.append(f"- Presets: {', '.join(report.get('presets', []))}")
    lines.append(f"- Phases: {', '.join(report.get('phases', []))}")
    lines.append(f"- Rarity modes: {', '.join(report.get('rarity_modes', []))}")
    lines.append(f"- Include tags: `{report.get('include_tags')}`")
    lines.append(f"- Exclude tags: `{report.get('exclude_tags')}`")
    lines.append(f"- Tick between: {report.get('tick_between')} (ticks={report.get('ticks_between')})")
    lines.append(f"- Verbose events included: {report.get('verbose')}")
    lines.append("")

    for run in report.get("runs", []):
        preset = run.get("preset")
        phase = run.get("phase")
        rm = run.get("rarity_mode")
        seed = run.get("seed")
        summary = run["result"]["summary"]

        lines.append(f"## {preset} / {phase} / {rm}  (seed={seed})")
        lines.append(f"- Cutoff rate: {summary['cutoff_rate']*100:.1f}%")
        lines.append(f"- Cutoff resolutions: {summary.get('cutoff_resolutions', {})}")
        lines.append(f"- Severity buckets: {summary['severity_buckets']}")
        lines.append(
            f"- Severity avg: {summary['severity_avg']:.2f} "
            f"(min={summary['severity_min']}, max={summary['severity_max']})"
        )
        lines.append(f"- Top tags: {summary['top_tags'][:8]}")
        lines.append(f"- Top event IDs: {summary['top_event_ids'][:8]}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    st.set_page_config(page_title="SPAR Engine Harness v0.1", layout="wide")
    hs = get_hs()

    st.title("SPAR Engine Harness v0.1")
    st.caption("Debug-first harness for tuning the encounter complications engine. Not a product UI.")

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("Inputs")

        preset = st.selectbox("Scene preset", ["dungeon", "city", "wilderness", "ruins"], index=0)
        pv = scene_preset_values(preset)

        scene_id = st.text_input("Scene ID", value="harness")
        scene_phase = st.selectbox("Scene phase", ["approach", "engage", "aftermath"], index=1)
        party_band = st.selectbox("Party band", ["low", "mid", "high", "unknown"], index=3)
        rarity_mode = st.selectbox("Rarity mode", ["calm", "normal", "spiky"], index=1)

        confinement = st.slider("Confinement", 0.0, 1.0, float(pv["confinement"]), 0.05)
        connectivity = st.slider("Connectivity", 0.0, 1.0, float(pv["connectivity"]), 0.05)
        visibility = st.slider("Visibility", 0.0, 1.0, float(pv["visibility"]), 0.05)

        pack_path = st.text_input("Content pack path", value=DEFAULT_PACK)
        seed = st.number_input("Seed", min_value=0, max_value=10**9, value=42, step=1)

        # Canonical batch size lives on HarnessState (never a local variable)
        hs.batch_n = st.selectbox(
            "Batch count",
            [10, 50, 200],
            index=[10, 50, 200].index(hs.batch_n) if hs.batch_n in [10, 50, 200] else 1,
        )

        tick_mode = st.selectbox("Tick mode", ["none", "turn", "scene"], index=0)
        ticks = st.number_input("Ticks", min_value=0, max_value=100, value=0, step=1)

        st.caption("Batch runs are sequential by default (treat each generated event as a 'turn').")
        tick_between = st.checkbox("Tick between events in batch", value=True)
        ticks_between_events = st.number_input("Ticks between events", min_value=0, max_value=10, value=1, step=1)

        include_tags_text = st.text_input(
            "Include tags (CSV)",
            value="hazard,reinforcements,time_pressure,social_friction,visibility,mystic,attrition,terrain,positioning,opportunity,information",
        )
        exclude_tags_text = st.text_input("Exclude tags (CSV)", value="")

        st.divider()
        st.subheader("State")

        if st.button("Reset session state"):
            hs.reset()
            st.toast("Session reset.", icon="✅")

        st.text_area(
            "Current state (read-only)",
            value=json.dumps(hs.engine_state.__dict__, indent=2),
            height=180,
        )

        st.divider()
        st.subheader("Pack")

        if st.button("Load pack") or not hs.pack_entries:
            try:
                entries = load_entries(pack_path)
                hs.pack_entries = entries
                hs.tag_vocab = derive_tag_vocab(entries)
                st.toast(f"Loaded {len(entries)} entries", icon="✅")
            except Exception as ex:
                st.error(str(ex))

        if hs.tag_vocab:
            st.caption("Pack tags:")
            st.write(hs.tag_vocab)

    entries = hs.pack_entries
    if not entries:
        st.info("Load a content pack from the sidebar to begin.")
        return

    scene = SceneContext(
        scene_id=scene_id,
        scene_phase=scene_phase,  # type: ignore
        environment=list(pv["env"]),
        tone=["debug"],
        constraints=Constraints(confinement=confinement, connectivity=connectivity, visibility=visibility),
        party_band=party_band,  # type: ignore
        spotlight=["debug"],
    )
    selection = SelectionContext(
        enabled_packs=["core_complications_v0_1"],
        include_tags=split_csv(include_tags_text),
        exclude_tags=split_csv(exclude_tags_text),
        factions_present=[],
        rarity_mode=rarity_mode,  # type: ignore
    )

    tabs = st.tabs(["Events", "Scenarios"])

    with tabs[0]:
        colA, colB = st.columns([2, 1])

        with colA:
            st.header("Events")
            btn1, btnN = st.columns(2)
            run_one = btn1.button("Generate 1", use_container_width=True)
            run_many = btnN.button(f"Generate {hs.batch_n}", use_container_width=True)

            if run_one or run_many:
                n = 1 if run_one else int(hs.batch_n)

                if tick_mode != "none" and int(ticks) > 0:
                    hs.engine_state = tick_state(hs.engine_state, ticks=int(ticks))

                rng = TraceRNG(seed=int(seed))

                batch_events: List[Dict[str, Any]] = []
                for idx in range(n):
                    if idx > 0 and tick_between and int(ticks_between_events) > 0:
                        hs.engine_state = tick_state(hs.engine_state, ticks=int(ticks_between_events))

                    rng.trace.clear()
                    ev = generate_event(scene, hs.engine_state, selection, entries, rng)
                    hs.engine_state = apply_state_delta(hs.engine_state, ev.state_delta)

                    d = event_to_dict(ev)
                    batch_events.append(d)
                    hs.events.insert(0, d)

                hs.last_batch = batch_events

            if hs.events:
                for e in hs.events[:25]:
                    with st.container(border=True):
                        event_card(e)
            else:
                st.info("No events generated yet.")

        with colB:
            st.header("Diagnostics")
            diagnostics(hs.last_batch)

    with tabs[1]:
        st.header("Scenario Runner (Multi-run)")
        st.caption("Run predefined multi-run suites and download a debug report for tuning.")

        suite = st.selectbox(
            "Suite",
            [
                "Presets × Engage × Normal (quick)",
                "Presets × (Approach/Engage/Aftermath) × Normal",
                "Presets × Engage × (Calm/Normal/Spiky)",
            ],
            index=0,
        )

        presets = ["dungeon", "city", "wilderness", "ruins"]

        if suite == "Presets × Engage × Normal (quick)":
            phases = ["engage"]
            rarity_modes = ["normal"]
        elif suite == "Presets × (Approach/Engage/Aftermath) × Normal":
            phases = ["approach", "engage", "aftermath"]
            rarity_modes = ["normal"]
        else:
            phases = ["engage"]
            rarity_modes = ["calm", "normal", "spiky"]

        batchN = st.number_input("Batch size per run", min_value=10, max_value=500, value=int(hs.batch_n), step=10)
        base_seed = st.number_input("Base seed", min_value=0, max_value=10**9, value=1000, step=1)

        include_tags_suite = st.text_input("Include tags (CSV)", value=include_tags_text)
        exclude_tags_suite = st.text_input("Exclude tags (CSV)", value=exclude_tags_text)

        tick_between_suite = st.checkbox("Tick between events in each batch", value=True)
        ticks_between_suite = st.number_input("Ticks between events", min_value=0, max_value=10, value=1, step=1)

        verbose_report = st.checkbox("Include full event lists in report", value=False)

        run_suite = st.button("Run suite", type="primary")
        if run_suite:
            try:
                report: Dict[str, Any] = {
                    "suite": suite,
                    "batch_n": int(batchN),
                    "base_seed": int(base_seed),
                    "presets": presets,
                    "phases": phases,
                    "rarity_modes": rarity_modes,
                    "include_tags": str(include_tags_suite),
                    "exclude_tags": str(exclude_tags_suite),
                    "tick_between": bool(tick_between_suite),
                    "ticks_between": int(ticks_between_suite),
                    "verbose": bool(verbose_report),
                    "runs": [],
                }

                run_idx = 0
                for preset_name in presets:
                    pv2 = scene_preset_values(preset_name)
                    for ph in phases:
                        for rm in rarity_modes:
                            run_idx += 1
                            scene2 = SceneContext(
                                scene_id=f"suite:{suite}:{preset_name}:{ph}:{rm}",
                                scene_phase=ph,  # type: ignore
                                environment=list(pv2["env"]),
                                tone=["debug"],
                                constraints=Constraints(
                                    confinement=float(pv2["confinement"]),
                                    connectivity=float(pv2["connectivity"]),
                                    visibility=float(pv2["visibility"]),
                                ),
                                party_band="unknown",
                                spotlight=["debug"],
                            )
                            selection2 = SelectionContext(
                                enabled_packs=["core_complications_v0_1"],
                                include_tags=split_csv(include_tags_suite),
                                exclude_tags=split_csv(exclude_tags_suite),
                                factions_present=[],
                                rarity_mode=rm,  # type: ignore
                            )
                            seed2 = int(base_seed) + run_idx
                            result = run_batch(
                                scene=scene2,
                                selection=selection2,
                                entries=entries,
                                seed=seed2,
                                n=int(batchN),
                                starting_engine_state=hs.engine_state.__class__.default(),
                                tick_between=bool(tick_between_suite),
                                ticks_between=int(ticks_between_suite),
                                verbose=bool(verbose_report),
                            )
                            report["runs"].append(
                                {
                                    "preset": preset_name,
                                    "phase": ph,
                                    "rarity_mode": rm,
                                    "seed": seed2,
                                    "result": result,
                                }
                            )

                hs.last_suite_report = report
                st.success("Suite completed.")
            except Exception as ex:
                st.error(str(ex))

        report = hs.last_suite_report
        if report:
            st.subheader("Suite Summary")

            rows = []
            for run in report.get("runs", []):
                s = run["result"]["summary"]
                rows.append(
                    {
                        "preset": run["preset"],
                        "phase": run["phase"],
                        "rarity_mode": run["rarity_mode"],
                        "cutoff_rate_pct": round(s["cutoff_rate"] * 100.0, 2),
                        "cutoff_resolutions": s.get("cutoff_resolutions", {}),
                        "bucket_1_3": s["severity_buckets"]["1-3"],
                        "bucket_4_6": s["severity_buckets"]["4-6"],
                        "bucket_7_10": s["severity_buckets"]["7-10"],
                        "severity_avg": round(s["severity_avg"], 2) if s["severity_avg"] is not None else None,
                        "severity_min": s["severity_min"],
                        "severity_max": s["severity_max"],
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

            md = report_to_markdown(report)
            st.download_button(
                "Download report (Markdown)",
                data=md.encode("utf-8"),
                file_name="scenario_suite_report.md",
                mime="text/markdown",
            )
            st.download_button(
                "Download report (JSON)",
                data=json.dumps(report, indent=2).encode("utf-8"),
                file_name="scenario_suite_report.json",
                mime="application/json",
            )


if __name__ == "__main__":
    main()
