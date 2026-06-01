import importlib.util
import os
spec = importlib.util.spec_from_file_location('optmod', os.path.join('Task-5-Optimization','optimization.py'))
opt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opt)
opt.run_scenarios()
print('run_scenarios completed')
