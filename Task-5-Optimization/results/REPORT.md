# Optimization Scenario Report

Generated from `Task-5-Optimization/results/scenario_results.csv`

## Top 5 scenarios (by profit)

|   cap_factor |   demand_scale |   emission_cap |   shortage_cost | status   |   profit |   total_production |   total_shortage |   total_setups |   A_cap |   B_cap |
|-------------:|---------------:|---------------:|----------------:|:---------|---------:|-------------------:|-----------------:|---------------:|--------:|--------:|
|          1.3 |            1.2 |            nan |            2000 | Optimal  |   7939.2 |                360 |                0 |              8 |     390 |     312 |
|          1.3 |            1.2 |            nan |             500 | Optimal  |   7939.2 |                360 |                0 |              8 |     390 |     312 |
|          1.3 |            1.2 |            nan |            1000 | Optimal  |   7939.2 |                360 |                0 |              8 |     390 |     312 |
|          1.3 |            1   |            nan |            1000 | Optimal  |   6521.4 |                300 |                0 |              7 |     390 |     312 |
|          1.3 |            1   |            nan |             500 | Optimal  |   6521.4 |                300 |                0 |              7 |     390 |     312 |

## Bottom 5 scenarios (by profit)

|   cap_factor |   demand_scale |   emission_cap |   shortage_cost | status   |   profit |   total_production |   total_shortage |   total_setups |   A_cap |   B_cap |
|-------------:|---------------:|---------------:|----------------:|:---------|---------:|-------------------:|-----------------:|---------------:|--------:|--------:|
|          0.7 |            1.2 |            200 |            2000 | Optimal  |  -305371 |            205.6   |          154.4   |              9 |     210 |     168 |
|          1   |            1.2 |            200 |            2000 | Optimal  |  -290090 |            213     |          147     |              6 |     300 |     240 |
|          1.3 |            1.2 |            200 |            2000 | Optimal  |  -289941 |            213     |          147     |              5 |     390 |     312 |
|          0.7 |            1.2 |            300 |            2000 | Optimal  |  -275314 |            219.857 |          140.143 |              7 |     210 |     168 |
|          0.7 |            1.2 |            nan |            2000 | Optimal  |  -275314 |            219.857 |          140.143 |              7 |     210 |     168 |

## Average profit by capacity factor

|   cap_factor |   profit |
|-------------:|---------:|
|          0.7 | -99631.8 |
|          1   | -53348.3 |
|          1.3 | -44840.3 |