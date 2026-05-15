import importlib
utils = importlib.import_module('src.utils')
from pathlib import Path
p = Path('models/preprocessor.pkl')
print('exists', p.exists())
try:
    pre = utils.load_model(p)
    print('loaded preprocessor type', type(pre))
except Exception as e:
    print('error', e)
