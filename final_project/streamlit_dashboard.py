import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat&display=swap" rel="stylesheet">
<style>
/* Apply Montserrat font across everything */
html, body, div, p, span, input, label, textarea, select, button, h1, h2, h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


st.title("Textile Industry Interactive Maps")
tab1, tab2, tab3 = st.tabs(["Home", "About", "Contact"])

with tab1:
    st.write("Welcome to the main Textile Industry dashboard.")
    # (Here you put your map visualizations code!)

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
            color='#A3C9A8' if country == country_choice else '#8ECAE6',  
            fill=True,
            fill_opacity=1,
            tooltip=country
        ).add_to(m)

    # Display map
    st.subheader(f"{map_choice}")

    st_folium(m, use_container_width=True, height=700)

    if map_choice == "Top Clothing Consumption":
        st.sidebar.info("""
        **Top 5 Countries**
        1. United States  
        2. China  
        3. Japan  
        4. Germany  
        5. United Kingdom
        """)
    
    elif map_choice == "Top Textile Waste Producers":
        st.sidebar.info("""
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
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore India</b></h2>
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
                    color='#A3C9A8',
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
                    color = '#FFE5B4',
                    weight = 3,
                    opacity = 0.4
                ).add_to(m2)

        folium.CircleMarker(
            location=[india_lat, india_lon],
            radius=4,
            color='#6C7A89',
            fill=True,
            fill_opacity=1,
            tooltip = 'India'
        ).add_to(m2)

        st_folium(m2, width=1200, height=600)

        st.markdown("""
        | Abbreviation | Meaning | Description |
        |:------------|:---------|:------------|
        | **kgs** | Kilograms | Weight measurement: 1 kg = 1,000 grams |
        | **mts** | Metric Tons | Weight measurement: 1 metric ton = 1,000 kilograms |
        | **pcs** | Pieces | Count of individual items or garments |
        | **unt** | Units | General count of goods |
        """)

    ### Conditional Network Visualization (Top Consumption: US) ###
    if map_choice == "Top Clothing Consumption" and country_choice == "United States":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore United States</b></h2>
        </div>
        """, unsafe_allow_html=True)

        US_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/US.csv'
        df = pd.read_csv(US_google, encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Thrift']

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#B0A8B9',        
            'Thrift': '#A3C9A8'   
        }
        bg_color = '#f5f6fa'
        plot_bg_color = '#e1e2e6'

        fig = go.Figure()

        for i, search_type in enumerate(search_types):
            df_type = df[df['Search_Type'] == search_type]
            for j, keyword in enumerate(keyword_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df_type['Date'],
                        y=df_type[keyword],
                        mode='lines+markers',
                        name=keyword,
                        line=dict(color=line_colors[keyword], width=3),
                        visible=False
                    )
                )

        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines+markers',
                    name=keyword,
                    line=dict(color=line_colors[keyword], width=3),
                    visible=True  
                )
            )

        buttons = []

        visible_total = [False] * (len(search_types) * len(keyword_cols)) + [True] * len(keyword_cols)
        buttons.append(
            dict(
                label='Total Google Search', 
                method='update',
                args=[{'visible': visible_total}]
            )
        )

        for i, search_type in enumerate(search_types):
            visible = [False] * (len(search_types) * len(keyword_cols) + len(keyword_cols))
            for j in range(len(keyword_cols)):
                idx = i * len(keyword_cols) + j
                visible[idx] = True
            buttons.append(
                dict(
                    label=search_type,
                    method='update',
                    args=[{'visible': visible}]
                )
            )

        fig.update_layout(
            title=dict(
                text="Consumer Google Search Trends",
                x=0.5,
                xanchor='center',
                font=dict(
                    family='Montserrat',
                    size=20,     
                    color='#474b4f'   
                )
            ),
            updatemenus=[dict(
                type='dropdown',
                direction='down',
                x=2,
                y=1.05,
                showactive=True,
                buttons=buttons,
                bgcolor='#F8F9FA',
                bordercolor='#8ECAE6',
                font=dict(color='#8ECAE6', size=14),
            )],
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,              
                gridcolor='#F8F9FA',           
                zeroline=False
            ), 
            yaxis=dict(
                title=dict(
                    text='Search Interest',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                showline=True,
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,
                gridcolor='#F8F9FA',
                zeroline=False
            ),
            legend=dict(
                title=dict(
                    text=f'Keyword',
                    font=dict(
                        family='Montserrat', 
                        color='#474b4f', 
                        size=15
                    )
                ),
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat', color='#474b4f', size=13)
            ),
            font=dict(family='Montserrat', color='#474b4f', size=15),
            paper_bgcolor=bg_color,
            plot_bgcolor=plot_bg_color,
            margin=dict(l=60, r=200, t=80, b=60)
        )
        st.plotly_chart(fig, use_container_width=True)


    ### Conditional Network Visualization (Top Consumption: Germany) ###
    if map_choice == "Top Clothing Consumption" and country_choice == "Germany":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore Germany</b></h2>
        </div>
        """, unsafe_allow_html=True)

        germany_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/Germany.csv'
        df = pd.read_csv(germany_google, encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Flohmarkt'] 

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#B0A8B9',         
            'Flohmarkt': '#A3C9A8'  
        }
        bg_color = '#f5f6fa'
        plot_bg_color = '#e1e2e6'

        fig = go.Figure()

        for i, search_type in enumerate(search_types):
            df_type = df[df['Search_Type'] == search_type]
            for j, keyword in enumerate(keyword_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df_type['Date'],
                        y=df_type[keyword],
                        mode='lines+markers',
                        name=keyword,
                        line=dict(color=line_colors[keyword], width=3),
                        visible=False  
                    )
                )

        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines+markers',
                    name=keyword,
                    line=dict(color=line_colors[keyword], width=3),
                    visible=True  
                )
            )

        buttons = []

        visible_total = [False] * (len(search_types) * len(keyword_cols)) + [True] * len(keyword_cols)
        buttons.append(
            dict(
                label='Total Google Search',
                method='update',
                args=[{'visible': visible_total}]
            )
        )

        for i, search_type in enumerate(search_types):
            visible = [False] * (len(search_types) * len(keyword_cols) + len(keyword_cols))
            for j in range(len(keyword_cols)):
                idx = i * len(keyword_cols) + j
                visible[idx] = True
            buttons.append(
                dict(
                    label=search_type,
                    method='update',
                    args=[{'visible': visible}]
                )
            )

        fig.update_layout(
            title=dict(
                text="Consumer Google Search Trends",
                x=0.5,
                xanchor='center',
                font=dict(
                    family='Montserrat',
                    size=20,     
                    color='#474b4f'   
                )
            ),
            updatemenus=[dict(
                type='dropdown',
                direction='down',
                x=2,
                y=1.05,
                showactive=True,
                buttons=buttons,
                bgcolor='#F8F9FA',
                bordercolor='#8ECAE6',
                font=dict(color='#8ECAE6', size=14),
            )],
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,              
                gridcolor='#F8F9FA',           
                zeroline=False
            ), 
            yaxis=dict(
                title=dict(
                    text='Search Interest',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                showline=True,
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,
                gridcolor='#F8F9FA',
                zeroline=False
            ),
            legend=dict(
                title=dict(
                    text=f'Keyword',
                    font=dict(
                        family='Montserrat', 
                        color='#474b4f', 
                        size=15
                    )
                ),
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat', color='#474b4f', size=13)
            ),
            font=dict(family='Montserrat', color='#474b4f', size=15),
            paper_bgcolor=bg_color,
            plot_bgcolor=plot_bg_color,
            margin=dict(l=60, r=200, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)


        ### Conditional Network Visualization (Top Consumption: Japan) ###
    if map_choice == "Top Clothing Consumption" and country_choice == "Japan":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore Japan</b></h2>
        </div>
        """, unsafe_allow_html=True)

        japan_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/Japan.csv'
        df = pd.read_csv(japan_google, encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Thrift']  # Keywords for Japan: シーイン is Shein and 古着 is Thrift

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#B0A8B9',         
            'Thrift': '#A3C9A8'  
        }
        bg_color = '#f5f6fa'
        plot_bg_color = '#e1e2e6'

        fig = go.Figure()

        for i, search_type in enumerate(search_types):
            df_type = df[df['Search_Type'] == search_type]
            for j, keyword in enumerate(keyword_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df_type['Date'],
                        y=df_type[keyword],
                        mode='lines+markers',
                        name=keyword,
                        line=dict(color=line_colors[keyword], width=3),
                        visible=False  
                    )
                )

        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines+markers',
                    name=keyword,
                    line=dict(color=line_colors[keyword], width=3),
                    visible=True  
                )
            )

        buttons = []

        visible_total = [False] * (len(search_types) * len(keyword_cols)) + [True] * len(keyword_cols)
        buttons.append(
            dict(
                label='Total Google Search',
                method='update',
                args=[{'visible': visible_total}]
            )
        )

        for i, search_type in enumerate(search_types):
            visible = [False] * (len(search_types) * len(keyword_cols) + len(keyword_cols))
            for j in range(len(keyword_cols)):
                idx = i * len(keyword_cols) + j
                visible[idx] = True
            buttons.append(
                dict(
                    label=search_type,
                    method='update',
                    args=[{'visible': visible}]
                )
            )

        fig.update_layout(
            title=dict(
                text="Consumer Google Search Trends",
                x=0.5,
                xanchor='center',
                font=dict(
                    family='Montserrat',
                    size=20,     
                    color='#474b4f'   
                )
            ),
            updatemenus=[dict(
                type='dropdown',
                direction='down',
                x=2,
                y=1.05,
                showactive=True,
                buttons=buttons,
                bgcolor='#F8F9FA',
                bordercolor='#8ECAE6',
                font=dict(color='#8ECAE6', size=14),
            )],
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,              
                gridcolor='#F8F9FA',           
                zeroline=False
            ), 
            yaxis=dict(
                title=dict(
                    text='Search Interest',
                    font=dict(
                        family='Montserrat',
                        size=18,
                        color='#474b4f'
                    )
                ),
                showline=True,
                linecolor='#474b4f',
                linewidth=2,
                ticks='outside',
                tickcolor='#474b4f',
                tickwidth=2,
                showticklabels=True,
                tickfont=dict(
                    family='Montserrat',
                    size=14,
                    color='#474b4f'
                ),
                showgrid=True,
                gridcolor='#F8F9FA',
                zeroline=False
            ),
            legend=dict(
                title=dict(
                    text=f'Keyword',
                    font=dict(
                        family='Montserrat', 
                        color='#474b4f', 
                        size=15
                    )
                ),
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat', color='#474b4f', size=13)
            ),
            font=dict(family='Montserrat', color='#474b4f', size=15),
            paper_bgcolor=bg_color,
            plot_bgcolor=plot_bg_color,
            margin=dict(l=60, r=200, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)




####### ABOUT AND CONTACT TAB ########
with tab2:
    st.subheader("About")
    st.write("""
    This dashboard explores international textile shipments, clothing consumption, and textile waste production 
    around the world. Built using Streamlit, Folium, and Python.
    """)
    
with tab3:
    st.subheader("Contact")
    st.write("""
         
    Grace Liu  
    Email: gl2910@columbia.edu
             
    Sofia Pelaez     
    Email: asp2265@columbia.edu
             
    Sevastian Sanchez   
    Email: ss7257@columbia.edu
              
    Emma Lucie Scherrer  
    Email: els2264@columbia.edu     
    """)
