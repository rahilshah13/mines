import pandas as pd
import matplotlib.pyplot as plt
def generate_elevation_histogram(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            try:
                parts = [p.strip() for p in line.split('|')]
                elevation = float(parts[2].replace('m', '').strip())
                data.append({'elevation': elevation, 'commodity': 'Unknown'})
            except (IndexError, ValueError):
                continue
    df = pd.DataFrame(data)
    df['elev_bin'] = pd.cut(df['elevation'], bins=10)
    pivot = df.groupby(['elev_bin', 'commodity']).size().unstack(fill_value=0)
    pivot.index = [f"{i.left:.0f} to {i.right:.0f}" for i in pivot.index]
    fig, ax = plt.subplots(figsize=(12, 7))
    pivot.plot(kind='bar', stacked=True, ax=ax, edgecolor='black')
    ax.set_title("Mines by Elevation")
    ax.set_ylabel("Count")
    ax.set_xlabel("Elevation Range (meters)")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Commodity', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('mines_by_elevation.png')
    plt.show()

generate_elevation_histogram("elevation.txt")