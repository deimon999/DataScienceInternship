import os
import pandas as pd
import importlib.util

res_fp = os.path.join('Task-5-Optimization', 'results', 'scenario_results.csv')
if not os.path.exists(res_fp):
    # run scenarios to produce results
    spec = importlib.util.spec_from_file_location('optmod', os.path.join('Task-5-Optimization', 'optimization.py'))
    opt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(opt)
    opt.run_scenarios()

# read results
df = pd.read_csv(res_fp)

# compute summaries
best = df.sort_values('profit', ascending=False).head(5)
worst = df.sort_values('profit', ascending=True).head(5)
avg_by_cap = df.groupby('cap_factor')['profit'].mean().reset_index()

report_lines = []
report_lines.append('# Optimization Scenario Report')
report_lines.append('')
report_lines.append('Generated from `Task-5-Optimization/results/scenario_results.csv`')
report_lines.append('')
report_lines.append('## Top 5 scenarios (by profit)')
report_lines.append('')
report_lines.append(best.to_markdown(index=False))
report_lines.append('')
report_lines.append('## Bottom 5 scenarios (by profit)')
report_lines.append('')
report_lines.append(worst.to_markdown(index=False))
report_lines.append('')
report_lines.append('## Average profit by capacity factor')
report_lines.append('')
report_lines.append(avg_by_cap.to_markdown(index=False))

out = os.path.join('Task-5-Optimization', 'results', 'REPORT.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print('Wrote report to', out)
