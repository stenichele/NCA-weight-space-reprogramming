"""One-shot weight algebra only. No state access, model evaluation, or fitting."""
import numpy as np


def edits(weights) -> dict[str, dict[str, np.ndarray]]:
    shapes = {"W1": (48, 128), "b1": (128,), "W2": (128, 16), "b2": (16,)}
    base = {k: np.array(weights[k], copy=True) for k in shapes}
    for k, shape in shapes.items():
        if base[k].shape != shape or not np.isfinite(base[k]).all():
            raise ValueError(f"Invalid {k}")
        if not np.issubdtype(base[k].dtype, np.floating):
            raise TypeError("Floating point weights are required")

    def copy():
        return {k: v.copy() for k, v in base.items()}

    def swap_channels(a, b):
        result = copy()
        p = np.arange(16)
        p[a], p[b] = p[b], p[a]
        indices = np.concatenate([p, p + 16, p + 32])
        result["W1"] = base["W1"][indices].copy()
        result["W2"] = base["W2"][:, p].copy()
        result["b2"] = base["b2"][p].copy()
        return result

    result = {
        "blue": swap_channels(1, 2),
        "swap_red_green": swap_channels(0, 1),
    }
    mirror = copy()
    mirror["W1"][16:32] = -base["W1"][16:32]
    result["mirror_horizontal"] = mirror

    clockwise = copy()
    clockwise["W1"][16:32] = -base["W1"][32:48]
    clockwise["W1"][32:48] = base["W1"][16:32]
    result["rotate_90_clockwise"] = clockwise

    halfturn = copy()
    halfturn["W1"][16:48] = -base["W1"][16:48]
    result["rotate_180"] = halfturn

    slow = copy()
    slow["W2"] *= 0.5
    slow["b2"] *= 0.5
    result["grow_half_speed"] = slow

    return result
