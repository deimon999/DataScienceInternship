"""
Model training and evaluation module.
Handles training of multiple models and model ensemble.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from typing import Tuple, Dict, Any

from .logger_setup import logger
from .config import (
    TEST_SIZE, RANDOM_STATE, N_JOBS,
    XGBOOST_PARAMS, LIGHTGBM_PARAMS, CATBOOST_PARAMS
)
from .utils import save_model, load_model, evaluate_prediction


class ModelTrainer:
    """
    Advanced model trainer with ensemble methods and hyperparameter tuning.
    """
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.model_history = []
        self.training_scores = {}
        logger.info("ModelTrainer initialized")
    
    def build_xgboost_model(self) -> xgb.XGBRegressor:
        """Build XGBoost model with optimized parameters."""
        logger.info("Building XGBoost model")
        params = dict(XGBOOST_PARAMS) if XGBOOST_PARAMS is not None else {}
        params.setdefault('random_state', RANDOM_STATE)
        return xgb.XGBRegressor(**params)
    
    def build_lightgbm_model(self) -> lgb.LGBMRegressor:
        """Build LightGBM model with optimized parameters."""
        logger.info("Building LightGBM model")
        params = dict(LIGHTGBM_PARAMS) if LIGHTGBM_PARAMS is not None else {}
        params.setdefault('random_state', RANDOM_STATE)
        return lgb.LGBMRegressor(**params)
    
    def build_catboost_model(self) -> CatBoostRegressor:
        """Build CatBoost model with optimized parameters."""
        logger.info("Building CatBoost model")
        return CatBoostRegressor(**CATBOOST_PARAMS)
    
    def build_random_forest_model(self) -> RandomForestRegressor:
        """Build Random Forest model."""
        logger.info("Building Random Forest model")
        return RandomForestRegressor(
            n_estimators=150,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=N_JOBS,
        )
    
    def build_gradient_boosting_model(self) -> GradientBoostingRegressor:
        """Build Gradient Boosting model."""
        logger.info("Building Gradient Boosting model")
        return GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=5,
            min_samples_split=5,
            subsample=0.8,
            random_state=RANDOM_STATE,
        )
    
    def train_models(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, float]:
        """
        Train multiple models and store them.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Dictionary of model names and cross-validation scores
        """
        logger.info("Starting multi-model training")
        
        models_to_train = {
            'xgboost': self.build_xgboost_model(),
            'lightgbm': self.build_lightgbm_model(),
            'catboost': self.build_catboost_model(),
            'random_forest': self.build_random_forest_model(),
            'gradient_boosting': self.build_gradient_boosting_model(),
        }
        
        cv_scores = {}
        
        for model_name, model in models_to_train.items():
            try:
                logger.info(f"Training {model_name}")
                
                # Train model
                model.fit(X_train, y_train)
                self.models[model_name] = model
                
                # Cross-validation score
                cv_score = cross_val_score(
                    model, X_train, y_train, 
                    cv=5, 
                    scoring='r2',
                    n_jobs=N_JOBS
                ).mean()
                
                cv_scores[model_name] = cv_score
                self.training_scores[model_name] = cv_score
                
                logger.info(f"{model_name} CV R² Score: {cv_score:.4f}")
                
                # Store history
                self.model_history.append({
                    'model': model_name,
                    'cv_score': cv_score,
                    'timestamp': pd.Timestamp.now(),
                })
            
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
        
        # Select best model
        self.best_model = max(self.models.items(), key=lambda x: cv_scores.get(x[0], 0))[1]
        best_model_name = max(self.models.items(), key=lambda x: cv_scores.get(x[0], 0))[0]
        
        logger.info(f"Best model selected: {best_model_name} with CV R² Score: {cv_scores[best_model_name]:.4f}")
        
        return cv_scores
    
    def evaluate_on_test_set(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all models on test set.
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary of model evaluation metrics
        """
        logger.info("Evaluating models on test set")
        
        evaluation_results = {}
        
        for model_name, model in self.models.items():
            try:
                y_pred = model.predict(X_test)
                metrics = evaluate_prediction(y_test.values, y_pred)
                evaluation_results[model_name] = metrics
                
                logger.info(f"{model_name} Test R² Score: {metrics['r2_score']:.4f}")
            
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {str(e)}")
        
        return evaluation_results
    
    def get_feature_importance(self, model_name: str = None, top_n: int = 20) -> Dict[str, float]:
        """
        Get feature importance from trained model.
        
        Args:
            model_name: Name of model to get importance from
            top_n: Number of top features to return
            
        Returns:
            Dictionary of feature names and importance scores
        """
        if model_name is None:
            model = self.best_model
        else:
            model = self.models.get(model_name)
        
        if model is None:
            logger.warning("No model available for feature importance")
            return {}
        
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            else:
                logger.warning(f"Model {type(model).__name__} doesn't have feature importances")
                return {}
            
            # Note: Feature names should be passed from preprocessing
            feature_names = [f"feature_{i}" for i in range(len(importances))]
            
            importance_dict = dict(zip(feature_names, importances))
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_features[:top_n])
        
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using best model.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if self.best_model is None:
            logger.error("No trained model available for prediction")
            raise ValueError("Model not trained. Call train_models() first.")
        
        try:
            predictions = self.best_model.predict(X)
            logger.info(f"Prediction successful for {len(X)} samples")
            return predictions
        
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def save_models(self, model_dir: str) -> None:
        """
        Save all trained models to disk.
        
        Args:
            model_dir: Directory to save models
        """
        logger.info("Saving all trained models")
        
        for model_name, model in self.models.items():
            try:
                model_path = f"{model_dir}/{model_name}_model.pkl"
                save_model(model, model_path)
            except Exception as e:
                logger.error(f"Error saving {model_name}: {str(e)}")
        
        if self.best_model:
            best_path = f"{model_dir}/best_model.pkl"
            save_model(self.best_model, best_path)
    
    def load_models(self, model_dir: str) -> None:
        """
        Load trained models from disk.
        
        Args:
            model_dir: Directory containing saved models
        """
        logger.info("Loading trained models")
        
        try:
            best_model_path = f"{model_dir}/best_model.pkl"
            self.best_model = load_model(best_model_path)
            logger.info("Best model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading best model: {str(e)}")
    
    def get_model_comparison(self) -> pd.DataFrame:
        """
        Get comparison of all trained models.
        
        Returns:
            DataFrame with model comparison metrics
        """
        if not self.model_history:
            logger.warning("No model history available")
            return pd.DataFrame()
        
        comparison_df = pd.DataFrame(self.model_history)
        return comparison_df.sort_values('cv_score', ascending=False)
