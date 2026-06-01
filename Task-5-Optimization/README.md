Task 5 — Advanced Optimization Project (CODTECH)

Overview
- An advanced production-mix optimization using linear programming with PuLP.
- Includes scenario sweeps, simple sensitivity analysis, and plotting.

Files
- `optimization.py`: runnable script implementing model and scenario analysis.
- `data.csv`: example product/resource data.
 - `multi_period_data.csv`: example multi-period demand and parameters.
- `requirements.txt`: python deps.

Quick start
1. Create and activate your venv, then install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r Task-5-Optimization/requirements.txt
```

2. Run the example:

```bash
python Task-5-Optimization/optimization.py
```

3. To run the multi-period MIP example, ensure `multi_period_data.csv` is present and run:

```bash
python Task-5-Optimization/optimization.py
# The script will run the single-period and multi-period examples and show plots
```

4. To run scenario sweeps (capacity / demand variations) and save results:

```bash
python Task-5-Optimization/optimization.py
# scenario results are saved to Task-5-Optimization/results/scenario_results.csv
```

5. The script now includes extended scenario axes: emission caps and shortage costs. It will also save a heatmap image at:

- `Task-5-Optimization/results/profit_heatmap.png`
- `Task-5-Optimization/results/profit_heatmap.csv` (mean profits pivot)

Install the extra plotting dependency:

```bash
pip install seaborn
```
