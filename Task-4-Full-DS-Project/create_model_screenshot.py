import pickle
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
BEST_MODEL_PATH = os.path.join(MODELS_DIR, 'best_model.pkl')
PREPROC_PATH = os.path.join(MODELS_DIR, 'preprocessor.pkl')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'Presentation-and-Documentation', 'model_importance.png')

# Load model
with open(BEST_MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Try to load preprocessor for feature names
feature_names = None
if os.path.exists(PREPROC_PATH):
    try:
        with open(PREPROC_PATH, 'rb') as f:
            pre = pickle.load(f)
        # common attribute in sklearn transformers
        if hasattr(pre, 'feature_names_in_'):
            feature_names = list(pre.feature_names_in_)
        elif hasattr(pre, 'get_feature_names_out'):
            try:
                feature_names = list(pre.get_feature_names_out())
            except Exception:
                feature_names = None
    except Exception:
        feature_names = None

# Get importances
importances = None
if hasattr(model, 'feature_importances_'):
    importances = model.feature_importances_
elif hasattr(model, 'coef_'):
    importances = abs(model.coef_).ravel()
else:
    raise SystemExit('Model does not expose feature importances')

# Align feature names
if feature_names is None or len(feature_names) != len(importances):
    feature_names = [f'feature_{i}' for i in range(len(importances))]

# Plot top 10
indices = importances.argsort()[::-1][:10]
names = [feature_names[i] for i in indices]
vals = importances[indices]

plt.figure(figsize=(8,6))
plt.barh(range(len(names))[::-1], vals[::-1], color='C0')
plt.yticks(range(len(names))[::-1], names)
plt.xlabel('Importance')
plt.title('Top 10 Feature Importances (best_model)')
plt.tight_layout()

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
plt.savefig(OUT_PATH, dpi=150)
print('saved', OUT_PATH)
