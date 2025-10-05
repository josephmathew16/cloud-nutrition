import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# --- Load dataset ---
df = pd.read_csv('../data/All_Diets.csv')
print("✅ Data loaded successfully!")
print(df.head())

# --- Clean missing values ---
df.fillna(df.mean(numeric_only=True), inplace=True)

# --- Average macronutrients by diet type ---
avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean().reset_index()
print("\nAverage macronutrients per diet type:")
print(avg_macros)

# --- Top 5 protein-rich recipes per diet type ---
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
print("\nTop 5 protein-rich recipes:")
print(top_protein[['Diet_type', 'Recipe_name', 'Protein(g)']])

# --- Add new metrics ---
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)']
df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)']

# --- Visualization (Save to analysis/outputs) ---
plt.figure(figsize=(10, 6))
sns.barplot(x='Diet_type', y='Protein(g)', data=avg_macros)
plt.title('Average Protein per Diet Type')
plt.xticks(rotation=45)
plt.tight_layout()
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
plt.savefig(f'outputs/avg_protein_{timestamp}.png')
plt.close()

print("✅ Visualization saved in analysis/outputs/")
