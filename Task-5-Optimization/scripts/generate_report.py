import pandas as pd
import os
base = os.path.dirname(__file__)
p = os.path.join(base, '..', 'results', 'scenario_results.csv')
p = os.path.normpath(p)
df = pd.read_csv(p)
# top 5 by profit
top=df.sort_values('profit', ascending=False).head(5)
# mean profit by cap_factor
mean_by_cap=df.groupby('cap_factor')['profit'].mean().reset_index()
# effect of emission cap
mean_by_em=df.groupby('emission_cap')['profit'].mean().reset_index()
report='''# Task-5 Optimization - Scenario Summary

This report summarizes the scenario sweep results (see `results/scenario_results.csv`).

## Top 5 scenarios by profit
'''
for i,row in top.iterrows():
    report+=f"- cap_factor={row.cap_factor}, demand_scale={row.demand_scale}, emission_cap={row.emission_cap}, shortage_cost={row.shortage_cost} -> profit={row.profit:.2f}\n"
report+="\n## Mean profit by capacity factor\n"
for i,row in mean_by_cap.iterrows():
    report+=f"- cap_factor={row.cap_factor}: mean profit={row.profit:.2f}\n"
report+="\n## Mean profit by emission cap (rows in heatmap)\n"
for i,row in mean_by_em.iterrows():
    report+=f"- emission_cap={row.emission_cap}: mean profit={row.profit:.2f}\n"
report+="\nGenerated files:\n- results/scenario_results.csv\n- results/scenario_product_period.csv\n- results/profit_heatmap.png and per-product heatmaps\n- results/production_heatmap_<product>.png\n- results/stacked_production_timeline_baseline.png\n- results/shortage_by_period_baseline.png\n- results/stacked_shortage_timeline_baseline.png\n"
open('..\\REPORT.md','w').write(report)
print('Wrote REPORT.md')
