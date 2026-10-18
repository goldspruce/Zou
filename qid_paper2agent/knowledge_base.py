"""
Domain knowledge base and semantic index for 'The Quick Initial Doublet: A Common Mechanism Across Neural Subsystems'.
Grounds the Paper2Agent in the paper's theory, subsystems, and experimental literature.
"""

from typing import Dict, Any, List, Optional

PAPER_METADATA = {
    "title": "The Quick Initial Doublet: A Common Mechanism Across Neural Subsystems",
    "version": "Review Paper Draft (October 2026 Revision)",
    "core_concept": "The Quick Initial Doublet (QID): Two fast action potentials (often >100-300 Hz) followed by a slower spike train or quiescence, triggering an abrupt physiological phase transition specific to that neural subsystem."
}

NEURAL_SUBSYSTEMS: Dict[str, Dict[str, Any]] = {
    "lmn_muscle": {
        "name": "Lower Motor Neurons (LMN) & Skeletal Muscle",
        "doublet_frequency": "100 Hz (10 ms ISI)",
        "trailing_rate": "25 Hz (40 ms ISI)",
        "phase_transition": "From relaxed or eccentric state to instantaneous concentric muscle tetanus.",
        "anatomical_structures": "Ventral horn alpha motor neurons, Neuromuscular Junction (NMJ), Fast-Fatigable (FF) Type IIx muscle fibers.",
        "mechanism": (
            "Large FF motor neurons fire a 100 Hz QID to exploit non-linear sarcoplasmic Ca2+ cooperativity (Hill exponent ~2.22), "
            "rapidly driving initial Jerk (445 m/s^3) and tautening muscle fibers within 50 ms. The firing rate then dials back to 25 Hz "
            "to prevent metabolic exhaustion and ionic exhaust while sustaining tetanic force to complete ballistic acceleration."
        ),
        "degradation_pathology": (
            "Age-related underclocking of the QID (e.g. from 100 Hz down to 90, 80, or 75 Hz) drastically reduces initial jerk and takeoff velocity, "
            "yielding dynapenia (loss of muscle power) before macroscopic sarcopenia (loss of muscle mass)."
        ),
        "key_citations": ["Christie & Kamen (2010)", "Burke et al. (1973)", "Klass et al. (2008)"]
    },
    "umn_corticospinal": {
        "name": "Upper Motor Neurons (UMN) / Corticospinal Engine-Start",
        "doublet_frequency": "200 Hz (5 ms ISI)",
        "trailing_rate": "Single spikes (singlets)",
        "phase_transition": "Metaphorical 'engine start': waking up quiescent LMNs by priming membrane potential to threshold.",
        "anatomical_structures": "Primary Motor Cortex (M1), Layer Vb Betz cells / Fast Pyramidal Tract Neurons (PTNs), Corticospinal Tract.",
        "mechanism": (
            "A 200 Hz QID burst travels down the corticospinal tract. Due to rapid AMPA EPSP decay (tau = 4.0 ms), isolated spikes decay too fast "
            "to cause sustained depolarization. The 200 Hz doublet yields a temporal summation multiplier M ≈ 1.40, subthreshold depolarizing the LMN "
            "membrane from resting (-65 mV) to action potential threshold (-55 mV). Once primed at -55 mV, subsequent single M1 spikes reliably fire the LMN."
        ),
        "degradation_pathology": (
            "When UMN QID frequency decays to 150 Hz or 100 Hz, inter-spike EPSP dissipation exceeds 80-90%. The membrane remains stranded at -56 to -57 mV. "
            "Extra central spikes must be recruited, doubling initiation latency and causing postural catch-steps to fail during balance perturbations."
        ),
        "key_citations": ["Evarts (1968)", "McCormick et al. (1985)"]
    },
    "auditory_octopus": {
        "name": "Ventral Cochlear Nucleus Octopus Cells",
        "doublet_frequency": "300 Hz (~3.3 ms ISI)",
        "trailing_rate": "Quiescence / transient pause",
        "phase_transition": "Marking the occurrence of a salient sound onset contrasted against background noise.",
        "anatomical_structures": "Ventral Cochlear Nucleus (VCN), Auditory nerve fibers, Hair cells, Superior Olivary Complex.",
        "mechanism": (
            "Octopus cells receive convergent inputs from auditory hair cells and fire a rapid 300 Hz QID upon sound activation. "
            "Acting like a 'knock-knock' double tap on a door, the doublet distinctly demarcates salient acoustic transients from stochastic neuronal noise, "
            "enabling sub-millisecond temporal resolution essential for Interaural Time Difference (ITD) horizontal sound localization."
        ),
        "degradation_pathology": (
            "Loss of high-frequency precision impairs spatial hearing in noisy environments (the 'cocktail party problem') and acoustic orientation."
        ),
        "key_citations": ["Golding et al. (1995)", "Oertel (1999)"]
    },
    "cortical_pv_interneurons": {
        "name": "Cortical Parvalbumin-Positive (PV+) Interneurons",
        "doublet_frequency": "300 Hz (~3.3 ms ISI)",
        "trailing_rate": "Silent pause until the next 40 Hz cycle (~25 ms)",
        "phase_transition": "From active cognitive processing to dead silence (pendulum escapement).",
        "anatomical_structures": "Cortex, GABAergic PV+ Fast-Spiking basket cells, Pyramidal cell somata and axon initial segments.",
        "mechanism": (
            "PV+ interneurons fire inhibitory QIDs at ~300 Hz, followed by silence for the remainder of the 25 ms cycle. "
            "This acts analogous to a clockwork pendulum escapement: the powerful inhibitory double burst creates a synchronized inhibitory clamp, "
            "pacing the excitatory pyramidal neurons into 40 Hz gamma oscillations critical for cognitive binding and active working memory."
        ),
        "degradation_pathology": (
            "Impairment of PV+ fast-spiking kinetics disrupts 40 Hz gamma synchrony, a hallmark observed in Alzheimer's disease, schizophrenia, and cognitive decline."
        ),
        "key_citations": ["Bartos et al. (2007)", "Cardin et al. (2009)", "Sohal et al. (2009)", "Buzsáki & Wang (2012)"]
    }
}

MOTOR_CONTROL_HIERARCHY = {
    "Level 1": {
        "name": "Ideation & Strategy (High-Level Intent)",
        "structures": "Prefrontal Cortex, Posterior Parietal Cortex, Association Cortices",
        "role": "'What to do.' Converts sensory context and goals into high-level motor intentions."
    },
    "Level 2": {
        "name": "Tactical Planning & Subcortical Tuning (Motor Programming)",
        "structures": "Premotor Area (PMA), Supplementary Motor Area (SMA), Basal Ganglia, Cerebellum",
        "role": "'How to do it.' Basal ganglia gates execution; Cerebellum computes real-time predictive error corrections and timing."
    },
    "Level 3": {
        "name": "Executive Command / Upper Motor Neurons (UMN System)",
        "structures": "Primary Motor Cortex (M1), Layer Vb Betz cells, Corticospinal Tract",
        "role": "'Send the firing command.' Fires 200 Hz QID down corticospinal tract to prime spinal motor pools."
    },
    "Level 4": {
        "name": "The Final Common Pathway / Lower Motor Neurons (LMN System)",
        "structures": "Alpha Motor Neurons (spinal cord ventral horn), NMJ, Skeletal Muscle",
        "role": "'Contract the muscle.' Fires 100 Hz QID to trigger muscle tetanus and convert electrical drive into ballistic mechanical force."
    }
}

MCCORMICK_CLASSIFICATION = {
    "Regular Spiking (RS)": "Most common phenotype; shows strong spike frequency adaptation (firing slows down over time).",
    "Intrinsically Bursting (IB)": "Responds with an initial high-frequency cluster/burst, then settles into a regular, slower rhythm.",
    "Fast-Spiking (FS)": "Maintains sustained high discharge rates (>30 Hz, often >100 Hz) with very brief action potentials and minimal adaptation."
}

BURKE_MOTOR_UNITS = {
    "Slow (S)": "Small alpha motor neurons, innervate Type I slow-twitch fibers. Low firing frequency (~25 Hz), fatigue-resistant, postural control. Do NOT express QID.",
    "Fast-Fatigue Resistant (FR)": "Intermediate motor neurons, innervate Type IIa fibers. Moderate force, moderate mitochondrial density. May express a moderated initial doublet.",
    "Fast-Fatigable (FF)": "Largest alpha motor neurons, innervate massive Type IIx fast-twitch fibers. High metabolic demand. Obligate expressors of the 100 Hz QID for explosive power."
}


def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    Retrieves matching conceptual content, citations, and physiological mechanisms from the manuscript.
    """
    q = query.lower()
    matches = {}

    for key, sub in NEURAL_SUBSYSTEMS.items():
        if any(term in q for term in [key, sub["name"].lower(), "subsystem", "auditory", "cortex", "motor", "pv+", "interneuron", "octopus"]):
            matches[key] = sub

    if "level" in q or "pathway" in q or "hierarchy" in q or "control" in q:
        matches["motor_pathway"] = MOTOR_CONTROL_HIERARCHY

    if "mccormick" in q or "rs" in q or "ib" in q or "fs" in q or "classification" in q:
        matches["mccormick"] = MCCORMICK_CLASSIFICATION

    if "burke" in q or "motor unit" in q or "fiber" in q or "ff" in q or "fr" in q or "type i" in q:
        matches["burke_units"] = BURKE_MOTOR_UNITS

    if not matches:
        # Default full overview
        matches = {
            "overview": PAPER_METADATA,
            "subsystems": list(NEURAL_SUBSYSTEMS.keys()),
            "hierarchy": list(MOTOR_CONTROL_HIERARCHY.keys())
        }

    return matches
