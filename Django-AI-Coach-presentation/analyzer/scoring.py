import math

def compute_score(pc: float, m_bar: float, sigma: float, eye: float, sym: float, jerk: float) -> float:
    raw_score = 100 * (
        0.25 * (1.0 - pc) +
        0.20 * max(0.0, 1.0 - abs(m_bar - 0.5)) +
        0.15 * math.exp(-sigma) +
        0.20 * eye +
        0.10 * sym +
        0.10 * max(0.0, 1.0 - jerk)
    )
    return max(0.0, min(100.0, raw_score))
