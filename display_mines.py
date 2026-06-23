import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from matplotlib.animation import FuncAnimation
import fiona

gpkg_path = "./mine_data/data/facilities.gpkg"
gdf = gpd.read_file(gpkg_path, layer='facilities') 

# --- Print Facility Coordinates ---
def get_lat(geom):
    if geom is None or geom.is_empty: return None
    if hasattr(geom, 'geoms'): return geom.geoms[0].y if len(geom.geoms) > 0 else None
    return geom.y

def get_lon(geom):
    if geom is None or geom.is_empty: return None
    if hasattr(geom, 'geoms'): return geom.geoms[0].x if len(geom.geoms) > 0 else None
    return geom.x

lats = gdf.geometry.apply(get_lat)
lons = gdf.geometry.apply(get_lon)

for name, lat, lon in zip(gdf['facility_name'], lats, lons):
    if lat is not None and lon is not None:
        print(f"Facility: {name} | Lat: {lat:.6f}, Lon: {lon:.6f}")
    else:
        print(f"Facility: {name} | No valid coordinates found.")


# --- Setup Plot ---
filter_col = 'primary_commodity' 
unique_values = sorted([val for val in gdf[filter_col].unique() if val is not None])
options = ['All'] + unique_values
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.25)

def update(label):
    ax.clear()
    if label == 'All':
        gdf.plot(ax=ax, color='blue', edgecolor='black', alpha=0.7)
    else:
        gdf[gdf[filter_col] == label].plot(ax=ax, color='red', edgecolor='black', alpha=0.7)
    ax.set_title(f"Facilities producing: {label}")
    plt.draw()

# Initial plot
gdf.plot(ax=ax, color='blue', edgecolor='black', alpha=0.7)

# --- Button Logic ---
ax_radio = plt.axes([0.02, 0.4, 0.15, 0.3], facecolor='#f0f0f0')
radio = RadioButtons(ax_radio, options)
radio.on_clicked(update)

# --- GIF Export Function ---
def save_gif(event):
    print("Generating GIF...")
    def animate(i):
        update(options[i])
    anim = FuncAnimation(fig, animate, frames=len(options), interval=1000)
    anim.save('facilities.gif', writer='pillow')
    print("Saved as 'facilities.gif'")

ax_button = plt.axes([0.02, 0.3, 0.15, 0.05])
from matplotlib.widgets import Button
btn = Button(ax_button, 'Save GIF')
btn.on_clicked(save_gif)
plt.show()