import pandas as pd
from pathlib import Path

csv_path = Path("data/raw/capture_260301-182426_f32_v100.csv")
df = pd.read_csv(csv_path)

print("Unique channels:", sorted(df['ActiveChannel'].unique()))
print("\nChannel counts:")
print(df['ActiveChannel'].value_counts().sort_index())
