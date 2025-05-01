import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
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

business_palette = [
    "#3A506B",  # Navy Blue
    "#D98C5F",  # Warm Orange
    "#E07A5F",  # Coral Red
    "#EAE0D5",  # Light Taupe
    "#B7B7D7",  # Lavender
    "#22223B",  # Charcoal
    "#8A9A5B",  # Olive Green
]

modern_business_template = dict(
    layout=dict(
        font=dict(
            family="Montserrat, sans-serif",
            color="#22223B",
            size=16
        ),
        title=dict(
            font=dict(
                family="Montserrat, sans-serif",
                color="#3A506B",
                size=22
            ),
            x=0.5
        ),
        paper_bgcolor="#f7f7f7",
        plot_bgcolor="#f7f7f7",
        xaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            zeroline=False,
            linecolor="#bdbdbd",
            ticks="outside",
            tickfont=dict(size=15, color="#22223B"),
            title=dict(
                font=dict(size=16, color="#22223B")
            )
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            zeroline=False,
            linecolor="#bdbdbd",
            ticks="outside",
            tickfont=dict(size=15, color="#22223B"),
            title=dict(
                font=dict(size=16, color="#22223B")
            )
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#e0e0e0",
            title=dict(font=dict(size=15, color="#22223B"))
        ),
        colorway=business_palette,
        margin=dict(l=80, r=40, t=80, b=60)
    )
)

pio.templates["modern_business"] = modern_business_template
pio.templates.default = "modern_business"

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


    for i, country in enumerate(relevant_countries):
        folium.CircleMarker(
            location=cons_waste_coords[country],
            radius=12 if country == country_choice else 5, 
            color=business_palette[i % len(business_palette)],  
            fill=True,
            fill_color=business_palette[i % len(business_palette)],
            fill_opacity=0.9 if country == country_choice else 0.6,
            tooltip=country
        ).add_to(m)

    st.subheader(f"{map_choice}")

    st_folium(m, use_container_width=True, height=700)

    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)":
        st.sidebar.markdown("""
        <div style="
            background-color: #D98C5F;
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

            apparel_imports_df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/apparel_imports.csv')
            apparel_imports_df = apparel_imports_df[apparel_imports_df['Apparel_Imports'] > 0]
            df_no_world = apparel_imports_df[apparel_imports_df['Importers'] != 'World']

            def highlight_top5(group):
                top5 = group.nlargest(5, 'Apparel_Imports')
                group['Highlight'] = np.where(group['Importers'].isin(top5['Importers']), 'Top 5', 'Other')
                return group

            df_no_world = df_no_world.groupby('Year').apply(highlight_top5).reset_index(drop=True)

            color_map = {'Top 5': '#D98C5F', 'Other': '#3A506B'}

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

            fig.update_geos(
                fitbounds='locations',
                showcountries=True,
                showcoastlines=False,
                showframe=False,
                bgcolor='#22223B',
                landcolor='#3A506B',
                lakecolor='#22223B', 
                projection_type='natural earth'
            )

            fig.update_layout(
    
                title=dict(
                    text="Apparel Imported by Country (USD by thousands) — Top 5 Highlighted",
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=28, color='#3A506B', family='Montserrat, sans-serif')
                ),
                legend=dict(
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=0.02,
                    bgcolor='rgba(255,255,255,0.6)',
                    bordercolor='#e0e0e0',
                    borderwidth=1.2,
                    font=dict(size=16, color='#22223B')
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown('''The map above illustrates the total value of apparel imports (in thousands of US dollars) by country, 
                        including crocheted and knitted apparel, not crocheted and knitted apparel as well as other made up textiles articles. 
                        The top five importing countries, the United States, France, Germany, the United Kingdom, and Japan, are highlighted in 
                        yellow, consistently ranking as the largest importers of apparel from 2005 to the present. The varying shades of blue are 
                        due to missing data.''')
        
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

            st.markdown('''We decided to analyse consumer interest in fast fashion versus more sustainable alternatives by focusing on the top five apparel-importing countries and using Google search trends as a proxy for consumer demand.''')
            st.write('''For each country, we compared search volumes for leading fast fashion brands with terms representing second-hand and 
                     more sustainable shopping options. To ensure relevance, we tailored the keywords and brand selections to reflect the most 
                     commonly used terms and popular platforms in each country.''')
            st.markdown("""
            - For Japan, for example, we conducted searches using the Japanese equivalents of “thrift” and “Shein,” then translated the results for consistency in our analysis.
            """)

            ##### ALL google search trends map #####
            def load_country_df(filename, country, keyword_cols):
                #google_filepath = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/'
                df = pd.read_csv(filename, encoding='latin1')
                df.rename(columns={'Month': 'Date'}, inplace=True)
                df['Country'] = country
                df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('utf-8')
                return df

            dfs = [
                load_country_df('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/UK.csv', 'UK', ['Boohoo', 'Charity Shop']),
                load_country_df('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/US.csv', 'US', ['Shein', 'Thrift']),
                load_country_df('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/France.csv', 'France', ['Shein', 'Friperie']),
                load_country_df('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/Germany.csv', 'Germany', ['Shein', 'Flohmarkt']),
                load_country_df('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/Japan.csv', 'Japan', ['Shein', 'Thrift']),
            ]
            df = pd.concat(dfs, ignore_index=True)

            country_keywords = {
                'UK': ['Boohoo', 'Charity Shop'],
                'US': ['Shein', 'Thrift'],
                'France': ['Shein', 'Friperie'],
                'Germany': ['Shein', 'Flohmarkt'],
                'Japan': ['Shein', 'Thrift'],
            }
            line_colors = {
                'Shein': '#3A506B',
                'Thrift': '#D98C5F',
                'Boohoo': '#3A506B',
                'Charity Shop': '#D98C5F',
                'Friperie': '#D98C5F',
                'Flohmarkt': '#D98C5F'
            }
            countries = list(country_keywords.keys())

            trace_map = {}
            fig = go.Figure()
            trace_i = 0

            for country in countries:
                cdf = df[df['Country'] == country]
                keywords = country_keywords[country]
                search_types = cdf['Search_Type'].unique()

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


            def make_visibility(selected_country, selected_type):
                vis = [False] * trace_i
                for idx in trace_map.get((selected_country, selected_type), []):
                    vis[idx] = True
                return vis
            
            dropdown_menus = []
            for i, country in enumerate(countries):
                cdf = df[df['Country'] == country]
                types = ['Total Google Search'] + list(cdf['Search_Type'].unique())
                buttons = []
                for s_type in types:
                    buttons.append(dict(
                        label=s_type,
                        method="update",
                        args=[
                            {"visible": make_visibility(country, s_type)},
                            {"title": f"<b>Consumer Google Search Trends ({country}) - {s_type}</b>"}
                        ]
                    ))
                dropdown_menus.append(dict(
                    type='dropdown',
                    direction='down',
                    buttons=buttons,
                    x=0.01,
                    y=1.2,
                    xanchor='left',
                    yanchor='top',
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(size=12, color='#3A506B'),
                    visible=(i == 0)
                ))

            country_buttons = []
            for i, country in enumerate(countries):
                label = f"{country}"
                country_buttons.append(dict(
                    label=label,
                    method="update",
                    args=[
                        {"visible": make_visibility(country, 'Total Google Search')},
                        {"title": f"<b>Consumer Google Search Trends ({country}) - Total Google Search</b>",
                        **{f"updatemenus[{j+1}].visible": (j == i) for j in range(len(countries))}
                        }
                    ]
                ))

            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        buttons=country_buttons,
                        x=0.5,
                        y=1.2,
                        xanchor="center",
                        yanchor="top",
                        bgcolor='white',
                        font=dict(color='#3A506B', size=14, family='Montserrat, sans-serif'),
                        bordercolor='#3A506B'
                    )
                ] + dropdown_menus,
                title=dict(
                    text='<b>Consumer Google Search Trends (UK) - Total Google Search</b>',
                    x=0.5,
                    xanchor='center',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=22)
                ),
                yaxis=dict(
                    title='Search Interest',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.5)',
                    zeroline=False
                ),
                xaxis=dict(
                    title='Date',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.5)'
                ),
                legend_title='Keyword',
                legend=dict(
                    orientation='h',
                    y=-0.3,
                    x=0.5,
                    xanchor='center',
                    bgcolor='rgba(245,246,250,0.7)',
                    bordercolor='#b0b0b0',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                ),
                font=dict(
                    family='Montserrat, sans-serif',
                    color='#3A506B',
                    size=12
                ),
                paper_bgcolor='white',
                plot_bgcolor='rgba(245,246,250,0.3)',
                margin=dict(t=150, b=100),
                hovermode='x unified'
            )


            for idx in trace_map[('UK', 'Total Google Search')]:
                fig.data[idx].visible = True

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
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore United States</b></h2>
        </div>
        """, unsafe_allow_html=True)

        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/US.csv', encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Thrift']

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#3A506B',        
            'Thrift': '#D98C5F'   
        }

        trace_map = {}
        fig = go.Figure()
        trace_i = 0


        search_types = df['Search_Type'].unique()

        for s_type in search_types:
            sdf = df[df['Search_Type'] == s_type]
            for keyword in keyword_cols:
                fig.add_trace(
                    go.Scatter(
                        x=sdf['Date'],
                        y=sdf[keyword],
                        mode='lines',
                        name=f"{keyword}",
                        line=dict(color=line_colors[keyword], width=2),
                        visible=False
                    )
                )
                trace_map.setdefault(s_type, []).append(trace_i)
                trace_i += 1

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()
        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines',
                    name=f"{keyword}",
                    line=dict(color=line_colors[keyword], width=2),
                    visible=False
                )
            )
            trace_map.setdefault('Total Google Search', []).append(trace_i)
            trace_i += 1

        def make_visibility(selected_type):
            vis = [False] * trace_i
            for idx in trace_map.get(selected_type, []):
                vis[idx] = True
            return vis

        init_type = 'Total Google Search'
        fig.update_traces(visible=False)
        for idx in trace_map[init_type]:
            fig.data[idx].visible = True

        types = ['Total Google Search'] + list(search_types)
        buttons = []

        vis_total = make_visibility('Total Google Search')
        buttons.append(
            dict(
                label='<span style="color:#3A506B"><b>Total Google Search</b></span>',
                method='update',
                args=[{'visible': vis_total}, {'title': f'US Consumer Google Search Trends'}]
            )
        )

        for s_type in search_types:
            vis = make_visibility(s_type)
            buttons.append(
                dict(
                    label=s_type,
                    method='update',
                    args=[{'visible': vis}, {'title': f'US Consumer Google Search Trends - {s_type}'}]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction='down',
                    x=1.22,
                    y=1.15,
                    showactive=True,
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                )
            ],
            title=dict(
                text=f'<b>US Consumer Google Search Trends - {init_type}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=18)
            ),
            yaxis=dict(
                title='Search Interest',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            legend_title='Keyword',
            legend=dict(
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
            ),
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            margin=dict(l=60, r=200, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    ### Top Consumption > Google Search: France ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "France":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore France</b></h2>
        </div>
        """, unsafe_allow_html=True)

        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/France.csv', encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Friperie']

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#3A506B',        
            'Friperie': '#D98C5F'   
        }

        trace_map = {}
        fig = go.Figure()
        trace_i = 0

        search_types = df['Search_Type'].unique()

        for s_type in search_types:
            sdf = df[df['Search_Type'] == s_type]
            for keyword in keyword_cols:
                fig.add_trace(
                    go.Scatter(
                        x=sdf['Date'],
                        y=sdf[keyword],
                        mode='lines',
                        name=f"{keyword}",
                        line=dict(color=line_colors[keyword], width=2),
                        visible=False
                    )
                )
                trace_map.setdefault(s_type, []).append(trace_i)
                trace_i += 1

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()
        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines',
                    name=f"{keyword}",
                    line=dict(color=line_colors[keyword], width=2),
                    visible=False
                )
            )
            trace_map.setdefault('Total Google Search', []).append(trace_i)
            trace_i += 1

        def make_visibility(selected_type):
            vis = [False] * trace_i
            for idx in trace_map.get(selected_type, []):
                vis[idx] = True
            return vis

        init_type = 'Total Google Search'
        fig.update_traces(visible=False)
        for idx in trace_map[init_type]:
            fig.data[idx].visible = True

        types = ['Total Google Search'] + list(search_types)
        buttons = []

        vis_total = make_visibility('Total Google Search')
        buttons.append(
            dict(
                label='<span style="color:#3A506B"><b>Total Google Search</b></span>',
                method='update',
                args=[{'visible': vis_total}, {'title': f'France Consumer Google Search Trends'}]
            )
        )

        for s_type in search_types:
            vis = make_visibility(s_type)
            buttons.append(
                dict(
                    label=s_type,
                    method='update',
                    args=[{'visible': vis}, {'title': f'France Consumer Google Search Trends - {s_type}'}]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction='down',
                    x=1.22,
                    y=1.15,
                    showactive=True,
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                )
            ],
            title=dict(
                text=f'<b>France Consumer Google Search Trends - {init_type}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=18)
            ),
            yaxis=dict(
                title='Search Interest',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            legend_title='Keyword',
            legend=dict(
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
            ),
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            margin=dict(l=60, r=200, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)    

    ### Top Consumption > Google Search Top Consumption: Germany ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "Germany":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore Germany</b></h2>
        </div>
        """, unsafe_allow_html=True)

        #germany_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/Germany.csv'
        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/Germany.csv', encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Flohmarkt'] 

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#3A506B',         
            'Flohmarkt': '#D98C5F'  
        }
        
        trace_map = {}
        fig = go.Figure()
        trace_i = 0

        search_types = df['Search_Type'].unique()

        for s_type in search_types:
            sdf = df[df['Search_Type'] == s_type]
            for keyword in keyword_cols:
                fig.add_trace(
                    go.Scatter(
                        x=sdf['Date'],
                        y=sdf[keyword],
                        mode='lines',
                        name=f"{keyword}",
                        line=dict(color=line_colors[keyword], width=2),
                        visible=False
                    )
                )
                trace_map.setdefault(s_type, []).append(trace_i)
                trace_i += 1

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()
        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines',
                    name=f"{keyword}",
                    line=dict(color=line_colors[keyword], width=2),
                    visible=False
                )
            )
            trace_map.setdefault('Total Google Search', []).append(trace_i)
            trace_i += 1

        def make_visibility(selected_type):
            vis = [False] * trace_i
            for idx in trace_map.get(selected_type, []):
                vis[idx] = True
            return vis

        init_type = 'Total Google Search'
        fig.update_traces(visible=False)
        for idx in trace_map[init_type]:
            fig.data[idx].visible = True


        types = ['Total Google Search'] + list(search_types)
        buttons = []

        vis_total = make_visibility('Total Google Search')
        buttons.append(
            dict(
                label='<span style="color:#3A506B"><b>Total Google Search</b></span>',
                method='update',
                args=[{'visible': vis_total}, {'title': f'Consumer Google Search Trends (Germany)'}]
            )
        )

        for s_type in search_types:
            vis = make_visibility(s_type)
            buttons.append(
                dict(
                    label=s_type,
                    method='update',
                    args=[{'visible': vis}, {'title': f'Germany Consumer Google Search Trends - {s_type}'}]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction='down',
                    x=1.22,
                    y=1.15,
                    showactive=True,
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                )
            ],
            title=dict(
                text=f'<b>Germany Consumer Google Search Trends - {init_type}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=18)
            ),
            yaxis=dict(
                title='Search Interest',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            legend_title='Keyword',
            legend=dict(
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
            ),
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            margin=dict(l=60, r=200, t=80, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    ### Top Consumption > Google Search: Japan ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "Japan":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore Japan</b></h2>
        </div>
        """, unsafe_allow_html=True)

        #japan_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/Japan.csv'
        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/Japan.csv', encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Shein', 'Thrift']  # Keywords for Japan: シーイン is Shein and 古着 is Thrift

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Shein': '#3A506B',         
            'Thrift': '#D98C5F'  
        }
        
        trace_map = {}
        fig = go.Figure()
        trace_i = 0

        search_types = df['Search_Type'].unique()

        for s_type in search_types:
            sdf = df[df['Search_Type'] == s_type]
            for keyword in keyword_cols:
                fig.add_trace(
                    go.Scatter(
                        x=sdf['Date'],
                        y=sdf[keyword],
                        mode='lines',
                        name=f"{keyword}",
                        line=dict(color=line_colors[keyword], width=2),
                        visible=False
                    )
                )
                trace_map.setdefault(s_type, []).append(trace_i)
                trace_i += 1

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()
        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines',
                    name=f"{keyword}",
                    line=dict(color=line_colors[keyword], width=2),
                    visible=False
                )
            )
            trace_map.setdefault('Total Google Search', []).append(trace_i)
            trace_i += 1

        def make_visibility(selected_type):
            vis = [False] * trace_i
            for idx in trace_map.get(selected_type, []):
                vis[idx] = True
            return vis

        init_type = 'Total Google Search'
        fig.update_traces(visible=False)
        for idx in trace_map[init_type]:
            fig.data[idx].visible = True

        types = ['Total Google Search'] + list(search_types)
        buttons = []

        vis_total = make_visibility('Total Google Search')
        buttons.append(
            dict(
                label='<span style="color:#3A506B"><b>Total Google Search</b></span>',
                method='update',
                args=[{'visible': vis_total}, {'title': f'Japan Consumer Google Search Trends'}]
            )
        )

        for s_type in search_types:
            vis = make_visibility(s_type)
            buttons.append(
                dict(
                    label=s_type,
                    method='update',
                    args=[{'visible': vis}, {'title': f'Japan Consumer Google Search Trends - {s_type}'}]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction='down',
                    x=1.22,
                    y=1.15,
                    showactive=True,
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                )
            ],
            title=dict(
                text=f'<b>Japan Consumer Google Search Trends - {init_type}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=18)
            ),
            yaxis=dict(
                title='Search Interest',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            legend_title='Keyword',
            legend=dict(
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
            ),
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            margin=dict(l=60, r=200, t=80, b=60)
        )


        st.plotly_chart(fig, use_container_width=True)

    ### Top Consumption > Google Search: UK ###
    if map_choice == "Top Countries Importing the Most Apparel (Clothing Consumption)" and country_choice == "United Kingdom":
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore United Kingdom</b></h2>
        </div>
        """, unsafe_allow_html=True)

        #uk_google = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Consumer_Google_Search/UK.csv'
        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Consumer_Google_Search/UK.csv', encoding='latin1')
        df.rename(columns={'Month': 'Date'}, inplace=True)
        keyword_cols = ['Boohoo', 'Charity Shop']  

        df['Search_Type'] = df['Search_Type'].str.encode('ascii', 'ignore').str.decode('ascii')

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()

        search_types = df['Search_Type'].unique()
        line_colors = {
            'Boohoo': '#3A506B',         
            'Charity Shop': '#D98C5F'  
        }
        
        trace_map = {}
        fig = go.Figure()
        trace_i = 0

        search_types = df['Search_Type'].unique()

        for s_type in search_types:
            sdf = df[df['Search_Type'] == s_type]
            for keyword in keyword_cols:
                fig.add_trace(
                    go.Scatter(
                        x=sdf['Date'],
                        y=sdf[keyword],
                        mode='lines',
                        name=f"{keyword}",
                        line=dict(color=line_colors[keyword], width=2),
                        visible=False
                    )
                )
                trace_map.setdefault(s_type, []).append(trace_i)
                trace_i += 1

        df_total = df.groupby('Date')[keyword_cols].mean().reset_index()
        for keyword in keyword_cols:
            fig.add_trace(
                go.Scatter(
                    x=df_total['Date'],
                    y=df_total[keyword],
                    mode='lines',
                    name=f"{keyword}",
                    line=dict(color=line_colors[keyword], width=2),
                    visible=False
                )
            )
            trace_map.setdefault('Total Google Search', []).append(trace_i)
            trace_i += 1

        def make_visibility(selected_type):
            vis = [False] * trace_i
            for idx in trace_map.get(selected_type, []):
                vis[idx] = True
            return vis

        init_type = 'Total Google Search'
        fig.update_traces(visible=False)
        for idx in trace_map[init_type]:
            fig.data[idx].visible = True

        types = ['Total Google Search'] + list(search_types)
        buttons = []

        vis_total = make_visibility('Total Google Search')
        buttons.append(
            dict(
                label='<span style="color:#3A506B"><b>Total Google Search</b></span>',
                method='update',
                args=[{'visible': vis_total}, {'title': f'UK Consumer Google Search Trends'}]
            )
        )

        for s_type in search_types:
            vis = make_visibility(s_type)
            buttons.append(
                dict(
                    label=s_type,
                    method='update',
                    args=[{'visible': vis}, {'title': f'UK Consumer Google Search Trends - {s_type}'}]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction='down',
                    x=1.22,
                    y=1.15,
                    showactive=True,
                    bgcolor='white',
                    bordercolor='#3A506B',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
                )
            ],
            title=dict(
                text=f'<b>UK Consumer Google Search Trends - {init_type}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=18)
            ),
            yaxis=dict(
                title='Search Interest',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            legend_title='Keyword',
            legend=dict(
                orientation='v',
                x=1.05,
                y=1,
                bgcolor='rgba(245,246,250,0.7)',
                bordercolor='#b0b0b0',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=12)
            ),
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            margin=dict(l=60, r=200, t=80, b=60)
        )


        st.plotly_chart(fig, use_container_width=True)

    if map_choice == "Top Countries Exporting the Most Textile Waste":
        st.sidebar.markdown("""
        <div style="
            background-color: #D98C5F;
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
                    <span style='background-color:#D98C5F; font-weight:bold;'>silk waste, rags, wool waste, and worn clothes</span> 
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
        

        #exports_filepath = '/Users/graceliu/Desktop/Columbia/Spring2025/data_visualization/final_project/Worn clothing and other Export Data/'
        #Importing data

        #USA
        path_usa = "https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/US%20clothing%20waste%20exports%202023.csv"
        df_usa = pd.read_csv(path_usa, sep=';')
        df_usa = df_usa.sort_values(by=['Quantity_exported_2023'], ascending=False)
        df_usa = df_usa.rename(columns={'Importers': 'country', 'Quantity_exported_2023': 'quantity_exported'})

        # USA subset
        df_usa_s = df_usa[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_usa_s['quantity_exported'] = pd.to_numeric(df_usa_s['quantity_exported'], errors='coerce')


        #CHINA
        path_china = "https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/China%20clothing%20waste%20exports%202023.csv"
        df_china = pd.read_csv(path_china, sep=";")
        df_china = df_china.sort_values(by=['quantity_exported'], ascending=False)

        #CHINA subset
        df_china_s = df_china[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_china_s['quantity_exported'] = pd.to_numeric(df_china_s['quantity_exported'], errors='coerce')


        #INDIA
        path_india = "https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/India%20clothing%20waste%20exports%202023.csv"
        df_india = pd.read_csv(path_india, sep=";")
        df_india = df_india.sort_values(by=['quantity_exported'], ascending=False)

        #INDIA subset
        df_india_s = df_india[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_india_s['quantity_exported'] = pd.to_numeric(df_india_s['quantity_exported'], errors='coerce')

        #ITALY
        path_italy = "https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/Italy%20clothing%20waste%20exports%202023.csv"
        df_italy = pd.read_csv(path_italy, sep=";")
        df_italy = df_italy.sort_values(by=['quantity_exported'], ascending=False)

        #ITALY  subset
        df_italy_s = df_italy[['country', 'quantity_exported']].iloc[0:10].sort_index()
        df_italy_s['quantity_exported'] = pd.to_numeric(df_italy_s['quantity_exported'], errors='coerce')


        # GERMANY
        path_germany = "https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/Germany%20clothing%20waste%20exports%202023.csv"
        df_germany = pd.read_csv(path_germany, sep=";")
        df_germany = df_germany.sort_values(by=['quantity_exported'], ascending=False)

        #GERMANY subset
        df_germany_s = df_germany[['country', 'quantity_exported']].iloc[1:11].sort_index()
        df_germany_s['quantity_exported'] = pd.to_numeric(df_germany_s['quantity_exported'], errors='coerce')

        all_countries = set(
            pd.concat([
                df_usa_s['country'],
                df_china_s['country'],
                df_india_s['country'],
                df_italy_s['country'],
                df_germany_s['country'],
                pd.Series(['United States', 'China', 'India', 'Italy', 'Germany'])
            ])
        )

        df_coords = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/country_coordinates.csv')
        coord_dict = df_coords.set_index('country')[['latitude', 'longitude']].T.to_dict()

        def get_coords(country):
            return [coord_dict[country]['latitude'], coord_dict[country]['longitude']] if country in coord_dict else None

        def load_and_subset(path, importer_col, qty_col):
            df = pd.read_csv(path, sep=';')
            df = df.rename(columns={importer_col: 'country', qty_col: 'quantity_exported'})
            df = df[['country', 'quantity_exported']].iloc[0:10].copy()
            df['quantity_exported'] = pd.to_numeric(df['quantity_exported'], errors='coerce')
            return df
        
        df_usa_s = load_and_subset("https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/US%20clothing%20waste%20exports%202023.csv", 'Importers', 'Quantity_exported_2023')
        df_china_s = load_and_subset("https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/China%20clothing%20waste%20exports%202023.csv", 'country', 'quantity_exported')
        df_india_s = load_and_subset("https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/India%20clothing%20waste%20exports%202023.csv", 'country', 'quantity_exported')
        df_italy_s = load_and_subset("https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/Italy%20clothing%20waste%20exports%202023.csv", 'country', 'quantity_exported')
        df_germany_s = load_and_subset("https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Waste%20Export%20Data/Germany%20clothing%20waste%20exports%202023.csv", 'country', 'quantity_exported')

        origin_coords_usa = get_coords("United States")
        origin_coords_china = get_coords("China")
        origin_coords_india = get_coords("India")
        origin_coords_italy = get_coords("Italy")
        origin_coords_germany = get_coords("Germany")

        def get_country_coords(df):
            return {row['country']: get_coords(row['country']) for _, row in df.iterrows() if get_coords(row['country'])}

        country_coords_usa = get_country_coords(df_usa_s)
        country_coords_china = get_country_coords(df_china_s)
        country_coords_india = get_country_coords(df_india_s)
        country_coords_italy = get_country_coords(df_italy_s)
        country_coords_germany = get_country_coords(df_germany_s)

        origin_selection = st.selectbox(
            label='Origin:',
            options=['All', 'United States', 'China', 'India', 'Italy', 'Germany'],
            index=0 
        )

        def create_map(selected_origin):
            m = folium.Map(location=[20, 0], zoom_start=2.1, tiles='cartodb positron')

            def get_color(qty):
                if qty > 100000:
                    return "#22223B"
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
                    return {'fillColor': '#4062BB', 'color': 'none', 'weight': 0, 'fillOpacity': 0.6}
                else:
                    return {'fillColor': 'none', 'color': 'none', 'weight': 0, 'fillOpacity': 0}

            folium.GeoJson(world_geo, style_function=style_function).add_to(m)

            for origin_coords, df, country_coords, country_name in countries_data:
                if selected_origin != 'All' and selected_origin != country_name:
                    continue
                if origin_coords is None:
                    continue

                popup_html = folium.Popup(
                    f"<div style='font-size:14px'><b>{country_name}</b><br>Total Exported: {df['quantity_exported'].sum():,.0f} Tons 🚢</div>",
                    max_width=250
                )
                folium.CircleMarker(
                    location=origin_coords,
                    radius=7.8,
                    color='#D96C06',
                    weight=2,
                    fill=True,
                    fill_color='#D96C06',
                    fill_opacity=0.9,
                    popup=popup_html
                ).add_to(m)

                for idx, row in df.iterrows():
                    dest_country = row['country']
                    qty = row['quantity_exported']
                    dest_coords_raw = country_coords.get(dest_country)
                    if dest_coords_raw:
                        offset_lat = 0.5 * ((idx % 3) - 1)
                        offset_lon = 0.5 * (((idx + 1) % 3) - 1)
                        dest_coords = [
                            dest_coords_raw[0] + offset_lat,
                            dest_coords_raw[1] + offset_lon
                        ]
                        AntPath(
                            locations=[origin_coords, dest_coords],
                            color=get_color(qty),
                            weight=3,
                            delay=800,
                            dash_array=[8, 20],
                            pulse_color='white'
                        ).add_to(m)

                        popup_html = f"<b>{dest_country}</b>: {qty:,.0f} Tons ⚠️"
                        folium.CircleMarker(
                            location=dest_coords,
                            radius=4,
                            color='#A3C9A8',
                            fill=True,
                            fill_color='#A3C9A8',
                            fill_opacity=0.7,
                            popup=folium.Popup(popup_html, max_width=250)
                        ).add_to(m)

            legend_html = """
            <div style="
                position: fixed;
                bottom: 50px; left: 50px; width: 200px; height: 100px;
                background-color: white;
                border:2px solid grey;
                z-index:9999;
                font-size:14px;
                padding: 10px;
            ">
            <b>Export Quantity</b><br>
            <i style="background:#3A506B; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> > 100,000 Tons<br>
            <i style="background:#D98C5F; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> 40,000–100,000 Tons<br>
            <i style="background:#8A9A5B; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> < 40,000 Tons
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
            return m

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
        textile_exp_df = pd.read_csv('Textile_Waste_Exports.csv')

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
            marker_color='#3A506B'
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
                x=-0.05,
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
            x=agg['Textile Type'],
            y=agg['Export Value (USD)'],
            marker_color='#3A506B',
            text=[f"${v:,.0f}" for v in agg['Export Value (USD)']],
            textposition='outside',
            hovertemplate='%{x}: %{y:,.0f} USD<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text='<b>Total Export Value per Textile Type</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=22, color='#3A506B', family='Montserrat, Montserrat, sans-serif')
            ),
            height=600,
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                title='<b>Total Export Value (USD)</b>',
                title_font=dict(size=16, color='#3A506B', family='Montserrat, sans-serif')
            ),
            xaxis=dict(
                showgrid=False,
                automargin=True,
                title='',
                tickfont=dict(size=14, color='#3A506B', family='Montserrat, sans-serif')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14, family='Montserrat, sans-serif', color='#3A506B'),
            margin=dict(l=80, r=40, t=100, b=80),
            bargap=0.3,
            showlegend=False
        )

        fig.update_traces(
            marker_line_width=0,
            textfont=dict(
                family='Montserrat, sans-serif',
                size=12,
                color='#3A506B',
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

        textile_exp_df = pd.read_csv('Textile_Waste_Exports.csv')

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
                x=0.1,
                y=1.05,
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
        <div style="text-align:center; color:#D98C5F;">
            <h2><b>Explore India</b></h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### **India's Textile Shipments Network**")
        india_shipments_df = pd.read_csv('India_Shipments.csv')

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
                    color = '#D98C5F',
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
            background-color: #D98C5F;
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

    if map_choice == "Top Countries Importing the Most Textile Waste" and country_choice == "All":
        st.markdown('''
                <h3>
                   The main importers are often developing or manufacturing-focused countries. They import textile waste for recycling, reprocessing, or resale, indicating a global redistribution of waste materials for economic use or disposal.</h3>
                    ''', unsafe_allow_html=True)
        
        ##### WASTE IMPORTERS #####
        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Textile_Waste_Imports.csv')

        focus_countries = ['United States of America', 'China', 'Netherlands', 'Mexico', 'Russian Federation']
        df = df[df['Importer Country'].isin(focus_countries)]

        df['Import Value (USD)'] = pd.to_numeric(df['Import Value (USD)'], errors='coerce').fillna(0)

        waste_types = df['Textile Type'].unique()

        def get_country_imports(waste_type=None):
            if waste_type is None:  
                d = df.groupby('Importer Country')['Import Value (USD)'].sum()
            else:
                d = df[df['Textile Type'] == waste_type].groupby('Importer Country')['Import Value (USD)'].sum()
            return d.reindex(focus_countries, fill_value=0)

        dropdown_options = [('**Textile Waste**', None)] 
        dropdown_options += [(wt, wt) for wt in waste_types]

        bar_data = []
        x_labels = []
        for label, wt in dropdown_options:
            imports = get_country_imports(wt)
            sorted_imports = imports.sort_values(ascending=False)
            bar_data.append(sorted_imports.values)
            x_labels.append(sorted_imports.index)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x_labels[0],
            y=bar_data[0],
            marker_color='#3A506B'
        ))

        buttons = []
        for i, (label, wt) in enumerate(dropdown_options):
            clean_label = label.replace('**', '<b>').replace('**', '</b>')
            buttons.append(dict(
                label=clean_label,
                method='update',
                args=[
                    {'y': [bar_data[i]], 'x': [x_labels[i]]},
                    {'title': f"Top 5 Textile Waste Importers: focus on {clean_label}"}
                ]
            ))

        fig.update_layout(
            updatemenus=[dict(
                buttons=buttons,
                direction='down',
                showactive=True,
                x=-0.05,
                xanchor='left',
                y=1.15,
                yanchor='top'
            )],
            title="Top 5 Textile Waste Importers",
            title_x=0.5,
            yaxis_title='Total Import Value (USD)',
            xaxis_title='Country'
        )

        st.plotly_chart(fig)

        st.markdown('''
                <h3>
                    <span style= font-weight:bold;'>Social and Economic Impacts</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        st.markdown('''
        - **Secondary Markets**: Many importing countries have large markets for second-hand clothing and textiles, which provide affordable apparel to local populations and support jobs in sorting, resale, and repair industries.
        - **Industrial Reuse**: Some textile waste is processed for industrial applications, such as insulation, cleaning rags, or recycled fibers for new products.
        ''')

        ##### TEXTILE WASTE TYPE IMPORTED #####

        agg = df.groupby('Textile Type')['Import Value (USD)'].sum().reset_index()

        agg = agg.dropna(subset=['Import Value (USD)'])

        agg = agg.sort_values('Import Value (USD)', ascending=False)

        fig = go.Figure(go.Bar(
            x=agg['Textile Type'],
            y=agg['Import Value (USD)'],
            marker_color='#3A506B',
            text=[f"${v:,.0f}" for v in agg['Import Value (USD)']],
            textposition='outside',
            hovertemplate='%{x}: %{y:,.0f} USD<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text='<b>Total Import Value per Textile Type</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=22, color='#3A506B', family='Montserrat, Montserrat, sans-serif')
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                title='<b>Total Import Value (USD)</b>',
                title_font=dict(size=16, color='#3A506B', family='Montserrat, sans-serif')
            ),
            xaxis=dict(
                showgrid=False,
                automargin=True,
                title='',
                tickfont=dict(size=14, color='#3A506B', family='Montserrat, sans-serif')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14, family='Montserrat, sans-serif', color='#3A506B'),
            margin=dict(l=80, r=40, t=100, b=80),
            bargap=0.3,
            showlegend=False
        )

        fig.update_traces(
            marker_line_width=0,
            textfont=dict(
                family='Montserrat, sans-serif',
                size=12,
                color='#3A506B',
            )
        )

        st.plotly_chart(fig)

        st.markdown('''
                <h3>
                    <span style= font-weight:bold;'>Environmental and Infrastructural Challenges</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        st.markdown('''
        - **Waste Management Strain**: In many developing countries (e.g., Ghana, Kenya), the volume and low quality of imported textiles far exceed local demand or recycling capacity. As a result, a significant portion ends up in landfills, open dumps, or is burned, causing severe environmental and health risks.
        - **Pollution**: Decomposing textiles can release toxic chemicals, microplastics, and greenhouse gases, polluting air, soil, and water. Inadequate waste infrastructure exacerbates these impacts.
        - **Flooding and Disease**: Textile waste can clog drainage systems, increasing the risk of flooding and waterborne diseases in urban areas.
        ''')

        ##### LINE GRAPH TEXTILE TYPES #####

        df['Import Value (USD)'] = pd.to_numeric(df['Import Value (USD)'], errors='coerce')

        countries = ['United States of America', 'China', 'Netherlands', 'Mexico', 'Russian Federation']
        df = df[df['Importer Country'].isin(countries)]

        textile_types = df['Textile Type'].unique()

        fig = go.Figure()

        traces_per_type = []
        for ttype in textile_types:
            traces = []
            for country in countries:
                subset = df[(df['Textile Type'] == ttype) & (df['Importer Country'] == country)]
                traces.append(go.Scatter(
                    x=subset['Year'],
                    y=subset['Import Value (USD)'],
                    mode='lines+markers',
                    name=country
                ))
            traces_per_type.append(traces)

        for trace in traces_per_type[0]:
            fig.add_trace(trace)

        buttons = []
        for i, ttype in enumerate(textile_types):
            args = [
                {'y': [traces_per_type[i][j].y for j in range(len(countries))],
                'x': [traces_per_type[i][j].x for j in range(len(countries))]},
                {'title': f'Import Value Over Time: {ttype}'}
            ]
            buttons.append(dict(
                label=ttype,
                method='update',
                args=args
            ))

        fig.update_layout(
            updatemenus=[dict(
                type="dropdown",
                direction="down",
                buttons=buttons,
                x=0.1,
                y=1.05,
                showactive=True
            )],
            title=f'Import Value Over Time: {textile_types[0]}',
            xaxis_title='Year',
            yaxis_title='Import Value (USD)',
        )
    
        st.plotly_chart(fig)

        st.markdown('''
                <h3>
                    <span style= font-weight:bold;'>Policy and Regulatory Context</span> 
                    </h3>
                    ''', unsafe_allow_html=True)
        st.markdown('''
        - **Trade Restrictions**: Some countries (e.g., Rwanda, Kenya, Tanzania, Uganda, Burundi) have implemented or attempted bans on used clothing imports to protect local industries and reduce environmental harm.
        - **EU Policy Changesn**: The European Union is moving toward stricter controls on textile waste exports, particularly to non-OECD countries, to address the negative impacts of waste dumping abroad and to promote circular economy practices within the EU. 
        ''')

        st.markdown('''
                <h4>
                    <span style='background-color:#D98C5F; font-weight:bold;'>
                    In essence, the global textile waste trade is both an opportunity and a challenge-supporting reuse and recycling but also risking environmental and social harm if not managed responsibly.
                    </span> 
                </h4>
                ''', unsafe_allow_html=True)




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
