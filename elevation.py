import os
import math

DATA_FILE = "facility.txt"
CHUNKS_DIR = "chunks"
# 11km in meters for comparison with Haversine (which returns meters)
MAX_DISTANCE_METERS = 110000 

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance in meters between two points."""
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_closest_elevation(lat, lon):
    lat_int = int(round(lat))
    file_path = f"{CHUNKS_DIR}/lat_{lat_int}.pl"
    if not os.path.exists(file_path): return None
    
    best_dist = float('inf')
    best_z = None
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('z('):
                try:
                    parts = line.replace('z(', '').replace(').', '').split(',')
                    p_lat, p_lon, p_z = float(parts[0]), float(parts[1]), float(parts[2])                    
                    dist = haversine_distance(lat, lon, p_lat, p_lon)
                    if dist < best_dist:
                        best_dist = dist
                        best_z = p_z
                except: continue

    return best_z if best_dist <= MAX_DISTANCE_METERS else None 

with open(DATA_FILE, 'r') as f_in, open("elevation.txt", 'w') as f_out:
    for line in f_in:
        # Expected format: Name | Lat: A, Lon: B | Commodity
        if "Lat:" in line and "Lon:" in line:
            try:
                parts = [p.strip() for p in line.split('|')]
                coords = parts[1].split(',')
                lat = float(coords[0].split(':')[1])
                lon = float(coords[1].split(':')[1])
                elev = get_closest_elevation(lat, lon)
                elev_str = f"{elev}m" if elev is not None else "No data nearby"
                out_line = f"{parts[0]} | {parts[1]} | {parts[2]} | {elev_str}"
                print(out_line)
                f_out.write(out_line + "\n")
            except Exception as e:
                print(f"Error parsing line: {line.strip()} | {e}")