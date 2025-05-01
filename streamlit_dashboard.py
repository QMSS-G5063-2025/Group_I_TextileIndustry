import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from folium import features
from geopy.geocoders import Nominatim
import time
import json
import requests
import ipywidgets as widgets
from IPython.display import display, clear_output
from folium.plugins import AntPath

st.set_page_config(layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat&display=swap" rel="stylesheet">
<style>
/* Apply Montserrat font across everything */
html, body, div, p, span, input, label, textarea, select, button, h1, h2, h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


st.title("Textile Industry Interactive Maps 🌍👖👗👕")
tab1, tab2, tab3 = st.tabs(["Home", "About", "Contact"])

with tab1:

    ######### Main Interactive Maps ##########
    top_consumption_countries = ['United States', 'France', 'Japan', 'Germany', 'United Kingdom']

    top_export_waste_countries = ['China', 'United States', 'India', 'Italy', 'Germany']

    top_import_waste_countries = ['China', 'United States', 'The Netherlands', 'Mexico', 'Russia']


    cons_waste_coords = {
        'United States': [37.0902, -95.7129],
        'China': [35.8617, 104.1954],
        'Japan': [36.2048, 138.2529],
        'Germany': [51.1657, 10.4515],
        'United Kingdom': [55.3781, -3.4360],
        'India': [20.5937, 78.9629],
        'Brazil': [-14.2350, -51.9253],
        'Italy': [41.8719, 12.5674],
        'France': [46.2276, 2.2137],
        'The Netherlands': [52.1326, 5.2913],
        'Russia': [61.5240, 105.3188],
        'Mexico': [23.6345, -102.5528]
    }

    map_choice = st.sidebar.selectbox(
        "Select map",
        ("Top Countries Importing the Most Apparel (Clothing Consumption)", "Top Countries Exporting the Most Textile Waste",
         "Top Countries Importing the Most Textile Waste")
    )

    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)":
        relevant_countries = top_consumption_countries
    elif map_choice == "Top Countries Exporting the Most Textile Waste":
        relevant_countries = top_export_waste_countries
    else:
        relevant_countries = top_import_waste_countries

    country_choice = st.sidebar.selectbox(
        "Explore a country",
        ["All"] + relevant_countries
    )

    ##### FOLIUM MAPS #####
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')


    for country in relevant_countries:
        folium.CircleMarker(
            location=cons_waste_coords[country],
            radius=12 if country == country_choice else 5, 
            color='#A3C9A8' if country == country_choice else '#8ECAE6',  
            fill=True,
            fill_opacity=1,
            tooltip=country
        ).add_to(m)

    st.subheader(f"{map_choice}")

    st_folium(m, use_container_width=True, height=700)

    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)":
        st.sidebar.markdown("""
        <div style="
            background-color: #A3C9A8;
            padding: 15px;
            border-radius: 10px;
            color: #1a1a1a;
            font-size: 16px;
        ">
        <b>Top 5 Countries</b><br>
        1. United States<br>
        2. Germany<br>
        3. Japan<br>
        4. United Kingdom<br>
        5. France
        </div>
        """, unsafe_allow_html=True)

        #### APPAREL IMPORTS MAP ####
        if country_choice == "All":

            #### apparel imports map ####
            st.markdown("---")
            st.markdown("<h2 style='text-align:center;'>Apparel Imports Animated Map</h2>", unsafe_allow_html=True)

            apparel_imports_df = pd.read_csv('/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/apparel_imports.csv')
            apparel_imports_df = apparel_imports_df[apparel_imports_df['Apparel_Imports'] > 0]
            df_no_world = apparel_imports_df[apparel_imports_df['Importers'] != 'World']

            def highlight_top5(group):
                top5 = group.nlargest(5, 'Apparel_Imports')
                group['Highlight'] = np.where(group['Importers'].isin(top5['Importers']), 'Top 5', 'Other')
                return group

            df_no_world = df_no_world.groupby('Year').apply(highlight_top5).reset_index(drop=True)

            color_map = {'Top 5': '#FFE5B4', 'Other': '#6C7A89'}

            fig = px.choropleth(
                df_no_world,
                locations='Importers',
                locationmode='country names',
                color='Highlight',
                color_discrete_map=color_map,
                animation_frame='Year',
                hover_name='Importers',
                hover_data={
                    'Apparel_Imports': ':.0f',
                    'Highlight': False,
                    'Year': True,
                    'Importers': False
                },
                width=1000,
                height=800
            )

            fig.update_traces(
                hovertemplate='<b>%{hovertext}</b><br>Year: %{customdata[1]}<br>Apparel imported (US dollar thousand): %{customdata[0]:,}<extra></extra>'
            )

            fig.update_geos(
                fitbounds='locations',
                showcountries=True,
                showcoastlines=False,
                showframe=False,
                bgcolor='#B0A8B9',  
                landcolor='#0f3d91', 
                lakecolor='#8ECAE6',  
                projection_type='natural earth'
            )

            fig.update_layout(
                paper_bgcolor='#B0A8B9',
                plot_bgcolor='#B0A8B9',
                font=dict(color='#F8F9FA', family='Montserrat, Arial, sans-serif', size=18),
                margin=dict(r=0, t=80, l=0, b=0),
                title=dict(
                    text = "Apparel Imported by Country (USD by thousands) — Top 5 Highlighted",
                    x =  0.5,
                    xanchor =  'center',
                    yanchor=  'top',
                    font = dict(size=28, color='#F8F9FA', family='Montserrat, Arial, sans-serif')
                    ,
                ),
                legend=dict(
                    title = None,
                    orientation='h',
                    yanchor='bottom',
                    y=0.9,
                    xanchor='right',
                    x=1,
                    bgcolor='#F8F9FA',  # <-- Light white background for legend box
                    bordercolor='#6C7A89',               # <-- Border color
                    borderwidth=2,
                    font=dict(size=18, color='#6C7A89')
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.write("The map above illustrates the total value of apparel imports (in thousands of US dollars) by country, including crocheted and knitted apparel, not crocheted and knitted apparel, as well as other made-up textile articles. The top five importing countries — the United States, France, Germany, the United Kingdom, and Japan — are highlighted in yellow, consistently ranking as the largest importers of apparel from 2005 to the present. The varying shades of grey are due to missing data.")
        
            ### time series line graph ###
            top_countries = ['United States of America', 'France', 'Japan', 'Germany', 'United Kingdom'] #Top Countries defined thanks to previous map, we can see that there is not much change

            line_df = apparel_imports_df[apparel_imports_df['Importers'].isin(top_countries)]

            fig_line = px.line(line_df,
                            x='Year',
                            y='Apparel_Imports',
                            color='Importers',
                            title='Apparel Imports Evolution for Top 5 Countries')
            
            fig_line.update_layout(
                title = dict(
                    x = 0.5,
                    xanchor = 'center',
                    font = dict(size=24, color='#474b4f', family='Montserrat')
                ),
                yaxis_title="Total Apparel Imports (USD)",
                xaxis_title="Year",
                hovermode='x unified')
            
            st.plotly_chart(fig_line, use_container_width=True)


            st.markdown("---")
            st.markdown("<h2 style='text-align:center;'>Consumer Behavior</h2>", unsafe_allow_html=True)

            st.write('We analyzed consumer interest in fast fashion versus sustainable alternatives by focusing on the top 5 apparel-importing countries and using Google search trends as a proxy for consumer demand.')
            st.write('For each country, we compared search volumes for leading fast fashion brands with terms representing second-hand and more sustainable shopping options. To ensure relevance, we tailored the keywords and brand selections to reflect the most commonly used terms and popular platforms in each country.')
            st.markdown("""
            - For Japan, for example, we conducted searches using the Japanese equivalents of “thrift” and “Shein,” then translated the results for consistency in our analysis.
            """)

            ##### ALL google search trends map #####
            def load_country_df(filename, country, keyword_cols):
                google_filepath = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/'
                df = pd.read_csv(google_filepath + filename, encoding='latin1')
                df.rename(columns={'Month': 'Date'}, inplace=True)
                df['Country'] = country
                df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('utf-8')
                return df

            dfs = [
                load_country_df('UK.csv', 'UK', ['Boohoo', 'Charity Shop']),
                load_country_df('US.csv', 'US', ['Shein', 'Thrift']),
                load_country_df('France.csv', 'France', ['Shein', 'Friperie']),
                load_country_df('Germany.csv', 'Germany', ['Shein', 'Flohmarkt']),
                load_country_df('Japan.csv', 'Japan', ['Shein', 'Thrift']),
            ]
            df = pd.concat(dfs, ignore_index=True)

            country_keywords = {
                'UK': ['Boohoo', 'Charity Shop'],
                'US': ['Shein', 'Thrift'],
                'France': ['Shein', 'Friperie'],
                'Germany': ['Shein', 'Flohmarkt'],
                'Japan': ['Shein', 'Thrift'],
            }
            line_colors = {'Shein': '#474b4f', 'Thrift': '#a7a9ac', 'Boohoo': '#474b4f', 'Charity Shop': '#a7a9ac', 'Friperie': '#a7a9ac', 'Flohmarkt': '#a7a9ac'}

            countries = list(country_keywords.keys())

            # Track trace indices for each (country, search_type)
            trace_map = {}
            fig = go.Figure()
            trace_i = 0

            for country in countries:
                cdf = df[df['Country'] == country]
                keywords = country_keywords[country]
                search_types = cdf['Search_Type'].unique()
                # Add traces for each search type
                for s_type in search_types:
                    sdf = cdf[cdf['Search_Type'] == s_type]
                    for keyword in keywords:
                        fig.add_trace(
                            go.Scatter(
                                x=sdf['Date'],
                                y=sdf[keyword],
                                mode='lines+markers',
                                name=f"{keyword}",
                                line=dict(color=line_colors[keyword], width=3),
                                visible=False
                            )
                        )
                        trace_map.setdefault((country, s_type), []).append(trace_i)
                        trace_i += 1
                # Add traces for total
                df_total = cdf.groupby('Date')[keywords].mean().reset_index()
                for keyword in keywords:
                    fig.add_trace(
                        go.Scatter(
                            x=df_total['Date'],
                            y=df_total[keyword],
                            mode='lines+markers',
                            name=f"{keyword}",
                            line=dict(color=line_colors[keyword], width=3, dash='dot'),
                            visible=False
                        )
                    )
                    trace_map.setdefault((country, 'Total Google Search'), []).append(trace_i)
                    trace_i += 1

            # Helper to build visibility mask
            def make_visibility(selected_country, selected_type):
                vis = [False] * trace_i
                for idx in trace_map.get((selected_country, selected_type), []):
                    vis[idx] = True
                return vis

            # Initial state: UK, Total Google Search
            init_country = 'UK'
            init_type = 'Total Google Search'
            fig.update_traces(visible=False)
            for idx in trace_map[(init_country, init_type)]:
                fig.data[idx].visible = True

            # Dropdown for country
            country_buttons = []
            for country in countries:
                vis = make_visibility(country, 'Total Google Search')
                country_buttons.append(dict(
                    label=country,
                    method='update',
                    args=[{'visible': vis},
                        {'title': f'Consumer Google Search Trends ({country}) - Total Google Search'}]
                ))

            # Dropdown for search type
            def make_search_type_buttons(country):
                cdf = df[df['Country'] == country]
                types = ['Total Google Search'] + list(cdf['Search_Type'].unique())  # 'Total Google Search' first
                buttons = []

                # Add button for "Total Google Search" FIRST
                vis_total = make_visibility(country, 'Total Google Search')
                buttons.append(
                    dict(
                        label='<span style="color:#1a73e8"><b>Total Google Search</b></span>',  # blue and bold
                        method='update',
                        args=[{'visible': vis_total},
                            {'title': f'Consumer Google Search Trends ({country}) - Total Google Search'}]
                    )
                )

                # Add buttons for each other search type
                for s_type in types[1:]:  # Skip 'Total Google Search' as it's already added
                    vis = make_visibility(country, s_type)
                    buttons.append(
                        dict(
                            label=s_type,
                            method='update',
                            args=[{'visible': vis},
                                {'title': f'Consumer Google Search Trends ({country}) - {s_type}'}]
                        )
                    )
                return buttons

            search_type_buttons = make_search_type_buttons(init_country)

            fig.update_layout(
                updatemenus=[
                    dict(  # Dropdown for Country (Left)
                        buttons=country_buttons,
                        direction='down',
                        x=-0.13,  # Adjust x for left position
                        y=1.05,
                        showactive=True,
                        bgcolor='#cccccc',
                        bordercolor='#474b4f',
                        font=dict(color='#1a73e8', size=15)
                    ),
                    dict(  # Dropdown for Search Type (Right)
                        buttons=search_type_buttons,
                        direction='down',
                        x=1.57,  # Adjust x for right position
                        y=1.05,
                        showactive=True,
                        bgcolor='#cccccc',
                        bordercolor='#474b4f',
                        font=dict(color='#1a73e8', size=15)
                    )
                ],
                title=f'Consumer Google Search Trends ({init_country}) - {init_type}',
                xaxis_title='Date',
                yaxis_title='Search Interest',
                legend_title='Keyword',
                legend=dict(
                    orientation='v',
                    x=1.05,
                    y=1,
                    bgcolor='rgba(245,246,250,0.7)',
                    bordercolor='#b0b0b0',
                    font=dict(color='#474b4f', size=13)
                ),
                font=dict(family='Arial', color='#474b4f', size=15),
                paper_bgcolor='#f5f6fa',
                plot_bgcolor='#e1e2e6',
                margin=dict(l=60, r=200, t=80, b=60)
            )

            st.plotly_chart(fig, use_container_width=True)

            st.write('''While Google search trends provide a practical way to approximate consumer interest, 
                     this method has several important limitations:''')
            st.markdown("""
            - Search data can be biased, particularly when comparing online-only brands to brick-and-mortar alternatives, 
                        as consumer discovery and engagement differ between digital and physical retail.
            - Trends reflect search intent & curiosity —- not purchasing behavior.
            - Increasing internet access and growth of e-commerce over time can distort long-term trends, 
                        especially in the earlier years of the dataset.
            - Some brands, like Shein (founded in 2008), did not exist before certain dates, so search interest prior to their 
                        launch is not meaningful and has been excluded from our analysis.
            """)
            st.write('''Despite these caveats, Google search data offers a useful - if imperfect - means of gauging shifts 
                     in consumer interest between fast fashion and more sustainable shopping options over time.''')


    ### Top Consumption > Google Search: US ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "United States":
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
                x=1.45,
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

    ### Top Consumption > Google Search: France ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "France":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore France</b></h2>
        </div>
        """, unsafe_allow_html=True)

        france_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/France.csv'
        df = pd.read_csv(france_google, encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Friperie']

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#B0A8B9',        
            'Friperie': '#A3C9A8'   
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
                x=1.45,
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


    ### Top Consumption > Google Search Top Consumption: Germany ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "Germany":
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
                x=1.45,
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


    ### Top Consumption > Google Search: Japan ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "Japan":
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
                x=1.45,
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

    ### Top Consumption > Google Search: UK ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "United Kingdom":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#A3C9A8;">
            <h2><b>Explore United Kingdom</b></h2>
        </div>
        """, unsafe_allow_html=True)

        uk_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/UK.csv'
        df = pd.read_csv(uk_google, encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Boohoo', 'Charity Shop']  

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Boohoo': '#B0A8B9',         
            'Charity Shop': '#A3C9A8'  
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
                x=1.45,
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

    if map_choice == "Top Countries Exporting the Most Textile Waste":
        st.sidebar.markdown("""
        <div style="
            background-color: #A3C9A8;
            padding: 15px;
            border-radius: 10px;
            color: #1a1a1a;
            font-size: 16px;
        ">
        <b>Top 5 Countries</b><br>
        1. China<br>  
        2. United States<br>  
        3. India<br>
        4. Italy<br>  
        5. Germany
        </div>                    
        """,  unsafe_allow_html=True)
    

    if map_choice == "Top Countries Exporting the Most Textile Waste" and country_choice == "All":
        st.markdown('''
                <h3>
                    We focus on 
                    <span style='background-color:#8ECAE6; font-weight:bold;'>silk waste, rags, wool waste, and worn clothes</span> 
                    as our primary metrics for textile waste. While these represent only a subset of global textile waste and doesn't
                    capture the full diversity of textile waste, they offer a consistent and reliable basis for comparison given current data limitations.
                    </h3>
                    ''', unsafe_allow_html=True)
        
        st.write('''These categories cover a broad spectrum of textile waste, from manufacturing by-products (silk and wool waste) to post-consumer items (worn clothes, rags), 
                reflecting both industrial and household contributions to textile waste flows. 

                    Textile Waste metric is calculated as sum(silk waste + wool waste + rags + worn clothes)  

- Silk Waste: By-products and unusable remnants from silk production and processing.
- Rags: Discarded textiles, often cut or sorted for industrial cleaning or recycling.
- Wool Waste: Scraps and leftovers from wool processing or discarded woolen goods.
- Worn Clothes: Used clothing, typically collected for resale, reuse, or recycling.
    ''')
        
        st.markdown('''
                <h4>
                    The United States, China, India, Italy, and Germany - all developed countries - are the largest exporters of textile waste. 
                    This reflects high levels of textile consumption, efficient collection systems, and established waste management policies
                    </h4>
                    ''', unsafe_allow_html=True)
        

        exports_filepath = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Worn clothing and other Export Data/'
        #Importing data

        #USA
        path_usa = exports_filepath + "US clothing waste exports 2023.csv"
        df_usa = pd.read_csv(path_usa, sep=';')
        df_usa = df_usa.sort_values(by=['Quantity_exported_2023'], ascending=False)
        df_usa = df_usa.rename(columns={'Importers': 'country', 'Quantity_exported_2023': 'quantity_exported'})

        # USA subset
        df_usa_s = df_usa[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_usa_s['quantity_exported'] = pd.to_numeric(df_usa_s['quantity_exported'], errors='coerce')


        #CHINA
        path_china = exports_filepath + "China clothing waste exports 2023.csv"
        df_china = pd.read_csv(path_china, sep=";")
        df_china = df_china.sort_values(by=['quantity_exported'], ascending=False)

        #CHINA subset
        df_china_s = df_china[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_china_s['quantity_exported'] = pd.to_numeric(df_china_s['quantity_exported'], errors='coerce')


        #INDIA
        path_india = exports_filepath + "India clothing waste exports 2023.csv"
        df_india = pd.read_csv(path_india, sep=";")
        df_india = df_india.sort_values(by=['quantity_exported'], ascending=False)

        #INDIA subset
        df_india_s = df_india[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_india_s['quantity_exported'] = pd.to_numeric(df_india_s['quantity_exported'], errors='coerce')

        #ITALY
        path_italy = exports_filepath + "Italy clothing waste exports 2023.csv"
        df_italy = pd.read_csv(path_italy, sep=";")
        df_italy = df_italy.sort_values(by=['quantity_exported'], ascending=False)

        #ITALY  subset
        df_italy_s = df_italy[['country', 'quantity_exported']].iloc[0:10].sort_index()
        df_italy_s['quantity_exported'] = pd.to_numeric(df_italy_s['quantity_exported'], errors='coerce')


        # GERMANY
        path_germany = exports_filepath + "Germany clothing waste exports 2023.csv"
        df_germany = pd.read_csv(path_germany, sep=";")
        df_germany = df_germany.sort_values(by=['quantity_exported'], ascending=False)

        #GERMANY subset
        df_germany_s = df_germany[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_germany_s['quantity_exported'] = pd.to_numeric(df_germany_s['quantity_exported'], errors='coerce')


        ### Getting origin and destination coordinates ###
        # USA origin coordinates
        origin_country_usa = 'United States'
        geolocator = Nominatim(user_agent="geoapi", timeout = 40)
        origin_location_usa = geolocator.geocode(origin_country_usa)
        origin_coords_usa = [origin_location_usa.latitude, origin_location_usa.longitude]  # Corrected here

        # USA destination countries coordinates
        country_coords_usa = {}
        for country in df_usa_s['country'].unique():
            location = geolocator.geocode(country)
            if location:
                country_coords_usa[country] = (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {country}")
            time.sleep(1)


        # CHINA origin coordinates
        origin_country_china = 'China'
        geolocator = Nominatim(user_agent="geoapi")
        origin_location_china = geolocator.geocode(origin_country_china)
        origin_coords_china = [origin_location_china.latitude, origin_location_china.longitude]

        # CHINA destination countries coordinates
        country_coords_china = {}
        for country in df_china_s['country'].unique():
            location = geolocator.geocode(country)
            if location:
                country_coords_china[country] = (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {country}")
            time.sleep(1)


        # INDIA origin coordinates
        origin_country_india = 'India'
        geolocator = Nominatim(user_agent="geoapi")
        origin_location_india = geolocator.geocode(origin_country_india)
        origin_coords_india = [origin_location_india.latitude, origin_location_india.longitude]

        # INDIA destination countries coordinates
        country_coords_india = {}
        for country in df_india_s['country'].unique():
            location = geolocator.geocode(country)
            if location:
                country_coords_india[country] = (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {country}")
            time.sleep(1)


        # ITALY origin coordinates
        origin_country_italy = 'Italy'
        geolocator = Nominatim(user_agent="geoapi")
        origin_location_italy = geolocator.geocode(origin_country_italy)
        origin_coords_italy = [origin_location_italy.latitude, origin_location_italy.longitude]

        # ITALY destination countries coordinates
        country_coords_italy = {}
        for country in df_italy_s['country'].unique():
            location = geolocator.geocode(country)
            if location:
                country_coords_italy[country] = (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {country}")
            time.sleep(1)


        # GERMANY origin coordinates
        origin_country_germany = 'Germany'
        geolocator = Nominatim(user_agent="geoapi")
        origin_location_germany = geolocator.geocode(origin_country_germany)
        origin_coords_germany = [origin_location_germany.latitude, origin_location_germany.longitude]

        # GERMANY destintation countries coordinates
        country_coords_germany = {}
        for country in df_germany_s['country'].unique():
            location = geolocator.geocode(country)
            if location:
                country_coords_germany[country] = (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {country}")
            time.sleep(1)

        origin_selection = st.selectbox(
        "Choose an exporting country",
        ['All', 'United States', 'China', 'India', 'Italy', 'Germany']
        )

        def create_map(selected_origin):
            m_countries = folium.Map(location=[20, 0], zoom_start=3, tiles='cartodb positron')

            def get_color(qty):
                if qty > 100000:
                    return "#3A506B"
                elif qty > 40000:
                    return "#D98C5F"
                else:
                    return '#8A9A5B'

            countries_data = [
                (origin_coords_usa, df_usa_s, country_coords_usa, "United States"),
                (origin_coords_china, df_china_s, country_coords_china, "China"),
                (origin_coords_india, df_india_s, country_coords_india, "India"),
                (origin_coords_italy, df_italy_s, country_coords_italy, "Italy"),
                (origin_coords_germany, df_germany_s, country_coords_germany, "Germany"),
            ]

            origin_country_names = ['United States of America', 'China', 'India', 'Italy', 'Germany']

            url = 'https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json'
            world_geo = requests.get(url).json()

            def style_function(feature):
                country_name = feature['properties']['name']
                if country_name in origin_country_names:
                    return {
                        'fillColor': '#FFE5B4',
                        'color': 'none',
                        'weight': 0,
                        'fillOpacity': 0.3
                    }
                else:
                    return {
                        'fillColor': 'none',
                        'color': 'none',
                        'weight': 0,
                        'fillOpacity': 0
                    }

            folium.GeoJson(
                world_geo,
                style_function=style_function
            ).add_to(m_countries)

            for origin_coords, df, country_coords, country_name in countries_data:

                if selected_origin != 'All' and selected_origin != country_name:
                    continue

                folium.CircleMarker(
                    location=origin_coords,
                    radius=6,
                    color='#D96C06',
                    fill=True,
                    fill_color='#D96C06',
                    fill_opacity=1,
                    popup=folium.Popup(f"<b>{country_name}</b><br>Total Exported: {df['quantity_exported'].sum()} Tons", max_width=250)
                ).add_to(m_countries)

                for idx, row in df.iterrows():
                    dest_country = row['country']
                    qty = row['quantity_exported']

                    if dest_country in country_coords:
                        dest_coords = country_coords[dest_country]

                        AntPath(
                            locations=[origin_coords, dest_coords],
                            color=get_color(qty),
                            weight=2 + qty / 14000,
                            delay=800,
                            dash_array=[8, 20],
                            pulse_color='white'
                        ).add_to(m_countries)

                        folium.CircleMarker(
                            location=dest_coords,
                            radius=4,
                            color='#A3C9A8',
                            fill=True,
                            fill_color='#A3C9A8',
                            fill_opacity=0.7,
                            popup=folium.Popup(f"{dest_country}: {qty} Tons", max_width=200)
                        ).add_to(m_countries)

            legend_html = """
            <div style="
                position: fixed;
                bottom: 50px; left: 50px; width: 230px; height: 130px;
                background-color: white;
                border:2px solid grey;
                z-index:9999;
                font-size:14px;
                padding: 10px;
            ">
            <b>Export Quantity Legend</b><br>
            <i style="background:#3A506B; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> > 100,000 Tons<br>
            <i style="background:#D98C5F; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> 40,000–100,000 Tons<br>
            <i style="background:#8A9A5B; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> < 40,000 Tons
            </div>
            """
            m_countries.get_root().html.add_child(folium.Element(legend_html))

            return m_countries

        def update_map(change):
            clear_output(wait=True)
            display(origin_selection)
            m = create_map(origin_selection.value)
            display(m)

        m = create_map(origin_selection)
        st_folium(m, use_container_width=True, height=600)

        st.markdown('''
                <h3>
                    <span style = font-weight:bold;'>Environmental Implications</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        
        st.markdown('''
                - **Waste Diversion**: Exporting textile waste helps divert large quantities from domestic landfills and incinerators, potentially reducing environmental burdens at home.
                - **Resource Efficiency**: By extending the life cycle of clothing through reuse and recycling abroad, these exports lower the carbon and water footprint compared to producing new textiles-emissions can be reduced by up to 70%.
                - **Global Redistribution**: Much of the exported textile waste is reused in lower- and middle-income countries, providing affordable clothing and supporting local economies.
                 ''')
        
        ####### TEXTILE EXPORTS BAR GRAPH #######
        textile_exp_df = pd.read_csv('/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Textile_Waste_Exports.csv')

        textile_exp_df = textile_exp_df[textile_exp_df['Exporter Country'] != 'World']
        textile_exp_df['Export Value (USD)'] = pd.to_numeric(textile_exp_df['Export Value (USD)'], errors='coerce').fillna(0)

        focus_countries = ['United States of America', 'China', 'India', 'Italy', 'Germany']

        textile_exp_df = textile_exp_df[textile_exp_df['Exporter Country'].isin(focus_countries)]

        waste_types = textile_exp_df['Textile Type'].unique()

        def get_focus_values(waste_type=None):
            if waste_type is None:
                d = textile_exp_df.groupby('Exporter Country')['Export Value (USD)'].sum()
            else:
                d = textile_exp_df[textile_exp_df['Textile Type'] == waste_type].groupby('Exporter Country')['Export Value (USD)'].sum()
            d = d.reindex(focus_countries, fill_value=0)

            d = d.sort_values(ascending=False)

            return d

        dropdown_options = [('**Textile Waste**', None)]
        dropdown_options += [(wt, wt) for wt in waste_types]

        bar_data = []
        x_labels = []
        for label, wt in dropdown_options:
            values = get_focus_values(wt)
            bar_data.append(values.values)
            x_labels.append(values.index)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x_labels[0],
            y=bar_data[0],
            marker_color='blue'
        ))

        buttons = []
        buttons = []
        for i, (label, wt) in enumerate(dropdown_options):
            clean_label = label.replace('**', '<b>').replace('**', '</b>')
            buttons.append(dict(
                label=clean_label,
                method='update',
                args=[
                    {'y': [bar_data[i]], 'x': [x_labels[i]]},
                    {'title': f"Top 5 Waste Textile Exporters: focus on {clean_label}"}
                ]
            ))

        fig.update_layout(
            updatemenus=[dict(
                buttons=buttons,
                direction='down',
                showactive=True,
                x=0,
                xanchor='left',
                y=1.15,
                yanchor='top'
            )],
            title="Top 5 Textile Waste Exporters",
            title_x=0.5,
            yaxis_title='Total Export Value (USD)',
            xaxis_title='Country'
        )

        st.plotly_chart(fig)

        st.markdown('''
                <h3>
                    <span style= font-weight:bold;'>Social and Economic Impacts</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        st.markdown('''
        - **Job Creation**: The trade in used textiles supports thousands of jobs in receiving countries, both in formal and informal sectors. For example, Nordic exports alone are estimated to support over 10,000 market sellers in Africa.
        - **Access to Affordable Clothing**: Imports of used clothing make apparel more affordable in importing countries, though there are concerns about negative impacts on local textile industries.
        ''')

        ##### top 5 textile waste exporters #####
        textile_exp_df = pd.read_csv('Textile_Waste_Exports.csv')

        agg = textile_exp_df.groupby('Textile Type')['Export Value (USD)'].sum().reset_index()

        agg = agg.dropna(subset=['Export Value (USD)'])

        agg = agg.sort_values('Export Value (USD)')

        fig = go.Figure(go.Bar(
            y=agg['Textile Type'],
            x=agg['Export Value (USD)'],
            orientation='h',
            marker_color='#4062BB',
            text=[f"${v:,.0f}" for v in agg['Export Value (USD)']],
            textposition='outside',
            insidetextanchor='start',
            hovertemplate='%{y}: %{x:,.0f} USD<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text='Total Export Value per Textile Type',
                x=0.5,  
                xanchor='center' 
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                title='Total Export Value (USD)'
            ),
            yaxis=dict(
                showgrid=False,
                automargin=True,
                title=''
            ),
            plot_bgcolor='white',
            font=dict(size=16, family='Arial'),
            margin=dict(l=120, r=40, t=60, b=40),
            bargap=0.5,
            showlegend=False
        )

        fig.update_traces(
            marker_line_width=0,
            textfont=dict(
                family='Arial',
                size=16,
                color='#4062BB',
            )
        )

        st.plotly_chart(fig)

        st.markdown('''
                <h3>
                    <span style= font-weight:bold;'>Challenges and Risks</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        st.markdown('''
        - **Waste Transfer**: There is ongoing debate about whether this practice truly supports circularity or simply shifts the waste problem to countries with less capacity for responsible disposal or recycling. In many cases, textiles that cannot be reused eventually end up in landfills or are openly burned in recipient countries, especially in Africa and Asia.
        - **Regulatory Scrutiny**: Growing environmental concerns have led some governments (e.g., Sweden, Denmark, France) to propose stricter regulations on textile waste exports, aiming to ensure that exports do not simply offload environmental burdens onto less-equipped nations.
        ''')

        #### total export value per textile type ####

        #textile_exp_df = pd.read_csv('Textile_Waste_Exports.csv')

        countries = ['United States of America', 'China', 'India', 'Italy', 'Germany']
        textile_exp_df = textile_exp_df[textile_exp_df['Exporter Country'].isin(countries)]

        textile_exp_df['Export Value (USD)'] = pd.to_numeric(textile_exp_df['Export Value (USD)'], errors='coerce')

        textile_types = textile_exp_df['Textile Type'].unique()

        fig = go.Figure()

        traces_per_type = []
        for ttype in textile_types:
            traces = []
            for country in countries:
                subset = textile_exp_df[(textile_exp_df['Textile Type'] == ttype) & (textile_exp_df['Exporter Country'] == country)]
                traces.append(go.Scatter(
                    x=subset['Year'],
                    y=subset['Export Value (USD)'],
                    mode='lines+markers',
                    name=country
                ))
            traces_per_type.append(traces)

        for trace in traces_per_type[0]:
            fig.add_trace(trace)

        buttons = []
        for i, ttype in enumerate(textile_types):
            visible = [False] * (len(textile_types) * len(countries))
            for j in range(len(countries)):
                visible[i * len(countries) + j] = True

            buttons.append(dict(
                label=ttype,
                method='update',
                args=[
                    {'y': [traces_per_type[i][j].y for j in range(len(countries))],
                    'x': [traces_per_type[i][j].x for j in range(len(countries))]},
                    {'title': f'Export Value Over Time: {ttype}'}
                ]
            ))

        fig.update_layout(
            updatemenus=[dict(
                type="dropdown",
                direction="down",
                buttons=buttons,
                x=1.15,
                y=0.5,
                showactive=True
            )],
            title=f'Export Value Over Time: {textile_types[0]}',
            xaxis_title='Year',
            yaxis_title='Export Value (USD)',
        )

        st.plotly_chart(fig)

        st.markdown('''<i>*"Exporting used textiles is a fundamental part of the textile circular economy-an approach 
                    that minimizes waste by keeping products in use for as long as possible. Rather than discarding 
                    garments into landfills or incinerators, exporting worn clothing extends their life cycle, 
                    reduces environmental impact, and creates economic opportunities."*</i>''', unsafe_allow_html = True)


    ### Conditional Network Visualization (India textile shipments) ###
    if map_choice == "Top Countries Exporting the Most Textile Waste" and country_choice == "India":
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
            radius=10,
            color='#6C7A89',
            fill=True,
            fill_opacity=1,
            tooltip = 'India'
        ).add_to(m2)

        st_folium(m2, use_container_width=True, height=600)

        st.markdown("""
        | Abbreviation | Meaning | Description |
        |:------------|:---------|:------------|
        | **kgs** | Kilograms | Weight measurement: 1 kg = 1,000 grams |
        | **mts** | Metric Tons | Weight measurement: 1 metric ton = 1,000 kilograms |
        | **pcs** | Pieces | Count of individual items or garments |
        | **unt** | Units | General count of goods |
        """)


    if map_choice == "Top Countries Importing the Most Textile Waste":
        st.sidebar.markdown("""
        <div style="
            background-color: #A3C9A8;
            padding: 15px;
            border-radius: 10px;
            color: #1a1a1a;
            font-size: 16px;
        ">
        <b>Top 5 Countries</b><br>
        1. United States<br>  
        2. China<br>  
        3. The Netherlands<br>
        4. Mexico<br>  
        5. Russia
        </div>                    
        """,  unsafe_allow_html=True)

    




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
