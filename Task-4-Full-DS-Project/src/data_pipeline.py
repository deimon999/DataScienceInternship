"""
Advanced data preprocessing and feature engineering pipeline.
Handles data cleaning, transformation, and feature creation.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression
from typing import Tuple, List, Dict, Any, Union
from pathlib import Path

from .logger_setup import logger
from .config import (
    FEATURE_SCALING, MISSING_VALUE_STRATEGY, 
    USE_FEATURE_SELECTION, N_FEATURES_TO_SELECT,
    RANDOM_STATE
)


class AdvancedPreprocessor:
    """
    Advanced data preprocessing pipeline with feature engineering.
    """
    
    def __init__(self):
        self.scaler = None
        self.categorical_encoder = None
        self.numeric_imputer = None
        self.categorical_imputer = None
        self.feature_selector = None
        self.feature_names = None
        self.numeric_features = None
        self.categorical_features = None
        logger.info("AdvancedPreprocessor initialized")
    
    def identify_feature_types(self, data: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Identify numeric and categorical features.
        
        Args:
            data: Input dataframe
            
        Returns:
            Tuple of (numeric_features, categorical_features)
        """
        numeric_features = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        logger.info(f"Identified {len(numeric_features)} numeric and {len(categorical_features)} categorical features")
        
        return numeric_features, categorical_features
    
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values with advanced strategies.
        
        Args:
            data: Input dataframe with potential missing values
            
        Returns:
            Dataframe with missing values handled
        """
        data = data.copy()
        
        # Log missing values
        missing_stats = data.isnull().sum()
        if missing_stats.sum() > 0:
            logger.info(f"Found {missing_stats.sum()} missing values")
            logger.debug(f"Missing values: {missing_stats[missing_stats > 0].to_dict()}")
        
        # Numeric features
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if data[col].isnull().any():
                if MISSING_VALUE_STRATEGY == "median":
                    data[col].fillna(data[col].median(), inplace=True)
                elif MISSING_VALUE_STRATEGY == "mean":
                    data[col].fillna(data[col].mean(), inplace=True)
                else:
                    data[col].fillna(0, inplace=True)
        
        # Categorical features
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if data[col].isnull().any():
                data[col].fillna(data[col].mode()[0] if len(data[col].mode()) > 0 else "Unknown", inplace=True)
        
        logger.info("Missing values handled successfully")
        return data
    
    def detect_and_handle_outliers(self, data: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        """
        Detect and handle outliers using IQR or statistical methods.
        
        Args:
            data: Input dataframe
            method: Outlier detection method ("iqr" or "zscore")
            
        Returns:
            Dataframe with outliers handled
        """
        data = data.copy()
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == "iqr":
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
                if outliers > 0:
                    logger.info(f"Found {outliers} outliers in {col}, capping values")
                    data[col] = data[col].clip(lower_bound, upper_bound)
        
        return data
    
    def create_advanced_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features through polynomial and interaction features.
        
        Args:
            data: Input dataframe
            
        Returns:
            Dataframe with engineered features
        """
        data = data.copy()
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target variable from feature engineering if present
        if 'Price' in numeric_cols:
            numeric_cols.remove('Price')
        
        # Create polynomial features for top features
        top_features = numeric_cols[:3]  # Only for top 3 features
        for feature in top_features:
            if feature in data.columns:
                data[f'{feature}_squared'] = data[feature] ** 2
                data[f'{feature}_sqrt'] = np.sqrt(np.abs(data[feature]))
        
        # Create interaction features
        if len(top_features) >= 2:
            for i in range(len(top_features) - 1):
                if top_features[i] in data.columns and top_features[i+1] in data.columns:
                    data[f'{top_features[i]}_x_{top_features[i+1]}'] = (
                        data[top_features[i]] * data[top_features[i+1]]
                    )
        
        logger.info(f"Created {len(data.columns)} features through feature engineering")
        return data
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """
        Scale numeric features using configured scaler.
        
        Args:
            X: Input features
            fit: Whether to fit the scaler (True for training, False for inference)
            
        Returns:
            Scaled feature array
        """
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_features:
            logger.warning("No numeric features to scale")
            return X.values
        
        # Choose scaler class based on configuration
        if FEATURE_SCALING == "standard":
            ScalerClass = StandardScaler
        elif FEATURE_SCALING == "robust":
            ScalerClass = RobustScaler
        elif FEATURE_SCALING == "minmax":
            ScalerClass = MinMaxScaler
        else:
            ScalerClass = StandardScaler

        # Fit or reuse existing scaler
        if fit:
            self.scaler = ScalerClass()
            X_scaled = self.scaler.fit_transform(X[numeric_features])
        else:
            if self.scaler is None:
                # Fallback: if scaler wasn't fitted, fit on provided data and warn
                logger.warning("Scaler not fitted - fitting on transform input as fallback")
                self.scaler = ScalerClass()
                X_scaled = self.scaler.fit_transform(X[numeric_features])
            else:
                X_scaled = self.scaler.transform(X[numeric_features])
        
        # Create result dataframe
        result = X.copy()
        result[numeric_features] = X_scaled
        
        logger.info(f"Features scaled using {FEATURE_SCALING} scaler")
        return result
    
    def perform_feature_selection(self, X: pd.DataFrame, y: pd.Series, fit: bool = True) -> pd.DataFrame:
        """
        Perform feature selection to reduce dimensionality.
        
        Args:
            X: Input features
            y: Target variable
            fit: Whether to fit the selector (True for training, False for inference)
            
        Returns:
            Dataframe with selected features
        """
        if not USE_FEATURE_SELECTION or X.shape[1] <= N_FEATURES_TO_SELECT:
            return X
        
        try:
            if fit:
                self.feature_selector = SelectKBest(f_regression, k=N_FEATURES_TO_SELECT)
                X_selected = self.feature_selector.fit_transform(X, y)
            else:
                X_selected = self.feature_selector.transform(X)
            
            selected_features = X.columns[self.feature_selector.get_support()].tolist()
            logger.info(f"Selected {len(selected_features)} features from {X.shape[1]}")
            logger.debug(f"Selected features: {selected_features}")
            
            return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        except Exception as e:
            logger.warning(f"Feature selection failed: {str(e)}. Using all features.")
            return X
    
    def fit_transform(self, data: pd.DataFrame, target_column: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fit and transform data through complete preprocessing pipeline.
        
        Args:
            data: Input dataframe
            target_column: Name of target column
            
        Returns:
            Tuple of (processed_data, processing_info)
        """
        logger.info("Starting data preprocessing pipeline")
        
        data = data.copy()
        
        # Step 1: Identify feature types
        self.numeric_features, self.categorical_features = self.identify_feature_types(data)
        
        # Step 2: Handle missing values
        data = self.handle_missing_values(data)
        
        # Step 3: Detect and handle outliers
        data = self.detect_and_handle_outliers(data)
        
        # Step 4: Create advanced features
        data = self.create_advanced_features(data)
        
        # Separate features and target
        if target_column and target_column in data.columns:
            X = data.drop(columns=[target_column])
            y = data[target_column]
        else:
            X = data
            y = None
        
        # Step 5: Scale features
        # Encode simple categorical features to numeric (ordinal) if present
        if 'condition' in X.columns and not pd.api.types.is_numeric_dtype(X['condition']):
            cond_map = {'poor': 0.0, 'fair': 1.0, 'good': 2.0, 'excellent': 3.0}
            X['condition'] = X['condition'].astype(str).map(cond_map).astype(float)

        X = self.scale_features(X, fit=True)
        
        # Step 6: Feature selection (if target available)
        if y is not None:
            X = self.perform_feature_selection(X, y, fit=True)
        
        self.feature_names = X.columns.tolist()
        
        processing_info = {
            "original_shape": data.shape,
            "final_shape": X.shape,
            "numeric_features": len(self.numeric_features),
            "categorical_features": len(self.categorical_features),
            "feature_names": self.feature_names,
        }
        
        logger.info(f"Preprocessing completed: {processing_info}")
        
        if y is not None:
            return X, y, processing_info
        else:
            return X, processing_info
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted preprocessing pipeline.
        
        Args:
            data: Input dataframe
            
        Returns:
            Transformed dataframe
        """
        logger.info("Transforming new data with fitted preprocessor")
        
        data = data.copy()
        
        # Apply same transformations as fitting
        data = self.handle_missing_values(data)
        data = self.detect_and_handle_outliers(data)
        data = self.create_advanced_features(data)
        
        # Scale features
        # Encode categorical features same as in fit
        if 'condition' in data.columns and not pd.api.types.is_numeric_dtype(data['condition']):
            cond_map = {'poor': 0.0, 'fair': 1.0, 'good': 2.0, 'excellent': 3.0}
            data['condition'] = data['condition'].astype(str).map(cond_map).astype(float)

        data = self.scale_features(data, fit=False)
        
        # Feature selection
        if self.feature_selector is not None:
            data = self.perform_feature_selection(data, y=None, fit=False)
        
        # Ensure feature names match
        if self.feature_names:
            missing_features = set(self.feature_names) - set(data.columns)
            if missing_features:
                logger.warning(f"Missing features in transform: {missing_features}")
                for feature in missing_features:
                    data[feature] = 0
            
            data = data[self.feature_names]
        
        logger.info(f"Data transformed successfully to shape {data.shape}")
        return data
