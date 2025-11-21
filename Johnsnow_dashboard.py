import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from branca.element import Template, MacroElement
from streamlit_folium import st_folium

# ------------------------------
# 1. STREAMLIT PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="Cholera Death Map", layout="wide")
st.title("Cholera Death Dashboard")

# ------------------------------
# 2. LOAD DATA (CSV must have 'latitude' and 'longitude' columns)
# ------------------------------
df_deaths = pd.read_csv("Cholera_Deaths.csv")
df_pumps = pd.read_csv("Pumps.csv")

# ---- RENAME COLUMNS to match expected names ----
df_deaths = df_deaths.rename(columns={'X': 'longitude', 'Y': 'latitude'})
df_pumps = df_pumps.rename(columns={'X': 'longitude', 'Y': 'latitude'})
# ------------------------------

# -----------------------------------------
# 3. REPROJECT FROM EPSG:27700 → EPSG:4326
# -----------------------------------------
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

def reproject(df):
    lons = []
    lats = []
    for x, y in zip(df["X"], df["Y"]):
        lon, lat = transformer.transform(x, y)
        lons.append(lon)
        lats.append(lat)
    df["lon"] = lons
    df["lat"] = lats
    return df

pd_deaths = reproject(pd_deaths)
pd_pumps = reproject(pd_pumps)

# 3. CREATE BASE MAP
# ------------------------------
center_lat = df_deaths['latitude'].mean()
center_lon = df_deaths['longitude'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=16)

# ------------------------------
# 4. ADD CHOLERA DEATHS
# ------------------------------
deaths_layer = folium.FeatureGroup(name="Cholera Deaths")
for _, row in df_deaths.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.8
    ).add_to(deaths_layer)
deaths_layer.add_to(m)

# ------------------------------
# 5. ADD WATER PUMPS (Font Awesome tint)
# ------------------------------
pumps_layer = folium.FeatureGroup(name="Water Pumps")
for _, row in df_pumps.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup="Water Pump",
        icon=folium.Icon(color="blue", icon="tint", prefix="fa")
    ).add_to(pumps_layer)
pumps_layer.add_to(m)

# ------------------------------
# 6. ADD LAYER CONTROL
# ------------------------------
folium.LayerControl().add_to(m)

# ------------------------------
# 7. ADD TITLE AND LEGEND
# ------------------------------
template = """
{% macro html(this, kwargs) %}

<!-- TITLE -->
<div style="
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index:9999;
    background-color:white;
    padding:10px;
    border:2px solid grey;
    border-radius:5px;
    font-size:16px;
    font-weight:bold;
    ">
    CHOLERA DEATH MAP
</div>

<!-- LEGEND -->
<div style="
    position: fixed;
    bottom: 50px;
    left: 10px;
    z-index:9999;
    background-color:white;
    padding:10px;
    border:2px solid grey;
    border-radius:5px;
    font-size:14px;
    ">
    <i class="fa fa-circle" style="color:red;"></i> Cholera Deaths<br>
    <i class="fa fa-tint" style="color:blue;"></i> Water Pumps
</div>

{% endmacro %}
"""

macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)

# ------------------------------
# 8. DISPLAY MAP IN STREAMLIT
# ------------------------------
st.subheader("Interactive Cholera Map")

st_folium(m, width=1000, height=600)





