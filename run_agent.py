#!/usr/bin/env python3
"""
Interactive Virtual Co-Author CLI for 'The Quick Initial Doublet' (Paper2Agent Framework).
Allows readers, reviewers, and researchers to interactively converse with the paper,
query theoretical mechanisms, and run on-the-fly biophysical simulations.
"""

import sys
import json
from qid_paper2agent.electrophysiology import ElectrophysiologyEngine
from qid_paper2agent.kinematics import KinematicsEngine
from qid_paper2agent.aging import AgingModel
from qid_paper2agent.knowledge_base import (
    PAPER_METADATA,
    NEURAL_SUBSYSTEMS,
    MOTOR_CONTROL_HIERARCHY,
    search_knowledge_base
)

e_engine = ElectrophysiologyEngine()
k_engine = KinematicsEngine()
a_model = AgingModel(k_engine)


def print_banner():
    print("=" * 80)
    print(" PAPER2AGENT: VIRTUAL CO-AUTHOR")
    print(f" Paper: '{PAPER_METADATA['title']}'")
    print("=" * 80)
    print("Commands:")
    print("  [1] jump <freq_hz>     - Simulate ballistic vertical jump kinematics")
    print("  [2] epsp <freq_hz>     - Compute UMN temporal summation & LMN Vm priming")
    print("  [3] age <years> [ath]  - Predict aging trajectory & dynapenia risk (ath: 1/0)")
    print("  [4] spikes <freq_hz>   - Print full spike-by-spike millisecond schedule")
    print("  [5] subsystems         - Display comparison of all 4 neural subsystems")
    print("  [6] hierarchy          - Show 4-part top-down motor control pathway")
    print("  [7] query <text>       - Search paper knowledge base for concepts/citations")
    print("  [8] benchmarks         - Print full table replicating Appendix D results")
    print("  help                   - Show this menu")
    print("  quit / exit            - Exit the co-author session")
    print("=" * 80)


def cmd_jump(args):
    if not args:
        print("Usage: jump <frequency_hz> (e.g. jump 100, jump 90, jump 75)")
        return
    try:
        f = float(args[0])
        res = k_engine.simulate_jump(f)
        print(f"\n--- Jump Simulation for QID Frequency: {f} Hz ---")
        print(f"Initial Jerk (Hill cooperativity):   {res.jerk_m_s3:.1f} m/s^3")
        print(f"Ignition Duration (t3):              {res.t3_ignition_ms:.1f} ms")
        print(f"Peak Sustained Acceleration (a_max): {res.a_max_m_s2:.2f} m/s^2")
        if res.stuck:
            print("Status:                              STUCK AT 0.000 m (Inertia never broken)")
        else:
            print(f"Takeoff Time (t_exit):               {res.takeoff_time_ms:.1f} ms")
            print(f"Exit Takeoff Velocity (v_exit):      {res.exit_velocity_m_s:.2f} m/s")
            print(f"Net Vertical Jump Height (h):        {res.jump_height_m:.2f} m ({res.capacity_pct:.1f}% of 1.00m baseline)")
        print(f"Physiological Note:                  {res.notes}\n")
    except ValueError:
        print("Please enter a valid numeric frequency in Hz.")


def cmd_epsp(args):
    if not args:
        print("Usage: epsp <frequency_hz> [tau_ms] (e.g. epsp 200, epsp 150, epsp 100)")
        return
    try:
        f = float(args[0])
        tau = float(args[1]) if len(args) > 1 else 4.0
        custom_engine = ElectrophysiologyEngine(tau_ms=tau) if tau != 4.0 else e_engine
        res = custom_engine.calculate_summation(f)
        print(f"\n--- UMN Temporal Summation & Depolarization for {f} Hz (tau={tau} ms) ---")
        print(f"Inter-Spike Interval (dt):           {res.dt_ms:.2f} ms")
        print(f"Decay Ratio (dt / tau):              {res.decay_ratio:.3f}")
        print(f"EPSP Retention Fraction (r):         {res.retention_r * 100.0:.2f}%")
        print(f"Summation Multiplier (M):            {res.summation_multiplier_m:.4f}")
        print(f"Accrued Summation Gain (G):          {res.summation_gain_g:.4f}")
        print(f"Membrane Depolarization (delta_V):   +{res.depolarization_mv:.2f} mV")
        print(f"Primed Membrane Potential (Vm):      {res.membrane_potential_vm:.2f} mV (Rest: -65 mV -> Threshold: -55 mV)")
        print(f"Summation Gain Collapse:             {res.gain_collapse_pct:.1f}%")
        print(f"Threshold Primed?:                   {'YES (Single M1 spike fires LMN)' if res.primes_threshold else 'NO (Requires extra spikes; latencies double)'}")
        print(f"Physiological Impact:                {res.physiological_impact}\n")
    except ValueError:
        print("Please enter valid numeric parameters.")


def cmd_age(args):
    if not args:
        print("Usage: age <years> [athlete_0_or_1] (e.g. age 55, age 70 1, age 75 0)")
        return
    try:
        age = int(args[0])
        is_ath = bool(int(args[1])) if len(args) > 1 else True
        prof = a_model.evaluate_profile(age, is_ath)
        print(f"\n--- Aging & Dynapenia Profile: Age {age} ({prof.athletic_tier}) ---")
        print(f"Estimated LMN QID Firing Rate:       {prof.qid_frequency_hz:.1f} Hz ({prof.qid_reduction_pct:.1f}% decline)")
        print(f"Expected Net Jump Height:            {prof.simulation.jump_height_m:.2f} m ({prof.simulation.capacity_pct:.1f}% capacity remaining)")
        print(f"Loss of Ballistic Power:             {100.0 - prof.simulation.capacity_pct:.1f}%")
        print(f"Takeoff Velocity:                    {prof.simulation.exit_velocity_m_s:.2f} m/s")
        print(f"Masters Track Athletic Benchmark:    {prof.masters_track_correlation}")
        print(f"Clinical Status:                     {prof.clinical_risk_status}\n")
    except ValueError:
        print("Please enter valid integers for age and athlete flag.")


def cmd_spikes(args):
    if not args:
        print("Usage: spikes <frequency_hz> (e.g. spikes 100, spikes 90, spikes 80)")
        return
    try:
        f = float(args[0])
        res = k_engine.simulate_jump(f)
        print(f"\n--- Millisecond Spike Progression Schedule ({f} Hz QID / 25 Hz Train) ---")
        print(f"{'Spike':<8} {'Time (ms)':<12} {'Jerk (m/s^3)':<14} {'Accel (m/s^2)':<14} {'Vel (m/s)':<12} {'Pos (m)':<10}")
        print("-" * 72)
        for s in res.spikes:
            print(f"{s.label:<8} {s.time_ms:<12.1f} {s.jerk_m_s3:<14.1f} {s.accel_m_s2:<14.2f} {s.vel_m_s:<12.2f} {s.pos_m:<10.3f}")
        print(f"\nResult: Jump Height = {res.jump_height_m:.2f} m ({res.capacity_pct:.1f}% capacity)\n")
    except ValueError:
        print("Please enter a valid numeric frequency in Hz.")


def cmd_subsystems():
    print("\n" + "=" * 80)
    print(" THE FOUR NEURAL SUBSYSTEMS OF THE QUICK INITIAL DOUBLET")
    print("=" * 80)
    for key, s in NEURAL_SUBSYSTEMS.items():
        print(f"\n▶ [{s['name'].upper()}]")
        print(f"  • Doublet Frequency:    {s['doublet_frequency']}")
        print(f"  • Trailing Rate:        {s['trailing_rate']}")
        print(f"  • Phase Transition:     {s['phase_transition']}")
        print(f"  • Structures:           {s['anatomical_structures']}")
        print(f"  • Functional Mechanism: {s['mechanism']}")
        print(f"  • Degradation Effect:   {s['degradation_pathology']}")
        print(f"  • Key Citations:        {', '.join(s['key_citations'])}")
    print()


def cmd_hierarchy():
    print("\n" + "=" * 80)
    print(" FOUR-PART MOTOR CONTROL PATHWAY (Appendix C)")
    print("=" * 80)
    for lvl, info in MOTOR_CONTROL_HIERARCHY.items():
        print(f"\n▶ {lvl}: {info['name']}")
        print(f"  • Role:       {info['role']}")
        print(f"  • Structures: {info['structures']}")
    print()


def cmd_query(args):
    if not args:
        print("Usage: query <search phrase> (e.g. query gamma, query octopus, query dynapenia)")
        return
    query_str = " ".join(args)
    results = search_knowledge_base(query_str)
    print(f"\n--- Search Results for '{query_str}' ---")
    print(json.dumps(results, indent=2))
    print()


def cmd_benchmarks():
    print("\n" + "=" * 80)
    print(" REPLICATED APPENDIX D BENCHMARKS (Full Matrix)")
    print("=" * 80)
    print(f"{'Condition':<22} {'Freq (Hz)':<10} {'Jerk (m/s^3)':<14} {'Accel (m/s^2)':<14} {'Takeoff (ms)':<14} {'Vel (m/s)':<12} {'Jump (m)':<10}")
    print("-" * 96)
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
        t_exit_str = f"{sim.takeoff_time_ms:.1f}" if not sim.stuck else "Stuck"
        vel_str = f"{sim.exit_velocity_m_s:.2f}" if not sim.stuck else "0.00"
        h_str = f"{sim.jump_height_m:.2f} ({sim.capacity_pct:.0f}%)" if not sim.stuck else "0.00 (0%)"
        print(f"{label:<22} {f:<10.1f} {sim.jerk_m_s3:<14.1f} {sim.a_max_m_s2:<14.2f} {t_exit_str:<14} {vel_str:<12} {h_str:<10}")
    print()


def run_cli():
    print_banner()
    while True:
        try:
            line = input("qid-agent> ").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ["quit", "exit", "q"]:
                print("Session closed. Happy researching!")
                break
            elif cmd == "help":
                print_banner()
            elif cmd == "jump":
                cmd_jump(args)
            elif cmd == "epsp":
                cmd_epsp(args)
            elif cmd == "age":
                cmd_age(args)
            elif cmd == "spikes":
                cmd_spikes(args)
            elif cmd == "subsystems":
                cmd_subsystems()
            elif cmd == "hierarchy":
                cmd_hierarchy()
            elif cmd == "query":
                cmd_query(args)
            elif cmd == "benchmarks":
                cmd_benchmarks()
            else:
                # Treat as a freeform query to the paper
                cmd_query([line])

        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break


def main():
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli()
    else:
        # Default: Launch In-Browser Agent and automatically open web browser
        import web_dashboard
        port = 8080
        for arg in sys.argv[1:]:
            if arg.isdigit():
                port = int(arg)
                break
        web_dashboard.run(port=port, auto_open=True)


if __name__ == "__main__":
    main()

