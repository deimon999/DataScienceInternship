import importlib
cfg = importlib.import_module('src.config')
print('MODEL_PATH:', cfg.MODEL_PATH)
print('PREPROCESSOR_PATH:', cfg.PREPROCESSOR_PATH)
