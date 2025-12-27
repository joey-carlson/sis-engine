#!/usr/bin/env python3
"""
Streamlit UI for SPAR Engine v0.1 - Rapid Prototyping Interface

This provides an interactive web interface for testing and exploring
the SPAR encounter complications engine.
"""

import streamlit as st
from pathlib import Path

from spar_engine.content import load_pack
from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG


# Load content once and cache it
@st.cache_resource
def load_content():
    return load_pack("data/core_complications.json")


def main():
    st.set_page_config(
        page_title="SPAR Engine v0.1",
        page_icon="🎲",
        layout="wide"
    )

    st.title("🎲 SPAR Engine v0.1 - Encounter Complications")
    st.markdown("*A system-agnostic procedural encounter complications engine for TTRPGs*")

    # Load content
    entries = load_content()

    # Sidebar for scene configuration
    st.sidebar.header("🎭 Scene Configuration")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        scene_phase = st.selectbox(
            "Scene Phase",
            ["approach", "engage", "aftermath"],
            help="Current phase of the encounter"
        )

        environment = st.multiselect(
            "Environment",
            ["confined", "populated", "open", "industrial", "derelict", "sea", "planar"],
            default=["confined", "populated", "open"],
            help="Where the encounter takes place (leave empty to allow all)"
        )

        tone = st.multiselect(
            "Tone",
            ["gritty", "heroic", "weird", "noir", "gonzo"],
            default=["gritty"],
            help="Atmospheric style"
        )

    with col2:
        party_band = st.selectbox(
            "Party Size",
            ["low", "mid", "high", "unknown"],
            index=1,
            help="Relative party strength"
        )

        spotlight = st.multiselect(
            "Spotlight",
            ["combat", "social", "exploration", "stealth", "mystic"],
            default=["combat"],
            help="Focus areas for the encounter"
        )

    st.sidebar.header("🏗️ Scene Constraints")
    st.sidebar.markdown("How constrained is the scene? (0.0 = open, 1.0 = trapped)")

    confinement = st.sidebar.slider("Confinement", 0.0, 1.0, 0.5, 0.1,
                                   help="Physical/tactical restriction")
    connectivity = st.sidebar.slider("Connectivity", 0.0, 1.0, 0.5, 0.1,
                                    help="Available buffers/exits")
    visibility = st.sidebar.slider("Visibility", 0.0, 1.0, 0.5, 0.1,
                                  help="How observable actions are")

    st.sidebar.header("🎯 Content Selection")

    rarity_mode = st.sidebar.selectbox(
        "Rarity Mode",
        ["calm", "normal", "spiky"],
        index=1,
        help="How volatile the complications should be"
    )

    include_tags = st.sidebar.multiselect(
        "Include Tags",
        ["hazard", "reinforcements", "time_pressure", "social_friction",
         "visibility", "mystic", "attrition", "terrain", "positioning",
         "threat", "cost", "information", "opportunity"],
        default=["hazard", "reinforcements", "time_pressure", "social_friction"],
        help="Must include at least one of these tags"
    )

    exclude_tags = st.sidebar.multiselect(
        "Exclude Tags",
        ["hazard", "reinforcements", "time_pressure", "social_friction",
         "visibility", "mystic", "attrition", "terrain", "positioning",
         "threat", "cost", "information", "opportunity"],
        help="Exclude entries with these tags"
    )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🎪 Generate Complications")

        # Generation controls
        col_gen1, col_gen2, col_gen3 = st.columns(3)

        with col_gen1:
            seed = st.number_input("RNG Seed", value=42, min_value=0,
                                 help="For reproducible results")

        with col_gen2:
            count = st.number_input("Event Count", value=1, min_value=1, max_value=10,
                                  help="How many complications to generate")

        with col_gen3:
            generate = st.button("🎲 Generate", type="primary", use_container_width=True)

    # Store state for generated events
    if 'events' not in st.session_state:
        st.session_state.events = []

    if generate:
        # Create scene context
        scene = SceneContext(
            scene_id="streamlit-demo",
            scene_phase=scene_phase,
            environment=environment,
            tone=tone,
            constraints=Constraints(confinement, connectivity, visibility),
            party_band=party_band,
            spotlight=spotlight,
        )

        # Create selection context
        selection = SelectionContext(
            enabled_packs=["core_complications_v0_1"],
            include_tags=include_tags,
            exclude_tags=exclude_tags,
            factions_present=[],
            rarity_mode=rarity_mode,
        )

        # Generate events
        rng = TraceRNG(seed=seed)
        state = EngineState.default()

        events = []
        for i in range(count):
            rng.trace.clear()
            event = generate_event(scene, state, selection, entries, rng)
            events.append(event)

        st.session_state.events = events

    # Display generated events
    if st.session_state.events:
        st.header("📋 Generated Complications")

        for i, event in enumerate(st.session_state.events):
            with st.expander(f"**{event.title}** (Severity: {event.severity})", expanded=True):
                col_a, col_b = st.columns([1, 2])

                with col_a:
                    st.metric("Severity", event.severity)
                    st.metric("Cutoff Applied", "Yes" if event.cutoff_applied else "No")
                    if event.cutoff_applied:
                        st.caption(f"Resolution: {event.cutoff_resolution}")

                with col_b:
                    if event.tags:
                        st.write("**Tags:**", ", ".join(event.tags))

                    if event.effect_vector.threat > 0:
                        st.caption(f"Threat: +{event.effect_vector.threat}")
                    if event.effect_vector.cost > 0:
                        st.caption(f"Cost: +{event.effect_vector.cost}")
                    if event.effect_vector.heat > 0:
                        st.caption(f"Heat: +{event.effect_vector.heat}")
                    if event.effect_vector.time_pressure > 0:
                        st.caption(f"Time Pressure: +{event.effect_vector.time_pressure}")

                if event.fiction.prompt:
                    st.markdown("**Fiction:**")
                    st.write(event.fiction.prompt)

                if event.fiction.immediate_choice:
                    st.markdown("**Immediate Choices:**")
                    for choice in event.fiction.immediate_choice:
                        st.write(f"• {choice}")

                if event.followups:
                    st.markdown("**Follow-ups:**")
                    for followup in event.followups:
                        st.caption(followup.get("tag", "") + ": " + followup.get("in", ""))

    with col2:
        st.header("📊 Current Scene")
        st.write(f"**Phase:** {scene_phase}")
        st.write(f"**Environment:** {', '.join(environment) if environment else 'None'}")
        st.write(f"**Tone:** {', '.join(tone) if tone else 'None'}")
        st.write(f"**Party:** {party_band}")
        st.write(f"**Spotlight:** {', '.join(spotlight) if spotlight else 'None'}")

        st.subheader("Constraints")
        st.progress(confinement, text=f"Confinement: {confinement:.1f}")
        st.progress(connectivity, text=f"Connectivity: {connectivity:.1f}")
        st.progress(visibility, text=f"Visibility: {visibility:.1f}")

        st.subheader("Selection")
        st.write(f"**Rarity:** {rarity_mode}")
        st.write(f"**Include Tags:** {', '.join(include_tags) if include_tags else 'None'}")
        st.write(f"**Exclude Tags:** {', '.join(exclude_tags) if exclude_tags else 'None'}")

    # Footer
    st.markdown("---")
    st.caption("SPAR Engine v0.1 - Built for rapid prototyping and testing")


if __name__ == "__main__":
    main()
