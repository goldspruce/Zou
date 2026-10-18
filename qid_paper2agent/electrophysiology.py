"""
Electrophysiological modeling of Upper Motor Neuron (UMN) temporal summation
and Lower Motor Neuron (LMN) subthreshold depolarization priming.
Derived from Appendix D of 'The Quick Initial Doublet' (pp. 7-9).
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List

# Biophysical Constants from Manuscript
DEFAULT_TAU_MS = 4.0             # AMPA EPSP decay time constant (ms)
DEFAULT_V_REST_MV = -65.0        # Resting membrane potential (mV)
DEFAULT_V_TARGET_MV = -55.0      # Action potential threshold potential (mV)
DEFAULT_DELTA_V_TARGET = 10.0    # Target depolarization (mV)
BASELINE_UMN_FREQ_HZ = 200.0     # Healthy M1 Upper Motor Neuron QID baseline (Hz)


@dataclass
class SummationResult:
    frequency_hz: float
    dt_ms: float
    decay_ratio: float
    retention_r: float
    summation_multiplier_m: float
    summation_gain_g: float
    depolarization_mv: float
    membrane_potential_vm: float
    gain_collapse_pct: float
    threshold_deficit_mv: float
    primes_threshold: bool
    physiological_impact: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frequency_hz": round(self.frequency_hz, 2),
            "dt_ms": round(self.dt_ms, 2),
            "decay_ratio": round(self.decay_ratio, 3),
            "retention_pct": round(self.retention_r * 100.0, 2),
            "summation_multiplier_m": round(self.summation_multiplier_m, 4),
            "summation_gain_g": round(self.summation_gain_g, 4),
            "depolarization_mv": round(self.depolarization_mv, 2),
            "membrane_potential_vm": round(self.membrane_potential_vm, 2),
            "gain_collapse_pct": round(self.gain_collapse_pct, 1),
            "threshold_deficit_mv": round(self.threshold_deficit_mv, 2),
            "primes_threshold": self.primes_threshold,
            "physiological_impact": self.physiological_impact
        }


class ElectrophysiologyEngine:
    """
    Simulates synaptic temporal summation and LMN membrane priming under UMN QID drive.
    """
    def __init__(
        self,
        tau_ms: float = DEFAULT_TAU_MS,
        v_rest_mv: float = DEFAULT_V_REST_MV,
        v_target_mv: float = DEFAULT_V_TARGET_MV,
        f_base_hz: float = BASELINE_UMN_FREQ_HZ
    ):
        self.tau_ms = tau_ms
        self.v_rest_mv = v_rest_mv
        self.v_target_mv = v_target_mv
        self.delta_v_target = v_target_mv - v_rest_mv
        self.f_base_hz = f_base_hz

        # Calibrate baseline unitary EPSP weight E0
        dt_base = 1000.0 / self.f_base_hz
        r_base = math.exp(-dt_base / self.tau_ms)
        self.m_base = 1.0 / (1.0 - r_base)
        self.g_base = self.m_base - 1.0
        self.e0 = self.delta_v_target / self.m_base

    def calculate_summation(self, frequency_hz: float) -> SummationResult:
        """
        Calculates temporal summation metrics for an arbitrary UMN frequency.
        """
        if frequency_hz <= 0:
            raise ValueError("Frequency must be positive.")

        dt_ms = 1000.0 / frequency_hz
        decay_ratio = dt_ms / self.tau_ms
        r = math.exp(-decay_ratio)
        m = 1.0 / (1.0 - r)
        g = m - 1.0

        depol_mv = self.e0 * m
        vm = self.v_rest_mv + depol_mv
        gain_collapse_pct = (1.0 - (g / self.g_base)) * 100.0
        deficit_mv = max(0.0, self.v_target_mv - vm)
        primes_threshold = vm >= (self.v_target_mv - 0.05)

        # Physiological qualitative impact mapping
        if frequency_hz >= 190.0:
            impact = (
                "Healthy 'engine start': robust subthreshold depolarization to -55 mV. "
                "Subsequent single M1 spikes reliably trigger instantaneous LMN firing."
            )
        elif frequency_hz >= 140.0:
            impact = (
                f"25% Degradation regime: Summation gain drops by ~42%. Vm stranded at {vm:.1f} mV. "
                f"A single M1 spike fails to discharge the LMN; extra spikes required, doubling initiation latency."
            )
        elif frequency_hz >= 90.0:
            impact = (
                f"50% Degradation regime: Summation gain collapses by ~78%. Over 91% of EPSP dissipates between spikes. "
                f"Dynamic 'engine start' vanishes; motor initiation reduces to sluggish voluntary ramp-up."
            )
        else:
            impact = (
                f"Severe Degradation / Tonic drive regime: Less than 1% residual voltage remains between spikes. "
                f"Summation gain collapses by >98%. Dynamic subthreshold priming is mathematically impossible."
            )

        return SummationResult(
            frequency_hz=frequency_hz,
            dt_ms=dt_ms,
            decay_ratio=decay_ratio,
            retention_r=r,
            summation_multiplier_m=m,
            summation_gain_g=g,
            depolarization_mv=depol_mv,
            membrane_potential_vm=vm,
            gain_collapse_pct=gain_collapse_pct,
            threshold_deficit_mv=deficit_mv,
            primes_threshold=primes_threshold,
            physiological_impact=impact
        )

    def evaluate_regimes(self, frequencies: List[float] = None) -> List[SummationResult]:
        """Evaluates the primary degradation regimes described in the paper."""
        if frequencies is None:
            frequencies = [200.0, 150.0, 100.0, 50.0]
        return [self.calculate_summation(f) for f in frequencies]
