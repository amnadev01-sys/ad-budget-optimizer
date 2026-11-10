"""Simulated digital advertising data generator.

Each row is one campaign-day for one audience segment
(age group, gender, city, device) on one platform.
All platform settings below are illustrative assumptions,
not real-world benchmarks.
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START_DATE = "2025-01-01"
N_DAYS = 365

# Platform "personalities" (assumptions)
# cpm = cost per 1000 impressions (Rs.), ctr = click rate,
# cvr = share of clicks that convert, aov = average order value (Rs.)
PLATFORMS = {
    "Facebook":  {"share": 0.25, "cpm": 350,  "ctr": 0.010, "cvr": 0.025, "aov": 4500,
                  "age": [0.10, 0.30, 0.30, 0.30], "device": [0.80, 0.15, 0.05]},
    "Instagram": {"share": 0.25, "cpm": 450,  "ctr": 0.009, "cvr": 0.035, "aov": 5000,
                  "age": [0.30, 0.40, 0.20, 0.10], "device": [0.90, 0.07, 0.03]},
    "Google":    {"share": 0.20, "cpm": 1500, "ctr": 0.030, "cvr": 0.035, "aov": 5500,
                  "age": [0.15, 0.35, 0.30, 0.20], "device": [0.55, 0.40, 0.05]},
    "TikTok":    {"share": 0.15, "cpm": 250,  "ctr": 0.016, "cvr": 0.012, "aov": 3000,
                  "age": [0.45, 0.35, 0.15, 0.05], "device": [0.97, 0.01, 0.02]},
    "YouTube":   {"share": 0.15, "cpm": 300,  "ctr": 0.005, "cvr": 0.020, "aov": 4500,
                  "age": [0.25, 0.35, 0.25, 0.15], "device": [0.70, 0.20, 0.10]},
}

# Campaign types change click and conversion rates
CAMPAIGNS = {
    "Eid Sale":           {"prob": 0.25, "ctr_mult": 1.2, "cvr_mult": 1.3},
    "Summer Collection":  {"prob": 0.30, "ctr_mult": 1.0, "cvr_mult": 1.0},
    "Winter Sale":        {"prob": 0.25, "ctr_mult": 1.1, "cvr_mult": 1.1},
    "Brand Awareness":    {"prob": 0.20, "ctr_mult": 0.8, "cvr_mult": 0.5},
}

AGE_GROUPS = ["18-24", "25-34", "35-44", "45+"]
DEVICES = ["Mobile", "Desktop", "Tablet"]
GENDERS = ["Female", "Male"]
CITIES = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar"]
CITY_PROBS = [0.25, 0.28, 0.15, 0.08, 0.10, 0.07, 0.07]


def generate_ad_data(n_rows, seed=SEED):
    """Return a DataFrame with n_rows of simulated advertising records."""
    rng = np.random.default_rng(seed)

    # --- Platform and campaign ---
    platform_names = list(PLATFORMS)
    platform_idx = rng.choice(len(platform_names), size=n_rows,
                              p=[PLATFORMS[p]["share"] for p in platform_names])
    campaign_names = list(CAMPAIGNS)
    campaign_idx = rng.choice(len(campaign_names), size=n_rows,
                              p=[CAMPAIGNS[c]["prob"] for c in campaign_names])

    # --- Per-row parameters looked up from the settings ---
    def lookup(settings, key, idx):
        return np.array([settings[name][key] for name in settings])[idx]

    cpm = lookup(PLATFORMS, "cpm", platform_idx)
    base_ctr = lookup(PLATFORMS, "ctr", platform_idx)
    base_cvr = lookup(PLATFORMS, "cvr", platform_idx)
    aov = lookup(PLATFORMS, "aov", platform_idx)
    ctr_mult = lookup(CAMPAIGNS, "ctr_mult", campaign_idx)
    cvr_mult = lookup(CAMPAIGNS, "cvr_mult", campaign_idx)

    # --- Funnel: impressions -> clicks -> conversions -> revenue ---
    impressions = rng.lognormal(mean=np.log(20000), sigma=0.6, size=n_rows).astype(np.int64)
    impressions = np.clip(impressions, 1000, None)

    ctr = np.clip(base_ctr * ctr_mult * rng.lognormal(0, 0.25, n_rows), 0.0005, 0.2)
    clicks = rng.binomial(impressions, ctr)

    cvr = np.clip(base_cvr * cvr_mult * rng.lognormal(0, 0.25, n_rows), 0.001, 0.5)
    conversions = rng.binomial(clicks, cvr)

    spend = np.round(impressions / 1000 * cpm * rng.lognormal(0, 0.10, n_rows), 2)
    revenue = np.round(conversions * aov * rng.lognormal(0, 0.15, n_rows), 2)

    # --- Audience: age and device depend on the platform ---
    age_idx = np.zeros(n_rows, dtype=np.int64)
    device_idx = np.zeros(n_rows, dtype=np.int64)
    for i, name in enumerate(platform_names):
        mask = platform_idx == i
        count = int(mask.sum())
        age_idx[mask] = rng.choice(len(AGE_GROUPS), size=count, p=PLATFORMS[name]["age"])
        device_idx[mask] = rng.choice(len(DEVICES), size=count, p=PLATFORMS[name]["device"])

    gender = rng.choice(GENDERS, size=n_rows, p=[0.55, 0.45])
    city = rng.choice(CITIES, size=n_rows, p=CITY_PROBS)
    days = rng.integers(0, N_DAYS, size=n_rows)

    return pd.DataFrame({
        "date": pd.Timestamp(START_DATE) + pd.to_timedelta(days, unit="D"),
        "campaign": np.array(campaign_names)[campaign_idx],
        "platform": np.array(platform_names)[platform_idx],
        "impressions": impressions,
        "clicks": clicks,
        "spend": spend,
        "conversions": conversions,
        "revenue": revenue,
        "age": np.array(AGE_GROUPS)[age_idx],
        "gender": gender,
        "city": city,
        "device": np.array(DEVICES)[device_idx],
    })


def save_raw_data(df, path, backup_dir):
    """Save raw data and a backup copy. Never overwrites an existing file."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"{path} already exists and was not overwritten.")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, Path(backup_dir) / path.name)