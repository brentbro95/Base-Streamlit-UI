from pathlib import Path

import pandas as pd
from sklearn.datasets import make_classification


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=6,
        n_redundant=2,
        n_classes=2,
        random_state=42,
    )

    columns = [f"feature_{i}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=columns)
    df["target"] = y

    output_path = data_dir / "train.csv"
    df.to_csv(output_path, index=False)
    print(f"Sample dataset saved to: {output_path}")


if __name__ == "__main__":
    main()
