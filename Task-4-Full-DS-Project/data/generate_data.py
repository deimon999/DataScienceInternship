"""
Generate synthetic house price dataset for training and testing.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse

def generate_house_price_dataset(n_samples: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic house price dataset.
    
    Args:
        n_samples: Number of samples to generate
        random_state: Random seed for reproducibility
        
    Returns:
        Generated dataset
    """
    np.random.seed(random_state)
    
    # Generate features
    square_feet = np.random.normal(2000, 800, n_samples).astype(int)
    square_feet = np.clip(square_feet, 500, 5000)
    
    bedrooms = np.random.choice([1, 2, 3, 4, 5, 6], n_samples, p=[0.05, 0.15, 0.35, 0.30, 0.12, 0.03])
    
    bathrooms = bedrooms * 0.75 + np.random.normal(0, 0.3, n_samples)
    bathrooms = np.clip(bathrooms, 1, 10)
    
    age = np.random.exponential(20, n_samples).astype(int)
    age = np.clip(age, 0, 100)
    
    garage = np.random.choice([0, 1, 2, 3, 4], n_samples, p=[0.05, 0.20, 0.50, 0.20, 0.05])
    
    location_score = np.random.normal(6.5, 1.5, n_samples)
    location_score = np.clip(location_score, 1, 10)
    
    condition_choices = ['excellent', 'good', 'fair', 'poor']
    condition = np.random.choice(condition_choices, n_samples, p=[0.20, 0.50, 0.25, 0.05])
    
    # Generate price based on features with realistic relationships
    base_price = 50000
    price = (base_price +
             square_feet * 100 +
             bedrooms * 30000 +
             bathrooms * 20000 +
             (-age * 200) +
             garage * 15000 +
             location_score * 20000)
    
    # Add condition adjustments
    condition_multiplier = {'excellent': 1.15, 'good': 1.0, 'fair': 0.85, 'poor': 0.7}
    price = price * np.array([condition_multiplier[c] for c in condition])
    
    # Add random noise
    price += np.random.normal(0, 50000, n_samples)
    price = np.clip(price, 50000, 500000)
    
    # Create dataframe
    df = pd.DataFrame({
        'square_feet': square_feet,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'age': age,
        'garage': garage,
        'location_score': location_score,
        'condition': condition,
        'Price': price.astype(int)
    })
    
    return df


def main():
    """Generate and save datasets."""
    parser = argparse.ArgumentParser(description='Generate house price dataset')
    parser.add_argument('--train-size', type=int, default=800, help='Number of training samples')
    parser.add_argument('--test-size', type=int, default=200, help='Number of test samples')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print("Generating house price dataset...")
    
    # Generate training data
    train_df = generate_house_price_dataset(args.train_size, args.seed)
    train_path = output_dir / 'train.csv'
    train_df.to_csv(train_path, index=False)
    print(f"Training data saved: {train_path} ({len(train_df)} samples)")
    
    # Generate test data
    test_df = generate_house_price_dataset(args.test_size, args.seed + 1)
    test_path = output_dir / 'test.csv'
    test_df.to_csv(test_path, index=False)
    print(f"Test data saved: {test_path} ({len(test_df)} samples)")
    
    # Print data summary
    print("\nDataset Summary:")
    print(f"Training set shape: {train_df.shape}")
    print(f"\nTraining set statistics:")
    print(train_df.describe())


if __name__ == "__main__":
    main()
