"""Budget recommendation engines for the digital advertising project.

Revenue model used for Engine C (an assumption, not learned from the data):
    revenue_i(spend) = ROAS_i * ref * (spend / ref) ** b,   with 0 < b < 1
where ref is the equal-split spend per platform. At the equal split each
platform earns exactly its historical ROAS; spending more or less changes
the return. The best split equalises the return of the next rupee on every
platform, which gives:  spend_i is proportional to ROAS_i ** (1 / (1 - b)).
"""
import numpy as np
import pandas as pd

BUDGET = 1_000_000   # Rs.
MIN_SHARE = 0.05     # every platform gets at least 5%
MAX_SHARE = 0.40     # no platform gets more than 40%
BASE_B = 0.7         # base diminishing-returns strength (assumption)


def allocate_with_limits(weights, budget, min_share, max_share):
    """Split the budget in proportion to the weights, keeping every
    platform between its minimum and maximum share."""
    weights = pd.Series(weights, dtype=float)
    low, high = budget * min_share, budget * max_share
    allocation = pd.Series(np.nan, index=weights.index)
    free = list(weights.index)
    remaining = float(budget)
    tolerance = 1e-9

    while free:
        split = remaining * weights[free] / weights[free].sum()
        too_high = split[split > high + tolerance]
        too_low = split[split < low - tolerance]

        if too_high.empty and too_low.empty:
            allocation[free] = split
            break

        # Fix the larger violation first, then re-split the rest
        excess = (too_high - high).sum()
        deficit = (low - too_low).sum()
        if excess >= deficit:
            allocation[too_high.index] = high
            remaining -= high * len(too_high)
            fixed = too_high.index
        else:
            allocation[too_low.index] = low
            remaining -= low * len(too_low)
            fixed = too_low.index
        free = [name for name in free if name not in fixed]

    return allocation


def roas_proportional(roas, budget, min_share, max_share):
    """Engine A: share proportional to ROAS."""
    return allocate_with_limits(roas, budget, min_share, max_share)


def diminishing_returns(roas, budget, min_share, max_share, b):
    """Engine C: best split when returns shrink as spend grows."""
    weights = pd.Series(roas, dtype=float) ** (1 / (1 - b))
    return allocate_with_limits(weights, budget, min_share, max_share)


def expected_revenue(allocation, roas, budget, b):
    """Expected revenue per platform under the diminishing-returns model."""
    ref = budget / len(roas)
    return roas * ref * (allocation / ref) ** b