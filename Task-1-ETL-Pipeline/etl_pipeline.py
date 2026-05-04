import argparse
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def run_pipeline(input_csv: Path, output_csv: Path) -> None:
    df = pd.read_csv(input_csv)

    df = df.drop_duplicates()

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
    )

    transformed = preprocessor.fit_transform(df)
    feature_names = preprocessor.get_feature_names_out()
    transformed_df = pd.DataFrame(transformed, columns=feature_names)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    transformed_df.to_csv(output_csv, index=False)

    print(f"Input rows: {len(df)}")
    print(f"Output shape: {transformed_df.shape}")
    print(f"Saved transformed data to: {output_csv}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ETL pipeline for data preprocessing, transformation, and loading."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", default="output/transformed_data.csv", help="Path to output CSV file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(Path(args.input), Path(args.output))
