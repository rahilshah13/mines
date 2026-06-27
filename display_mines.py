import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button
from matplotlib.animation import FuncAnimation

gdf = gpd.read_file("./mine_data/data/facilities.gpkg", layer='facilities').drop_duplicates(subset=['facility_name'])
gdf['lat'] = gdf.geometry.centroid.y
gdf['lon'] = gdf.geometry.centroid.x

def generate_reports(event):
    print("--- Starting report generation ---")
    with open("facility.txt", 'w') as f:
        for _, r in gdf.iterrows():
            commodity = r.get('primary_commodity', 'Unknown')
            line = f"{r['facility_name']} | Lat: {r['lat']:.6f}, Lon: {r['lon']:.6f} | {commodity}" if pd.notna(r['lat']) else f"{r['facility_name']} | No coordinates. | {commodity}"
            f.write(line + "\n")
    print("Successfully saved 'facility.txt'")
    
    avg_lat = gdf.groupby('primary_commodity')['lat'].mean()
    print("Average Latitude per Commodity:\n", avg_lat)
    fig_a, ax_a = plt.subplots(figsize=(8, 6))
    gdf['primary_commodity'].value_counts().plot(kind='bar', ax=ax_a, color='skyblue', edgecolor='black')
    ax_a.set_title("Commodities by Type"); ax_a.set_ylabel("Count")
    plt.tight_layout(); fig_a.savefig('mines_by_type.png')
    plt.close(fig_a)
    fig_b, ax_b = plt.subplots(figsize=(10, 6))
    gdf['lat_bin'] = pd.cut(gdf['lat'], bins=10)
    lat_comm = gdf.groupby(['lat_bin', 'primary_commodity']).size().unstack(fill_value=0)
    lat_comm.index = [f"{interval.left:.2f} to {interval.right:.2f}" for interval in lat_comm.index]
    lat_comm.plot(kind='bar', stacked=True, ax=ax_b)
    ax_b.set_title("Commodities by Latitude Bin"); ax_b.set_ylabel("Count")
    ax_b.set_xlabel("Latitude Range")
    plt.xticks(rotation=45, ha='right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(); fig_b.savefig('mines_by_latitude.png')
    plt.close(fig_b)
    print("--- All reports generated successfully ---")

fig, ax = plt.subplots(figsize=(10, 8)); plt.subplots_adjust(left=0.25)
filter_col = 'primary_commodity'
options = ['All'] + sorted(gdf[filter_col].dropna().unique())

def update(label):
    ax.clear()
    subset = gdf if label == 'All' else gdf[gdf[filter_col] == label]
    subset.plot(ax=ax, color='red' if label != 'All' else 'blue', edgecolor='black', alpha=0.7)
    ax.set_title(f"Facilities: {label}")
    plt.draw()

anim = None
def save_gif(event):
    global anim
    anim = FuncAnimation(fig, lambda i: update(options[i]), frames=len(options), interval=1000)
    anim.save('facilities.gif', writer='pillow')
    print("Saved 'facilities.gif'")

gdf.plot(ax=ax, color='blue', edgecolor='black', alpha=0.7)

rax = plt.axes([0.02, 0.4, 0.15, 0.3])
radio = RadioButtons(rax, options)
radio.on_clicked(update)

btn_gif_ax = plt.axes([0.02, 0.3, 0.15, 0.05])
btn_gif = Button(btn_gif_ax, 'Save GIF')
btn_gif.on_clicked(save_gif)

btn_rep_ax = plt.axes([0.02, 0.2, 0.15, 0.05])
btn_rep = Button(btn_rep_ax, 'Generate Reports')
btn_rep.on_clicked(generate_reports)

plt.show()