"""Advertising performance metrics."""
import numpy as np
import pandas as pd

SUM_COLUMNS = ["impressions", "clicks", "spend", "conversions", "revenue"]


def add_metrics(totals):
    """Add CTR, CPC, CPA, CVR, ROAS and profit to a table of summed columns."""
    result = totals.copy()
    result["ctr_pct"] = result["clicks"] / result["impressions"] * 100
    result["cpc"] = result["spend"] / result["clicks"].replace(0, np.nan)
    result["cpa"] = result["spend"] / result["conversions"].replace(0, np.nan)
    result["cvr_pct"] = result["conversions"] / result["clicks"].replace(0, np.nan) * 100
    result["roas"] = result["revenue"] / result["spend"]
    result["profit"] = result["revenue"] - result["spend"]
    return result


def summarize(df, by):
    """Sum the raw columns per group, then calculate the metrics."""
    totals = df.groupby(by, observed=True)[SUM_COLUMNS].sum()
    return add_metrics(totals).round(2)