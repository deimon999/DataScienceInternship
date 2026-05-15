import importlib, traceback
try:
    api = importlib.import_module('src.api')
    print('api module loaded')
    api.load_models()
    print('models:', api.model, api.preprocessor)
except Exception:
    traceback.print_exc()
