"""
Aging, Dynapenia, and Locomotive Frailty modeling.
Synthesizes clinical observations from Klass et al. (2008) and Masters Track benchmarks
from Section 3 of 'The Quick Initial Doublet' (pp. 3-5).
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from .kinematics import KinematicsEngine, JumpSimulationResult


@dataclass
class AgingProfile:
    age_years: int
    athletic_tier: str
    qid_frequency_hz: float
    qid_reduction_pct: float
    simulation: JumpSimulationResult
    masters_track_correlation: str
    clinical_risk_status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "age_years": self.age_years,
            "athletic_tier": self.athletic_tier,
            "qid_frequency_hz": round(self.qid_frequency_hz, 1),
            "qid_reduction_pct": round(self.qid_reduction_pct, 1),
            "jump_height_m": round(self.simulation.jump_height_m, 2),
            "performance_retention_pct": round(self.simulation.capacity_pct, 1),
            "performance_drop_pct": round(100.0 - self.simulation.capacity_pct, 1),
            "takeoff_velocity_m_s": round(self.simulation.exit_velocity_m_s, 2),
            "masters_track_correlation": self.masters_track_correlation,
            "clinical_risk_status": self.clinical_risk_status
        }


class AgingModel:
    """
    Maps biological aging trajectories to QID frequency decay and locomotive frailty.
    """
    def __init__(self, kinematics_engine: KinematicsEngine = None):
        self.kinematics = kinematics_engine or KinematicsEngine()

    def estimate_qid_frequency(self, age: int, is_active_athlete: bool = True) -> float:
        """
        Estimates LMN QID firing rate across lifespan based on Klass et al. (2008)
        and master athletic degradation curves.
        """
        if age <= 25:
            return 100.0

        if is_active_athlete:
            # Slower degradation in masters athletes
            if age <= 55:
                # 0% at 25 to 10% at 55
                reduction = 0.10 * ((age - 25) / 30.0)
            elif age <= 70:
                # 10% at 55 to 20% at 70
                reduction = 0.10 + 0.10 * ((age - 55) / 15.0)
            else:
                # Accelerates past 75
                reduction = 0.20 + 0.25 * ((age - 70) / 15.0)
        else:
            # General sedentary population declines earlier and faster
            if age <= 50:
                reduction = 0.15 * ((age - 25) / 25.0)
            elif age <= 70:
                reduction = 0.15 + 0.25 * ((age - 50) / 20.0)
            else:
                reduction = 0.40 + 0.35 * ((age - 70) / 15.0)

        reduction = min(max(reduction, 0.0), 0.75)
        return 100.0 * (1.0 - reduction)

    def evaluate_profile(self, age: int, is_active_athlete: bool = True) -> AgingProfile:
        tier = "Masters Athlete" if is_active_athlete else "General Population"
        freq = self.estimate_qid_frequency(age, is_active_athlete)
        reduction_pct = ((100.0 - freq) / 100.0) * 100.0
        sim = self.kinematics.simulate_jump(freq)

        if age <= 35:
            masters_corr = "Peak young athletic baseline. Capable of vertical dunk or ~1.00 m clearance."
            clinical = "Optimal motor unit recruitment, robust protective margin against neuromuscular fatigue."
        elif age <= 60:
            masters_corr = "Matches M55 World Record high jump drop-off (~25% decline from prime)."
            clinical = "Early subclinical dynapenia; intact muscle mass masks underlying neural rate coding decay."
        elif age <= 72:
            masters_corr = "Matches M70 World Record high jump drop-off (~47% decline from prime)."
            clinical = "Clinical dynapenia threshold; high vulnerability during unexpected perturbation catch-steps."
        elif age <= 80:
            masters_corr = "Jump clearance collapses below 20 cm. High hurdle clearance impossible."
            clinical = "Locomotive frailty. Rapidly escalating risk of fall-related fractures and morbidity."
        else:
            masters_corr = "Locomotion restricted to shuffling or assisted gait. Zero ballistic capacity."
            clinical = "Severe motor neuron underclocking approaching tonic 25 Hz limit. Extreme frailty."

        return AgingProfile(
            age_years=age,
            athletic_tier=tier,
            qid_frequency_hz=freq,
            qid_reduction_pct=reduction_pct,
            simulation=sim,
            masters_track_correlation=masters_corr,
            clinical_risk_status=clinical
        )

    def run_cohort_study(self, ages: List[int] = None) -> List[AgingProfile]:
        if ages is None:
            ages = [25, 40, 55, 65, 70, 75, 80]
        return [self.evaluate_profile(a) for a in ages]
