import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html
import matplotlib.pyplot as plt

#########
# Main Interactive Maps #
#########
top_consumption_countries = ['United States', 'China', 'Japan', 'Germany', 'United Kingdom']

top_waste_countries = ['China', 'United States', 'India', 'Italy', 'Germany']


cons_waste_coords = {
    'United States': [37.0902, -95.7129],
    'China': [35.8617, 104.1954],
    'Japan': [36.2048, 138.2529],
    'Germany': [51.1657, 10.4515],
    'United Kingdom': [55.3781, -3.4360],
    'India': [20.5937, 78.9629],
    'Brazil': [-14.2350, -51.9253],
    'Italy': [41.8719, 12.5674]
}

st.sidebar.title("Textile Industry Interactive Maps")

# Dropdown to choose map
map_choice = st.sidebar.selectbox(
    "Select map",
    ("Top Clothing Consumption", "Top Textile Waste Producers")
)

# Set which country list to use
if map_choice == "Top Clothing Consumption":
    relevant_countries = top_consumption_countries
else:
    relevant_countries = top_waste_countries

# Country selector based on selected map
country_choice = st.sidebar.selectbox(
    "Explore a country",
    relevant_countries
)

##### FOLIUM MAPS #####
m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')


for country in relevant_countries:
    folium.CircleMarker(
        location=cons_waste_coords[country],
        radius=8 if country == country_choice else 5, 
        color='red' if country == country_choice else 'blue',  
        fill=True,
        fill_opacity=1,
        tooltip=country
    ).add_to(m)

# Display map
st.subheader(f"{map_choice}")
col1, col2 = st.columns([3, 1])

with col1:
    st_folium(m, width=900, height=500)

with col2:
    if map_choice == "Top Clothing Consumption":
        st.info("""
        **Top 5 Countries**
        1. United States  
        2. China  
        3. Japan  
        4. Germany  
        5. United Kingdom
        """)
    
    elif map_choice == "Top Textile Waste Producers":
        st.info("""
        **Top 5 Countries**
        1. China  
        2. United States  
        3. India
        4. Italy  
        5. Germany
        """)

### Conditional Network Visualization (India textile shipments) ###
if map_choice == "Top Textile Waste Producers" and country_choice == "India":
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:lightgreen;">
        <h2><b>Explore More</b></h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### **India's Textile Shipments Network**")
    india_shipments_df = pd.read_csv('/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/India_Shipments.csv')

    country_coords = {
        'India': [20.5937, 78.9629],
        'United States': [37.0902, -95.7129],
        'Canada': [56.1304, -106.3468],
        'China': [35.8617, 104.1954],
        'South Korea': [35.9078, 127.7669],
        'Netherlands': [52.1326, 5.2913],
        'Slovenia': [46.1512, 14.9955],
        'Indonesia': [0.7893, 113.9213],
        'Colombia':[4.5709, -74.2973],
        'Ethiopia': [9.1450, 40.4897],
        'Japan': [36.2048, 138.2529],
        'Philippines': [12.8797, 121.7740],
        'Poland': [51.9194, 19.1451],
        'Dominican Republic': [18.7357, -70.1627],
        'Germany': [51.1657, 10.4515],
        'Taiwan': [23.6978, 120.9605],
        'Spain': [40.4637, -3.7492],
        'Saudi Arabia': [23.8859, 45.0792],
        'Brazil': [-14.2350, -51.9253],
    }

    m2 = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')

    india_lat, india_lon = country_coords['India']

    for idx, row in india_shipments_df.iterrows():
        destination = row['Destination']
        qty = row['Qty']

        # Check if destination exists in our coordinates dictionary
        if destination in country_coords:
            dest_lat, dest_lon = country_coords[destination]

            # Add destination marker
            folium.CircleMarker(
                location=[dest_lat, dest_lon],
                radius=4,
                color='green',
                fill=True,
                fill_opacity=1,
                #tooltip=f"{destination}: {qty}",
                popup=f"<b>{destination}</b><br>Quantity: {qty}"
            ).add_to(m2)

            # Add line from India to destination
            folium.PolyLine(
                locations=[
                    [india_lat, india_lon],
                    [dest_lat, dest_lon]
                ],
                color = 'lightblue',
                weight = 3,
                opacity = 0.4
            ).add_to(m2)

    folium.CircleMarker(
        location=[india_lat, india_lon],
        radius=4,
        color='Red',
        fill=True,
        fill_opacity=1,
        tooltip = 'India'
    ).add_to(m2)

    st_folium(m2, width=1000, height=600)

    st.markdown("""
    | Abbreviation | Meaning | Description |
    |:------------|:---------|:------------|
    | **kgs** | Kilograms | Weight measurement: 1 kg = 1,000 grams |
    | **mts** | Metric Tons | Weight measurement: 1 metric ton = 1,000 kilograms |
    | **pcs** | Pieces | Count of individual items or garments |
    | **unt** | Units | General count of goods |
    """)