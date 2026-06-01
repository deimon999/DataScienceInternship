import tempfile
import os
import shutil
import importlib.util


def load_opt_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'optimization.py')
    path = os.path.normpath(path)
    spec = importlib.util.spec_from_file_location('optmod', path)
    optmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(optmod)
    return optmod


def test_run_scenarios_smoke():
    optmod = load_opt_module()
    tmp = tempfile.mkdtemp()
    try:
        res_df, pivot = optmod.run_scenarios(capacity_factors=[1.0], demand_scales=[1.0], data_path=os.path.join(os.path.dirname(optmod.__file__), 'multi_period_data.csv'), save_dir=tmp)
        out_csv = os.path.join(tmp, 'scenario_results.csv')
        prod_csv = os.path.join(tmp, 'scenario_product_period.csv')
        assert os.path.exists(out_csv)
        assert os.path.exists(prod_csv)
        assert len(res_df) > 0
    finally:
        shutil.rmtree(tmp)
