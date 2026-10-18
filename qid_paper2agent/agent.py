"""
Virtual Co-Author Agent for 'The Quick Initial Doublet' (Paper2Agent Framework).
Provides natural language comprehension, intent dispatching, and biophysical tool calling.
Compatible with Python 3.9+.
"""

import json
from typing import Dict, Any, Tuple
from .electrophysiology import ElectrophysiologyEngine
from .kinematics import KinematicsEngine
from .aging import AgingModel
from .knowledge_base import (
    PAPER_METADATA,
    NEURAL_SUBSYSTEMS,
    MOTOR_CONTROL_HIERARCHY,
    search_knowledge_base
)

e_engine = ElectrophysiologyEngine()
k_engine = KinematicsEngine()
a_model = AgingModel(k_engine)


def process_agent_message(user_input: str) -> Dict[str, Any]:
    """
    Processes natural language inputs or commands and executes the corresponding
    biophysical models or knowledge base queries.
    """
    raw = user_input.strip()
    if not raw:
        return {
            "type": "empty",
            "reply": "Please enter a question or command (e.g. 'jump 85', 'epsp 150', 'explain octopus cells')."
        }

    parts = raw.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # 1. Direct Command: jump <freq>
    if cmd == "jump":
        if not args:
            return {
                "type": "error",
                "reply": "Usage: `jump <frequency_hz>` (e.g. `jump 100`, `jump 85`, `jump 50`)."
            }
        try:
            f = float(args[0])
            res = k_engine.simulate_jump(f)
            d = res.to_dict()
            if not res.stuck:
                reply = (
                    f"### 🦘 Ballistic Jump Simulation: {f:.1f} Hz QID\n\n"
                    f"- **Initial Jerk (Hill Ca2+ cooperativity):** `{d['jerk_m_s3']} m/s³`\n"
                    f"- **Ignition Phase Duration (t3):** `{d['ignition_duration_ms']} ms`\n"
                    f"- **Peak Sustained Acceleration (a_max):** `{d['peak_sustained_accel_m_s2']} m/s²`\n"
                    f"- **Takeoff Time (t_exit):** `{d['takeoff_time_ms']} ms`\n"
                    f"- **Exit Velocity (v_exit):** `{d['exit_velocity_m_s']} m/s`\n"
                    f"- **Net Jump Clearance (h):** `{d['jump_height_m']} m` (**{d['capacity_pct']}%** of baseline)\n\n"
                    f"> **Physiological Context:** {d['notes']}"
                )
            else:
                reply = (
                    f"### 🦘 Ballistic Jump Simulation: {f:.1f} Hz\n\n"
                    f"**STATUS: STUCK AT 0.000 m (0% capacity)**\n\n"
                    f"> **Physiological Context:** Without an initial doublet to trigger the Ignition Phase, "
                    f"tetanic tension merely equalizes with body weight. Inertia is never broken."
                )
            return {"type": "jump", "data": d, "reply": reply}
        except ValueError:
            return {"type": "error", "reply": f"Invalid frequency value: `{args[0]}`. Please supply a numeric frequency."}

    # 2. Direct Command: epsp <freq> [tau]
    if cmd == "epsp":
        if not args:
            return {
                "type": "error",
                "reply": "Usage: `epsp <frequency_hz> [tau_ms]` (e.g. `epsp 200`, `epsp 150`, `epsp 100`)."
            }
        try:
            f = float(args[0])
            tau = float(args[1]) if len(args) > 1 else 4.0
            engine = ElectrophysiologyEngine(tau_ms=tau) if tau != 4.0 else e_engine
            res = engine.calculate_summation(f)
            d = res.to_dict()
            status_badge = "✅ PRIMED TO THRESHOLD" if d['primes_threshold'] else "⚠️ SUBTHRESHOLD DEFICIT"
            reply = (
                f"### ⚡ UMN Temporal Summation & Depolarization: {f:.1f} Hz (tau = {tau:.1f} ms)\n\n"
                f"**Status:** {status_badge}\n\n"
                f"- **Inter-Spike Interval (dt):** `{d['dt_ms']} ms`\n"
                f"- **Decay Ratio (dt / tau):** `{d['decay_ratio']}`\n"
                f"- **Synaptic Retention (r):** `{d['retention_pct']}%`\n"
                f"- **Summation Multiplier (M):** `{d['summation_multiplier_m']}`\n"
                f"- **Summation Gain (G):** `{d['summation_gain_g']}`\n"
                f"- **Depolarization (delta_V):** `+{d['depolarization_mv']} mV`\n"
                f"- **Primed Potential (Vm):** `{d['membrane_potential_vm']} mV` (Rest: -65 mV -> Target: -55 mV)\n"
                f"- **Summation Gain Collapse:** `{d['gain_collapse_pct']}%`\n\n"
                f"> **Physiological Impact:** {d['physiological_impact']}"
            )
            return {"type": "epsp", "data": d, "reply": reply}
        except ValueError:
            return {"type": "error", "reply": "Invalid numeric arguments for EPSP simulation."}

    # 3. Direct Command: age <years> [athlete_0_or_1]
    if cmd == "age":
        if not args:
            return {
                "type": "error",
                "reply": "Usage: `age <years> [athlete_0_or_1]` (e.g. `age 55`, `age 70 1`, `age 75 0`)."
            }
        try:
            age = int(args[0])
            is_ath = bool(int(args[1])) if len(args) > 1 else True
            prof = a_model.evaluate_profile(age, is_ath)
            d = prof.to_dict()
            reply = (
                f"### ⏳ Lifespan Dynapenia Profile: Age {d['age_years']} ({d['athletic_tier']})\n\n"
                f"- **Estimated LMN QID Firing Rate:** `{d['qid_frequency_hz']} Hz` (**-{d['qid_reduction_pct']}%** rate loss)\n"
                f"- **Expected Vertical Jump Height:** `{d['jump_height_m']} m` (**{d['performance_retention_pct']}%** capacity remaining)\n"
                f"- **Net Ballistic Power Loss:** `{d['performance_drop_pct']}%`\n"
                f"- **Takeoff Velocity:** `{d['takeoff_velocity_m_s']} m/s`\n"
                f"- **Masters Track Correlation:** {d['masters_track_correlation']}\n\n"
                f"> **Clinical Status:** {d['clinical_risk_status']}"
            )
            return {"type": "age", "data": d, "reply": reply}
        except ValueError:
            return {"type": "error", "reply": "Invalid age format. Please supply an integer age."}

    # 4. Direct Command: spikes <freq>
    if cmd == "spikes":
        if not args:
            return {"type": "error", "reply": "Usage: `spikes <frequency_hz>` (e.g. `spikes 100`, `spikes 80`)."}
        try:
            f = float(args[0])
            res = k_engine.simulate_jump(f)
            table_lines = [
                f"### ⏱️ Millisecond Spike Schedule: {f:.1f} Hz QID / 25 Hz Train\n",
                "| Spike | Time (ms) | Jerk (m/s³) | Accel (m/s²) | Vel (m/s) | Pos (m) |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |"
            ]
            for s in res.spikes:
                table_lines.append(f"| {s.label} | {s.time_ms:.1f} | {s.jerk_m_s3:.1f} | {s.accel_m_s2:.2f} | {s.vel_m_s:.2f} | {s.pos_m:.3f} |")
            table_lines.append(f"\n**Takeoff Result:** `{res.jump_height_m:.2f} m` clearance ({res.capacity_pct:.1f}% capacity)")
            return {"type": "spikes", "reply": "\n".join(table_lines)}
        except ValueError:
            return {"type": "error", "reply": "Invalid frequency value."}

    # 5. Direct Command: subsystems
    if cmd in ["subsystems", "subsystem"]:
        lines = ["### 🧠 The Four Neural Subsystems of the Quick Initial Doublet\n"]
        for key, s in NEURAL_SUBSYSTEMS.items():
            lines.append(f"#### 🔹 {s['name']}")
            lines.append(f"- **Doublet Frequency:** `{s['doublet_frequency']}` | **Trailing:** `{s['trailing_rate']}`")
            lines.append(f"- **Phase Transition:** *{s['phase_transition']}*")
            lines.append(f"- **Mechanism:** {s['mechanism']}")
            lines.append(f"- **Degradation:** {s['degradation_pathology']}")
            lines.append(f"- **Key Literature:** {', '.join(s['key_citations'])}\n")
        return {"type": "subsystems", "reply": "\n".join(lines)}

    # 6. Direct Command: hierarchy / pathway
    if cmd in ["hierarchy", "pathway", "motor"]:
        lines = ["### 🏛️ Four-Part Motor Control Pathway (Appendix C)\n"]
        for lvl, info in MOTOR_CONTROL_HIERARCHY.items():
            lines.append(f"**{lvl}: {info['name']}**")
            lines.append(f"- *Role:* {info['role']}")
            lines.append(f"- *Structures:* {info['structures']}\n")
        return {"type": "hierarchy", "reply": "\n".join(lines)}

    # 7. Direct Command: benchmarks
    if cmd in ["benchmarks", "benchmark", "matrix"]:
        lines = [
            "### 📊 Replicated Manuscript Benchmarks (Appendix D)\n",
            "| Regime | QID Freq | Jerk (m/s³) | Accel (m/s²) | Takeoff (ms) | Vel (m/s) | Jump Height |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        regimes = [
            ("100% Baseline", 100.0),
            ("Moderate (10% drop)", 90.0),
            ("Intermediate (20% drop)", 80.0),
            ("Non-Linear (25% drop)", 75.0),
            ("Systemic Crash (50%)", 50.0),
            ("Absolute Baseline (Tonic)", 25.0)
        ]
        for label, f in regimes:
            sim = k_engine.simulate_jump(f)
            t_str = f"{sim.takeoff_time_ms:.1f}" if not sim.stuck else "Stuck"
            v_str = f"{sim.exit_velocity_m_s:.2f}" if not sim.stuck else "0.00"
            h_str = f"{sim.jump_height_m:.2f} m ({sim.capacity_pct:.0f}%)" if not sim.stuck else "0.00 m (0%)"
            lines.append(f"| **{label}** | {f:.1f} Hz | {sim.jerk_m_s3:.1f} | {sim.a_max_m_s2:.2f} | {t_str} | {v_str} | **{h_str}** |")
        return {"type": "benchmarks", "reply": "\n".join(lines)}

    # 8. Natural Language & Semantic Intent Parsing
    q_lower = raw.lower()

    # Check for jump question with embedded number (e.g. "what happens at 82 hz jump?")
    for token in parts:
        clean_num = token.rstrip("hz").rstrip("Hz").rstrip(".").rstrip(",")
        try:
            val = float(clean_num)
            if 20 <= val <= 350 and any(w in q_lower for w in ["jump", "jumped", "jumping", "locomotion", "tetanus"]):
                return process_agent_message(f"jump {val}")
            elif 25 <= val <= 350 and any(w in q_lower for w in ["epsp", "umn", "m1", "depolarization", "summation"]):
                return process_agent_message(f"epsp {val}")
            elif 20 <= val <= 95 and any(w in q_lower for w in ["age", "year", "old", "dynapenia", "aging", "elderly"]):
                return process_agent_message(f"age {int(val)}")
        except ValueError:
            pass

    # Knowledge search
    kb_res = search_knowledge_base(raw)
    if "auditory_octopus" in kb_res or any(w in q_lower for w in ["octopus", "auditory", "ear", "sound", "cochlear", "noise"]):
        sub = NEURAL_SUBSYSTEMS["auditory_octopus"]
        reply = (
            f"### 🦻 Auditory Octopus Cells: Temporal Coincidence Detection\n\n"
            f"- **Doublet Firing Rate:** `{sub['doublet_frequency']}`\n"
            f"- **Phase Transition:** *{sub['phase_transition']}*\n"
            f"- **Structures:** {sub['anatomical_structures']}\n\n"
            f"**Biophysical Function:**\n{sub['mechanism']}\n\n"
            f"**Pathology & Aging:**\n{sub['degradation_pathology']}\n\n"
            f"**Citations:** *{', '.join(sub['key_citations'])}*"
        )
        return {"type": "knowledge", "subsystem": "auditory_octopus", "reply": reply}

    if "cortical_pv_interneurons" in kb_res or any(w in q_lower for w in ["pv+", "parvalbumin", "gamma", "escapement", "interneuron", "40 hz", "clock"]):
        sub = NEURAL_SUBSYSTEMS["cortical_pv_interneurons"]
        reply = (
            f"### ⏱️ Cortical PV+ Interneurons: 40 Hz Gamma Escapement\n\n"
            f"- **Doublet Firing Rate:** `{sub['doublet_frequency']}` | **Trailing Rhythm:** `{sub['trailing_rate']}`\n"
            f"- **Phase Transition:** *{sub['phase_transition']}*\n"
            f"- **Structures:** {sub['anatomical_structures']}\n\n"
            f"**Pendulum Escapement Analogy:**\n{sub['mechanism']}\n\n"
            f"**Clinical Significance:**\n{sub['degradation_pathology']}\n\n"
            f"**Citations:** *{', '.join(sub['key_citations'])}*"
        )
        return {"type": "knowledge", "subsystem": "cortical_pv_interneurons", "reply": reply}

    if any(w in q_lower for w in ["dynapenia", "sarcopenia", "muscle power", "frailty", "fall"]):
        reply = (
            "### 🩺 Dynapenia vs. Sarcopenia in the QID Paradigm\n\n"
            "- **Dynapenia** is defined clinically as the loss of muscle **power** and force generation velocity.\n"
            "- **Sarcopenia** is the macroscopic loss of muscle **mass**.\n\n"
            "**Key Insight from the Paper:**\n"
            "Dynapenia frequently *precedes* macroscopic sarcopenia. When Fast-Fatigable (FF) alpha motor neurons "
            "suffer age-related underclocking (e.g. their QID drops from 100 Hz to 80 Hz), the motor unit loses its safety margin "
            "for immediate tetanic force. Because initial Jerk scales with a Hill cooperativity exponent n ≈ 2.22, "
            "a modest 20% neural rate decay causes an immediate **47% loss in explosive jump clearance**, even while muscle mass remains intact."
        )
        return {"type": "knowledge", "reply": reply}

    if any(w in q_lower for w in ["mccormick", "rs", "ib", "fs"]):
        from .knowledge_base import MCCORMICK_CLASSIFICATION
        lines = ["### 🔬 McCormick Neuronal Electrophysiological Classifications (Appendix A)\n"]
        for k, v in MCCORMICK_CLASSIFICATION.items():
            lines.append(f"- **{k}:** {v}")
        lines.append(
            "\n*Significance:* The paper emphasizes that while McCormick established these three phenotypes (RS, IB, FS), "
            "neurons executing a transient Quick Initial Doublet (like FF motor neurons or octopus cells) represent a specialized "
            "kinetic adaptation designed for immediate phase transitions."
        )
        return {"type": "knowledge", "reply": "\n".join(lines)}

    # Default overview
    reply = (
        f"### 📖 Quick Initial Doublet Virtual Co-Author\n\n"
        f"I can discuss theoretical mechanisms and run live biophysical simulations from the manuscript: "
        f"*{PAPER_METADATA['title']}*.\n\n"
        f"**Available Actions:**\n"
        f"- `jump <freq>` — Run ballistic jump kinematic ODE integration (e.g. `jump 85`)\n"
        f"- `epsp <freq> [tau]` — Compute UMN synaptic summation & Vm priming (e.g. `epsp 150`)\n"
        f"- `age <years> [ath]` — Project lifespan dynapenia decay (e.g. `age 70 1`)\n"
        f"- `spikes <freq>` — View millisecond spike train table (e.g. `spikes 90`)\n"
        f"- `subsystems` — Compare LMN, UMN, Octopus cells, and PV+ interneurons\n"
        f"- `benchmarks` — View replicated Appendix D benchmark matrix\n"
        f"- Or ask any question about the biophysics, Hill equation cooperativity, or neural phase transitions!"
    )
    return {"type": "general", "reply": reply}
