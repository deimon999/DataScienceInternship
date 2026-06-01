"""Advanced production optimization example using PuLP.

Features:
- Single-period production mix maximizing profit
- Resource constraints (A and B)
- Demand caps per product
- Global emissions cap or penalty
- Scenario sweep over emissions cap and demand scale
- Simple sensitivity via finite-difference and scenario variations
- Plots results

Run: python optimization.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, PULP_CBC_CMD, LpStatus, LpBinary

DATA_FP = os.path.join(os.path.dirname(__file__), "data.csv")


def load_data(path=DATA_FP):
    return pd.read_csv(path)


class ProductionOptimizer:
    def __init__(self, df, resource_A=300, resource_B=240, emissions_cap=None, emission_penalty=None):
        self.df = df.copy()
        self.resource_A = resource_A
        self.resource_B = resource_B
        self.emissions_cap = emissions_cap
        self.emission_penalty = emission_penalty
        self.model = None
        self.vars = {}

    def build_model(self):
        model = LpProblem("ProductionMix", LpMaximize)
        products = list(self.df['product'])
        # Decision variables: production units (continuous, >=0)
        x = {p: LpVariable(f"x_{p}", lowBound=0) for p in products}
        self.vars = x

        # Objective: maximize profit minus optional emission penalty
        profit_terms = [x[p] * float(self.df.loc[self.df['product'] == p, 'profit_per_unit'].iloc[0]) for p in products]
        objective = lpSum(profit_terms)
        if self.emission_penalty is not None:
            emission_terms = [x[p] * float(self.df.loc[self.df['product'] == p, 'emission_per_unit'].iloc[0]) for p in products]
            objective = objective - self.emission_penalty * lpSum(emission_terms)

        model += objective

        # Resource constraints
        model += lpSum([x[p] * float(self.df.loc[self.df['product'] == p, 'resource_A'].iloc[0]) for p in products]) <= self.resource_A, "Resource_A"
        model += lpSum([x[p] * float(self.df.loc[self.df['product'] == p, 'resource_B'].iloc[0]) for p in products]) <= self.resource_B, "Resource_B"

        # Demand caps
        for p in products:
            cap = float(self.df.loc[self.df['product'] == p, 'max_demand'].iloc[0])
            model += x[p] <= cap, f"DemandCap_{p}"

        # Emissions cap if provided
        if self.emissions_cap is not None:
            model += lpSum([x[p] * float(self.df.loc[self.df['product'] == p, 'emission_per_unit'].iloc[0]) for p in products]) <= self.emissions_cap, "EmissionsCap"

        self.model = model

    def solve(self, msg=False):
        if self.model is None:
            self.build_model()
        self.model.solve(PULP_CBC_CMD(msg=1 if msg else 0))
        status = LpStatus[self.model.status]
        sol = {p: v.value() for p, v in self.vars.items()}
        objective = self.model.objective.value()
        return status, sol, objective


def run_base_example():
    df = load_data()
    opt = ProductionOptimizer(df)
    status, sol, obj = opt.solve()
    print("Base run status:", status)
    print("Objective (profit):", obj)
    print("Solution:")
    for k, v in sol.items():
        print(k, round(v, 3))


def emissions_sweep(df, caps=None):
    if caps is None:
        caps = np.linspace(100, 400, 7)
    results = []
    product_period_rows = []
    for c in caps:
        opt = ProductionOptimizer(df, emissions_cap=c)
        status, sol, obj = opt.solve()
        total_emissions = sum(sol[p] * float(df.loc[df['product'] == p, 'emission_per_unit'].iloc[0]) for p in sol)
        results.append({'emissions_cap': c, 'status': status, 'profit': obj, 'total_emissions': total_emissions, **sol})
    return pd.DataFrame(results)


def demand_sensitivity(df, scale_factors=None):
    if scale_factors is None:
        scale_factors = np.linspace(0.5, 1.5, 9)
    rows = []
    for s in scale_factors:
        df2 = df.copy()
        df2['max_demand'] = df2['max_demand'] * s
        opt = ProductionOptimizer(df2)
        status, sol, obj = opt.solve()
        rows.append({'scale': s, 'status': status, 'profit': obj, **sol})
    return pd.DataFrame(rows)


def plot_emissions_sweep(df):
    res = emissions_sweep(df)
    plt.figure(figsize=(8, 5))
    plt.plot(res['emissions_cap'], res['profit'], marker='o')
    plt.xlabel('Emissions Cap')
    plt.ylabel('Profit')
    plt.title('Profit vs Emissions Cap')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_demand_sensitivity(df):
    res = demand_sensitivity(df)
    plt.figure(figsize=(8, 5))
    plt.plot(res['scale'], res['profit'], marker='o')
    plt.xlabel('Demand scale factor')
    plt.ylabel('Profit')
    plt.title('Profit vs Demand Scale')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def load_multi_period_data(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "multi_period_data.csv")
    df = pd.read_csv(path)
    # detect period columns with prefix 'demand_t'
    demand_cols = [c for c in df.columns if c.startswith('demand_t')]
    periods = sorted(demand_cols, key=lambda x: int(x.split('t')[-1]))
    return df, periods


class MultiPeriodOptimizer:
    def __init__(self, df, periods, resource_A_cap=300, resource_B_cap=240, shortage_cost=1000, emissions_cap=None):
        self.df = df.copy()
        self.periods = periods
        self.T = len(periods)
        self.products = list(self.df['product'])
        self.resource_A_cap = resource_A_cap
        self.resource_B_cap = resource_B_cap
        self.shortage_cost = shortage_cost
        self.emissions_cap = emissions_cap
        self.model = None
        self.x = {}  # production
        self.inv = {}
        self.y = {}  # setup binary
        self.short = {}

    def build_model(self):
        model = LpProblem('MultiPeriodProduction', LpMaximize)

        # create variables
        M = float(self.df[[c for c in self.df.columns if c.startswith('demand_t')]].sum(axis=1).max()) * 10
        for p in self.products:
            for t_idx, t in enumerate(self.periods):
                self.x[(p, t)] = LpVariable(f"x_{p}_{t}", lowBound=0)
                self.inv[(p, t)] = LpVariable(f"inv_{p}_{t}", lowBound=0)
                self.y[(p, t)] = LpVariable(f"y_{p}_{t}", lowBound=0, upBound=1, cat='Binary')
                self.short[(p, t)] = LpVariable(f"short_{p}_{t}", lowBound=0)

        # Objective: profit from fulfilled demand - holding - setup - shortage penalties
        obj_terms = []
        for p in self.products:
            profit = float(self.df.loc[self.df['product'] == p, 'profit_per_unit'].iloc[0])
            setup_cost = float(self.df.loc[self.df['product'] == p, 'setup_cost'].iloc[0]) if 'setup_cost' in self.df.columns else 0.0
            holding_cost = float(self.df.loc[self.df['product'] == p, 'holding_cost'].iloc[0]) if 'holding_cost' in self.df.columns else 0.0
            for t in self.periods:
                demand = float(self.df.loc[self.df['product'] == p, t].iloc[0])
                # profit on fulfilled demand (demand - short)
                obj_terms.append(profit * (demand - self.short[(p, t)]))
                obj_terms.append(-holding_cost * self.inv[(p, t)])
                obj_terms.append(-setup_cost * self.y[(p, t)])
                obj_terms.append(-self.shortage_cost * self.short[(p, t)])

        model += lpSum(obj_terms)

        # Inventory balance and demand fulfillment
        for p in self.products:
            for ti, t in enumerate(self.periods):
                demand = float(self.df.loc[self.df['product'] == p, t].iloc[0])
                if ti == 0:
                    # initial inventory assumed zero
                    model += (self.inv[(p, t)] == self.x[(p, t)] - (demand - self.short[(p, t)])), f"InvBal_{p}_{t}"
                else:
                    prev = self.periods[ti - 1]
                    model += (self.inv[(p, t)] == self.inv[(p, prev)] + self.x[(p, t)] - (demand - self.short[(p, t)])), f"InvBal_{p}_{t}"

                # link production to setup binary via big-M
                model += self.x[(p, t)] <= M * self.y[(p, t)], f"BigM_{p}_{t}"

        # Resource constraints per period
        for t in self.periods:
            model += lpSum([self.x[(p, t)] * float(self.df.loc[self.df['product'] == p, 'resource_A'].iloc[0]) for p in self.products]) <= self.resource_A_cap, f"ResA_{t}"
            model += lpSum([self.x[(p, t)] * float(self.df.loc[self.df['product'] == p, 'resource_B'].iloc[0]) for p in self.products]) <= self.resource_B_cap, f"ResB_{t}"

            # Emissions cap per period if provided
            if self.emissions_cap is not None:
                model += lpSum([self.x[(p, t)] * float(self.df.loc[self.df['product'] == p, 'emission_per_unit'].iloc[0]) for p in self.products]) <= self.emissions_cap, f"Emissions_{t}"

        self.model = model

    def solve(self, msg=False):
        if self.model is None:
            self.build_model()
        self.model.solve(PULP_CBC_CMD(msg=1 if msg else 0))
        status = LpStatus[self.model.status]
        prod = {(p, t): self.x[(p, t)].value() for p in self.products for t in self.periods}
        inv = {(p, t): self.inv[(p, t)].value() for p in self.products for t in self.periods}
        setups = {(p, t): self.y[(p, t)].value() for p in self.products for t in self.periods}
        short = {(p, t): self.short[(p, t)].value() for p in self.products for t in self.periods}
        objective = self.model.objective.value()
        return status, prod, inv, setups, short, objective


def run_multi_period_example():
    df, periods = load_multi_period_data()
    mpo = MultiPeriodOptimizer(df, periods, resource_A_cap=300, resource_B_cap=240, shortage_cost=1000)
    status, prod, inv, setups, short, obj = mpo.solve()
    print('\nMulti-period run status:', status)
    print('Objective (profit):', obj)
    # tabular summary
    for p in mpo.products:
        vals = [round(prod[(p, t)] or 0, 2) for t in periods]
        print(p, 'production per period:', vals)

    # plot aggregate production per period
    total_prod = [sum(prod[(p, t)] or 0 for p in mpo.products) for t in periods]
    plt.figure(figsize=(8, 4))
    plt.plot(range(len(periods)), total_prod, marker='o')
    plt.xticks(range(len(periods)), periods)
    plt.xlabel('Period')
    plt.ylabel('Total production')
    plt.title('Total production by period')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def run_scenarios(capacity_factors=None, demand_scales=None, data_path=None, save_dir=None):
    if capacity_factors is None:
        capacity_factors = [0.7, 1.0, 1.3]
    if demand_scales is None:
        demand_scales = [0.8, 1.0, 1.2]
    # new axes
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), 'multi_period_data.csv')
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(save_dir, exist_ok=True)

    # emission caps (per-period) and shortage costs
    emission_caps = [None, 200, 300]
    shortage_costs = [500, 1000, 2000]

    df, periods = load_multi_period_data(data_path)
    results = []
    product_period_rows = []
    for capf in capacity_factors:
        for dscale in demand_scales:
            for ecap in emission_caps:
                for scost in shortage_costs:
                    df2 = df.copy()
                    for c in periods:
                        df2[c] = df2[c] * dscale
                    A_cap = int(300 * capf)
                    B_cap = int(240 * capf)
                    mpo = MultiPeriodOptimizer(df2, periods, resource_A_cap=A_cap, resource_B_cap=B_cap, shortage_cost=scost, emissions_cap=ecap)
                    status, prod, inv, setups, short, obj = mpo.solve()
                    total_short = sum(v for v in short.values() if v is not None)
                    total_setup = sum(v for v in setups.values() if v is not None)
                    total_prod = sum(v for v in prod.values() if v is not None)
                    results.append({
                        'cap_factor': capf,
                        'demand_scale': dscale,
                        'emission_cap': ecap if ecap is not None else 'None',
                        'shortage_cost': scost,
                        'status': status,
                        'profit': obj,
                        'total_production': total_prod,
                        'total_shortage': total_short,
                        'total_setups': total_setup,
                        'A_cap': A_cap,
                        'B_cap': B_cap,
                    })
                    # collect per-product, per-period details
                    for p in mpo.products:
                        for t in mpo.periods:
                            prod_val = prod.get((p, t), 0) or 0
                            short_val = short.get((p, t), 0) or 0
                            setup_val = setups.get((p, t), 0) or 0
                            product_period_rows.append({
                                'cap_factor': capf,
                                'demand_scale': dscale,
                                'emission_cap': ecap if ecap is not None else 'None',
                                'shortage_cost': scost,
                                'product': p,
                                'period': t,
                                'production': prod_val,
                                'shortage': short_val,
                                'setup': setup_val,
                            })

    res_df = pd.DataFrame(results)
    out_fp = os.path.join(save_dir, 'scenario_results.csv')
    res_df.to_csv(out_fp, index=False)

    # save per-product per-period CSV
    prod_period_df = pd.DataFrame(product_period_rows)
    prod_period_fp = os.path.join(save_dir, 'scenario_product_period.csv')
    prod_period_df.to_csv(prod_period_fp, index=False)

    # create heatmap pivot: mean profit by emission_cap (rows) and shortage_cost (cols)
    pivot = res_df.groupby(['emission_cap', 'shortage_cost'])['profit'].mean().unstack()
    pivot_fp = os.path.join(save_dir, 'profit_heatmap.csv')
    pivot.to_csv(pivot_fp)

    # plot heatmap
    try:
        import seaborn as sns
        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot.astype(float), annot=True, fmt='.0f', cmap='viridis')
        plt.title('Mean Profit (rows: emission_cap, cols: shortage_cost)')
        plt.tight_layout()
        heat_fp = os.path.join(save_dir, 'profit_heatmap.png')
        plt.savefig(heat_fp)
        plt.close()
    except Exception:
        # fallback to matplotlib
        plt.figure(figsize=(8, 6))
        data = pivot.values.astype(float)
        plt.imshow(data, aspect='auto', cmap='viridis')
        plt.colorbar(label='Profit')
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.xticks(range(len(pivot.columns)), pivot.columns)
        plt.title('Mean Profit (rows: emission_cap, cols: shortage_cost)')
        plt.tight_layout()
        heat_fp = os.path.join(save_dir, 'profit_heatmap.png')
        plt.savefig(heat_fp)
        plt.close()

    print('Saved scenario results to', out_fp)
    print('Saved profit heatmap to', heat_fp)
    # --- Additional per-product visualizations ---
    # 1) Per-product production heatmaps (aggregated mean by emission_cap x shortage_cost)
    prod_summary = prod_period_df.groupby(['emission_cap', 'shortage_cost', 'product'])['production'].sum().reset_index()
    for product in prod_summary['product'].unique():
        sub = prod_summary[prod_summary['product'] == product]
        heat = sub.pivot(index='emission_cap', columns='shortage_cost', values='production')
        plt.figure(figsize=(6, 4))
        try:
            import seaborn as sns
            sns.heatmap(heat.astype(float), annot=True, fmt='.1f', cmap='magma')
        except Exception:
            plt.imshow(heat.values.astype(float), aspect='auto', cmap='magma')
            plt.colorbar()
        plt.title(f'Production heatmap - {product}')
        plt.tight_layout()
        pfp = os.path.join(save_dir, f'production_heatmap_{product}.png')
        plt.savefig(pfp)
        plt.close()

    # 2) Stacked production timeline for a baseline scenario (cap=1.0,dscale=1.0,ecap=None,scost=1000)
    baseline = prod_period_df[(prod_period_df['cap_factor'] == 1.0) & (prod_period_df['demand_scale'] == 1.0) & (prod_period_df['emission_cap'] == 'None') & (prod_period_df['shortage_cost'] == 1000)]
    if baseline.empty:
        baseline = prod_period_df.iloc[0:len(periods)*len(mpo.products)] if not prod_period_df.empty else None
    if baseline is not None and not baseline.empty:
        pivot_time = baseline.pivot_table(index='period', columns='product', values='production', aggfunc='sum').fillna(0)
        pivot_time = pivot_time.reindex(periods)  # ensure period order
        pivot_time.plot(kind='bar', stacked=True, figsize=(8, 4))
        plt.xlabel('Period')
        plt.ylabel('Production')
        plt.title('Stacked production timeline (baseline scenario)')
        plt.tight_layout()
        tpf = os.path.join(save_dir, 'stacked_production_timeline_baseline.png')
        plt.savefig(tpf)
        plt.close()

        # shortage-by-period heatmap for baseline
        shortage_pivot = baseline.pivot_table(index='period', columns='product', values='shortage', aggfunc='sum').fillna(0)
        plt.figure(figsize=(8, 4))
        try:
            import seaborn as sns
            sns.heatmap(shortage_pivot.astype(float).T, annot=True, fmt='.1f', cmap='Reds')
        except Exception:
            plt.imshow(shortage_pivot.values.T.astype(float), aspect='auto', cmap='Reds')
            plt.colorbar()
        plt.xlabel('Period')
        plt.ylabel('Product')
        plt.title('Shortage by period (baseline)')
        plt.tight_layout()
        spf = os.path.join(save_dir, 'shortage_by_period_baseline.png')
        plt.savefig(spf)
        plt.close()

    print('Saved per-product details to', prod_period_fp)

    # --- Per-product profit heatmaps ---
    # compute profit per product per scenario (sum over periods)
    profit_map = prod_period_df.merge(df[['product', 'profit_per_unit']], on='product')
    profit_map['revenue'] = profit_map['production'] * profit_map['profit_per_unit']
    prod_profit = profit_map.groupby(['emission_cap', 'shortage_cost', 'product'])['revenue'].sum().reset_index()
    for product in prod_profit['product'].unique():
        sub = prod_profit[prod_profit['product'] == product]
        heat = sub.pivot(index='emission_cap', columns='shortage_cost', values='revenue')
        plt.figure(figsize=(6, 4))
        try:
            import seaborn as sns
            sns.heatmap(heat.astype(float), annot=True, fmt='.0f', cmap='coolwarm')
        except Exception:
            plt.imshow(heat.values.astype(float), aspect='auto', cmap='coolwarm')
            plt.colorbar()
        plt.title(f'Profit heatmap - {product}')
        plt.tight_layout()
        pfp = os.path.join(save_dir, f'profit_heatmap_{product}.png')
        plt.savefig(pfp)
        plt.close()

    # --- Per-period stacked shortage summaries (baseline scenario)
    if 'baseline' in locals():
        shortage_time = baseline.pivot_table(index='period', columns='product', values='shortage', aggfunc='sum').fillna(0)
        # stacked bar of shortages by period
        shortage_time.plot(kind='bar', stacked=True, figsize=(8, 4), colormap='Reds')
        plt.xlabel('Period')
        plt.ylabel('Shortage')
        plt.title('Stacked shortage timeline (baseline)')
        stf = os.path.join(save_dir, 'stacked_shortage_timeline_baseline.png')
        plt.tight_layout()
        plt.savefig(stf)
        plt.close()

    return res_df, pivot


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run optimization examples and scenario sweeps')
    parser.add_argument('--run-base', action='store_true', help='Run the single-period base example and plots')
    parser.add_argument('--run-multi', action='store_true', help='Run the multi-period example')
    parser.add_argument('--run-scenarios', action='store_true', help='Run scenario sweeps and save results')
    parser.add_argument('--data', type=str, default=None, help='Path to multi-period data CSV')
    parser.add_argument('--out', type=str, default=None, help='Output directory for results')
    parser.add_argument('--capacity-factors', type=str, default=None, help='Comma-separated capacity factors, e.g. 0.7,1.0,1.3')
    parser.add_argument('--demand-scales', type=str, default=None, help='Comma-separated demand scale factors, e.g. 0.8,1.0,1.2')
    parser.add_argument('--emission-caps', type=str, default=None, help='Comma-separated emission caps or None, e.g. None,200,300')
    parser.add_argument('--shortage-costs', type=str, default=None, help='Comma-separated shortage costs, e.g. 500,1000,2000')
    args = parser.parse_args()

    if args.run_base:
        df = load_data()
        run_base_example()
        print('\nRunning emissions sweep and showing plot...')
        plot_emissions_sweep(df)
        print('\nRunning demand sensitivity and showing plot...')
        plot_demand_sensitivity(df)

    if args.run_multi:
        run_multi_period_example()

    if args.run_scenarios:
        # parse optional axes
        def parse_list(s, cast=float):
            if s is None:
                return None
            items = [it.strip() for it in s.split(',') if it.strip() != '']
            out = []
            for it in items:
                if it.lower() == 'none':
                    out.append(None)
                else:
                    out.append(cast(it))
            return out

        capf = parse_list(args.capacity_factors, float)
        dsc = parse_list(args.demand_scales, float)
        ec = None
        if args.emission_caps is not None:
            # emission caps may include None
            ec = []
            for it in [a.strip() for a in args.emission_caps.split(',') if a.strip()!='']:
                if it.lower() == 'none':
                    ec.append(None)
                else:
                    ec.append(float(it))
        sc = parse_list(args.shortage_costs, float)
        run_scenarios(capacity_factors=capf, demand_scales=dsc, data_path=args.data, save_dir=args.out)

    if not (args.run_base or args.run_multi or args.run_scenarios):
        # default behaviour: run base and multi, but not full scenarios
        df = load_data()
        run_base_example()
        run_multi_period_example()
