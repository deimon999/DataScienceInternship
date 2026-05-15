"""
Training entrypoint inside the `src` package. Mirrors top-level `train.py` but uses package-relative imports.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse

from .logger_setup import logger
from .config import TEST_SIZE, RANDOM_STATE, MODEL_DIR, TRAIN_DATA_PATH
from .data_pipeline import AdvancedPreprocessor
from .model_training import ModelTrainer
from .utils import save_model, evaluate_prediction


def load_data(train_path: Path = TRAIN_DATA_PATH, test_path: Path = None) -> tuple:
    logger.info(f"Loading data from {train_path}")
    train_df = pd.read_csv(train_path)
    logger.info(f"Training data loaded: {train_df.shape}")

    if test_path and Path(test_path).exists():
        test_df = pd.read_csv(test_path)
        logger.info(f"Test data loaded: {test_df.shape}")
        X_test = test_df.drop('Price', axis=1)
        y_test = test_df['Price']
    else:
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(
            train_df,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
        logger.info(f"Data split: train {train_df.shape}, test {test_df.shape}")
        X_test = test_df.drop('Price', axis=1)
        y_test = test_df['Price']

    X_train = train_df.drop('Price', axis=1)
    y_train = train_df['Price']

    return X_train, y_train, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description='Train house price prediction model')
    parser.add_argument('--train-path', type=str, default=None, help='Path to training data')
    parser.add_argument('--test-path', type=str, default=None, help='Path to test data')
    parser.add_argument('--model-dir', type=str, default=None, help='Directory to save models')
    args = parser.parse_args()

    train_path = Path(args.train_path) if args.train_path else TRAIN_DATA_PATH
    test_path = Path(args.test_path) if args.test_path else None
    model_dir = Path(args.model_dir) if args.model_dir else MODEL_DIR

    logger.info("=" * 80)
    logger.info("HOUSE PRICE PREDICTION - TRAINING PIPELINE")
    logger.info("=" * 80)

    try:
        logger.info("\n[STEP 1] Loading data...")
        X_train, y_train, X_test, y_test = load_data(train_path, test_path)

        logger.info("\n[STEP 2] Preprocessing data...")
        preprocessor = AdvancedPreprocessor()
        X_train_processed, y_train_processed, preprocess_info = preprocessor.fit_transform(
            pd.concat([X_train, y_train], axis=1),
            target_column='Price'
        )

        X_test_processed = preprocessor.transform(X_test)
        logger.info(f"Preprocessing info: {preprocess_info}")

        logger.info("\n[STEP 3] Training multiple models...")
        trainer = ModelTrainer()
        cv_scores = trainer.train_models(X_train_processed, y_train_processed)

        logger.info("\nCross-validation scores:")
        for model_name, score in sorted(cv_scores.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {model_name}: {score:.4f}")

        logger.info("\n[STEP 4] Evaluating on test set...")
        evaluation_results = trainer.evaluate_on_test_set(X_test_processed, y_test)

        logger.info("\nTest set evaluation:")
        for model_name, metrics in evaluation_results.items():
            logger.info(f"  {model_name}:")
            logger.info(f"    R² Score: {metrics['r2_score']:.4f}")
            logger.info(f"    RMSE: ${metrics['rmse']:.2f}")
            logger.info(f"    MAE: ${metrics['mae']:.2f}")

        logger.info("\n[STEP 5] Saving models and preprocessor...")
        model_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_models(str(model_dir))
        save_model(preprocessor, model_dir / 'preprocessor.pkl')
        logger.info(f"Models saved to {model_dir}")

        logger.info("\n[STEP 6] Generating predictions...")
        y_pred = trainer.predict(X_test_processed)
        test_metrics = evaluate_prediction(y_test.values, y_pred)

        logger.info("\nBest model performance:")
        logger.info(f"  R² Score: {test_metrics['r2_score']:.4f}")
        logger.info(f"  RMSE: ${test_metrics['rmse']:.2f}")
        logger.info(f"  MAE: ${test_metrics['mae']:.2f}")
        logger.info(f"  MAPE: {test_metrics['mape']:.2f}%")

        logger.info("\n[STEP 7] Feature importance analysis...")
        importance = trainer.get_feature_importance(top_n=10)
        if importance:
            logger.info("Top 10 important features:")
            for feature, score in importance.items():
                logger.info(f"  {feature}: {score:.4f}")

        logger.info("\n" + "=" * 80)
        logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)

        return {
            "status": "success",
            "best_model": type(trainer.best_model).__name__,
            "test_r2_score": test_metrics['r2_score'],
            "test_rmse": test_metrics['rmse'],
        }

    except Exception as e:
        logger.error(f"\n{'='*80}")
        logger.error(f"ERROR IN TRAINING PIPELINE: {str(e)}")
        logger.error("="*80)
        raise


if __name__ == "__main__":
    main()
