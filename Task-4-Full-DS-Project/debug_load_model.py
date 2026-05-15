import importlib, traceback
from pathlib import Path
try:
    utils = importlib.import_module('src.utils')
    print('utils module loaded')
    p = Path('models/best_model.pkl')
    print('exists:', p.exists())
    model = utils.load_model(p)
    print('loaded model type:', type(model))
except Exception as e:
    traceback.print_exc()
