# Digital Advertising Budget Optimizer

A Big Data Analytics project that answers one business question:
**where should a company spend its next Rs. 1,000,000 across Facebook, Instagram, Google, TikTok and YouTube?**

Author: Amna Bashir, BSAI

## What this project does

1. Simulates advertising campaign data (10,000 to 10 million records).
2. Calculates CTR, CPC, CPA, conversion rate, ROAS, revenue and profit per platform and per campaign.
3. Compares Pandas, a MapReduce-style Python implementation and Spark on growing data sizes.
4. Builds a budget recommendation engine that splits Rs. 1,000,000 across the five platforms.

> **Important:** all data is simulated. Results show how the method works. They do not prove real-world platform performance.

## Data

Each record is one campaign-day for one audience segment, with 12 columns:
`date, campaign, platform, impressions, clicks, spend, conversions, revenue, age, gender, city, device`.

- Period: 2025-01-01 to 2025-12-31, 4 campaigns, 7 cities, 4 age groups, 3 device types.
- Random seed is fixed (42), so the data is reproducible.
- Each platform has its own "personality" (illustrative assumptions, not real benchmarks):

| Platform | CPM (Rs.) | Click rate | Conversion rate | Avg. order (Rs.) |
|---|---|---|---|---|
| Facebook | 350 | 1.0% | 2.5% | 4,500 |
| Instagram | 450 | 0.9% | 3.5% | 5,000 |
| Google | 1,500 | 3.0% | 3.5% | 5,500 |
| TikTok | 250 | 1.6% | 1.2% | 3,000 |
| YouTube | 300 | 0.5% | 2.0% | 4,500 |

## Results

### 1. Platform performance (10,000 records)

Metrics are calculated from platform totals (sum first, then divide).
Profit = revenue minus ad spend only.

| Platform | Spend (Rs.) | Revenue (Rs.) | CTR (%) | CPC (Rs.) | CPA (Rs.) | Conv. rate (%) | ROAS |
|---|---|---|---|---|---|---|---|
| Google | 74,183,227 | 335,206,446 | 3.23 | 46.36 | 1,225.30 | 3.78 | 4.52 |
| Instagram | 27,628,076 | 108,981,694 | 0.95 | 47.77 | 1,278.13 | 3.74 | 3.94 |
| Facebook | 21,460,341 | 78,866,584 | 1.06 | 32.94 | 1,238.55 | 2.66 | 3.67 |
| TikTok | 8,951,217 | 23,832,886 | 1.72 | 14.64 | 1,122.13 | 1.30 | 2.66 |
| YouTube | 10,834,782 | 18,996,463 | 0.53 | 56.51 | 2,603.26 | 2.17 | 1.75 |

By campaign, ROAS is highest for Eid Sale (5.80), then Winter Sale (4.36), Summer Collection (3.69) and Brand Awareness (1.45).
Charts are in `outputs/figures/`.

### 2. Pandas vs MapReduce vs Spark

Task: read a Parquet file and sum five columns per platform.
Median of 3 runs on Google Colab (2 CPU cores, 13.6 GB RAM). All three tools returned matching results.

| Records | Pandas (s) | MapReduce (s) | Spark (s) |
|---|---|---|---|
| 10,000 | 0.01 | 0.07 | 0.57 |
| 100,000 | 0.06 | 0.41 | 0.57 |
| 1,000,000 | 0.24 | 4.60 | 1.57 |
| 10,000,000 | 2.39 | 48.01 | 4.40 |

Pandas was fastest at every size because the data (about 200 MB at 10 million rows) fits easily in memory.
Spark pays a fixed start-up cost, but its time grows much more slowly than MapReduce.
These tests do not show how the tools behave when data is larger than memory or on a cluster.

### 3. Budget recommendation for Rs. 1,000,000

- **Engine A:** share proportional to ROAS.
- **Engine C:** assumes diminishing returns (each extra rupee earns less). The best split gives each platform a share proportional to `ROAS^(1/(1-b))`. The strength `b = 0.7` is an assumption, checked with 0.6 and 0.8.
- Limits: every platform gets at least 5% and at most 40%.

| Platform | Engine A share | Engine A (Rs.) | Engine C share | Engine C (Rs.) |
|---|---|---|---|---|
| Google | 27.3% | 273,277 | 40.0% | 400,000 |
| Instagram | 23.8% | 238,210 | 26.7% | 267,090 |
| Facebook | 22.2% | 221,886 | 21.1% | 210,809 |
| TikTok | 16.1% | 160,822 | 7.2% | 72,101 |
| YouTube | 10.6% | 105,804 | 5.0% | 50,000 |

**Sensitivity of Engine C to b (budget share):**

| Platform | b = 0.6 | b = 0.7 | b = 0.8 |
|---|---|---|---|
| Google | 37.0% | 40.0% | 40.0% |
| Instagram | 26.2% | 26.7% | 29.4% |
| Facebook | 22.0% | 21.1% | 20.6% |
| TikTok | 9.8% | 7.2% | 5.0% |
| YouTube | 5.0% | 5.0% | 5.0% |

Google, Instagram and Facebook keep the same order for all three values of b. YouTube stays at the 5% minimum in every case, and TikTok falls from 9.8% to the 5% minimum as b increases, so at b = 0.8 TikTok and YouTube receive the same share.

**Modelled expected revenue (Rs.) for a Rs. 1,000,000 budget:**

| Strategy | b = 0.6 | b = 0.7 | b = 0.8 | Uplift vs equal split (b = 0.7) |
|---|---|---|---|---|
| Equal split (20% each) | 3,308,000 | 3,308,000 | 3,308,000 | 0.00% |
| Historical spend split | 3,450,804 | 3,543,496 | 3,657,554 | 7.12% |
| Engine A (ROAS) | 3,452,192 | 3,485,550 | 3,521,489 | 5.37% |
| Engine C (diminishing returns) | 3,505,899 | 3,588,054 | 3,683,362 | 8.47% |

## Limitations

- All data is simulated, and the platform settings are my own assumptions, not real benchmarks.
- In the simulated data revenue grows in proportion to spend, so diminishing returns cannot be learned from the data. The value of `b` is an assumption.
- The strategy comparison uses the same model that Engine C is built on. It illustrates the method and is not proof that Engine C works in practice. The gap between Engine C and the historical split is small (about 1.4 percentage points at b = 0.7).
- ROAS values come from 10,000 records, so they contain sampling error.
- Profit ignores product and operating costs.
- "MapReduce" here is a single-machine Python implementation of the map and reduce steps, not a Hadoop cluster.
- The benchmark ran on a free Colab machine with 2 cores. Colab used pandas 2.2.3, while the laptop used pandas 3.0.6. Datasets of different sizes are independent samples from the same generator.

## Project structure

```
src/         data_generator.py, metrics.py, budget_engine.py, check_env.py
notebooks/   01 generate data, 02 metrics, 03 charts, 04 benchmark (Colab), 05 budget engine
outputs/     figures/ (7 charts) and tables/ (5 CSV files)
data/        raw and backup data (not uploaded, recreated by the code)
```

## How to reproduce

1. Install the libraries: `pip install -r requirements.txt`
2. Run the notebooks one cell at a time, in this order: `01`, `02`, `03`, `05`. Notebook `01` refuses to overwrite an existing raw data file.
3. Notebook `04` runs on Google Colab. Upload `src/data_generator.py` first. Colab provides Java 21 and PySpark 4.0.5.

## Credits

The course brief pointed to public GitHub marketing-analytics projects as a starting point. They were used only for ideas. All code in this repository was written for this project.