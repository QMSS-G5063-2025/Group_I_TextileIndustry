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
        country_choice = st.sidebar.selectbox(
        "Explore a country",
        ["All"] + relevant_countries
    )
    else:
        relevant_countries = (
            top_export_waste_countries 
            if map_choice == "Top Countries Exporting the Most Textile Waste" 
            else top_import_waste_countries
        )
        country_choice = "All"



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

            color_map = {
                'Top 5': 'rgba(163, 201, 168, 0.9)', 
                'Other': 'rgba(217, 140, 95, 0.9)'     
            }

            fig = px.choropleth(
                df_no_world,
                locations='Importers',
                locationmode='country names',
                color='Highlight',
                color_discrete_map=color_map,
                animation_frame='Year',
                hover_name='Importers',
                title='Global Apparel Imports in USD (2005–2024)',
                width=1400,
                height=800
            )

            fig.update_traces(
                customdata=np.stack((df_no_world['Apparel_Imports'], df_no_world['Year']), axis=-1),
                hovertemplate=(
                    "<b>%{hovertext}</b><br>" +
                    "Apparel Imports: <b>$%{customdata[0]:,.2f}</b><br>" +
                    "Year: %{customdata[1]:.0f}<extra></extra>"
                )
            )

            fig.update_geos(
                fitbounds='locations',
                showcountries=True,
                showcoastlines=False,
                showframe=False,
                showland=True,
                landcolor='rgba(234, 224, 213, 0.9)',
                lakecolor='rgb(220, 228, 235)',
                oceancolor='rgb(236, 236, 236)',
                bgcolor='rgb(220, 228, 235)',
                projection_type='natural earth'
            )

            fig.update_layout(
                title=dict(
                    text="Global Apparel Imports in USD (2005-2024)",
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=24, color='#3A506B', family='Montserrat, sans-serif')
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

            # st.markdown('''The map above illustrates the total value of apparel imports (in thousands of US dollars) by country, 
            #             including crocheted and knitted apparel, not crocheted and knitted apparel as well as other made up textiles articles. 
            #             The top five importing countries, the United States, France, Germany, the United Kingdom, and Japan, are highlighted in 
            #             yellow, consistently ranking as the largest importers of apparel from 2005 to the present. The varying shades of blue are 
            #             due to missing data.''')

            st.markdown('''This map spotlights the world’s top apparel importers, highlighting the United States, France, Germany, the United Kingdom, 
            and Japan as the five countries bringing in the highest value of apparel goods (measured in thousands of US dollars). 
            Understanding which countries dominate apparel imports is crucial because it not only reveals where global demand is 
            concentrated, but also which economies drive the production and movement of clothing worldwide. The international flow of 
            apparel is one of many crucial factors that shape the global textile and apparel industry, impacting everything from [manufacturing locations](https://www.royaleuropetextile.com/top-10-textile-manufacturing-countries-in-the-world-fy-2024-update/) 
            to labor practices and environmental sustainabilty.''')
        
            ### time series line graph ###
            top_countries = ['United States of America', 'France', 'Japan', 'Germany', 'United Kingdom'] 
            country_colors = {
                'United States of America': '#3A506B',
                'France': '#D98C5F',
                'Japan': '#EAE0D5',
                'Germany': '#8A9A5B',
                'United Kingdom': '#B7B7D7'
            }

            line_df = apparel_imports_df[apparel_imports_df['Importers'].isin(top_countries)]

            fig = go.Figure()

            for country in top_countries:
                cdf = line_df[line_df['Importers'] == country]
                fig.add_trace(
                    go.Scatter(
                        x=cdf['Year'],
                        y=cdf['Apparel_Imports'],
                        mode='lines',
                        name=country,
                        line=dict(color=country_colors.get(country, '#3A506B'), width=2)
                    )
                )

            # Apply the exact same layout as your reference code
            fig.update_layout(
                title=dict(
                    text='<b>Apparel Imports Evolution for Top 5 Countries</b>',
                    x=0.5,
                    xanchor='center',
                    font=dict(family='Montserrat, sans-serif', color='#3A506B', size=22)
                ),
                yaxis=dict(
                    title='Total Apparel Imports (USD)',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.5)',
                    zeroline=False
                ),
                xaxis=dict(
                    title='Year',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.5)'
                ),
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
                margin=dict(t=100, b=100),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)


            st.markdown('''The significance of tracking apparel imports goes beyond trade statistics. High import volumes are closely tied 
            to patterns of mass consumption, “fast fashion,” and the environmental footprint of the apparel industry. Research shows 
            that consumption rates in developed economies like the US and Western Europe have a profound impact on global greenhouse gas [emissions](https://dash.harvard.edu/entities/publication/191f53b7-acf6-424a-a306-b006b8a4e3f3), 
            immense textile [waste generation](https://www.fibre2fashion.com/industry-article/10157/sustainability-challenges-in-the-global-textile-industry-analysing-waste-management-and-resource-eff), and resource use throughout the textile value chain. The demand from these top importers fuels production surges in 
            manufacturing hubs, often in developing countries (see importers/exporters network graphs below), amplifying the industry’s challenges with sustainability, 
            waste, and social responsibility.''')


            st.markdown("---")
            st.markdown("<h2 style='text-align:center;'>Consumer Behavior</h2>", unsafe_allow_html=True)

            # st.markdown('''We decided to analyse consumer interest in fast fashion versus more sustainable alternatives by focusing on the top five apparel-importing countries and using Google search trends as a proxy for consumer demand.''')
            # st.write('''For each country, we compared search volumes for leading fast fashion brands with terms representing second-hand and 
            #          more sustainable shopping options. To ensure relevance, we tailored the keywords and brand selections to reflect the most 
            #          commonly used terms and popular platforms in each country.''')
            # st.markdown("""
            # - For Japan, for example, we conducted searches using the Japanese equivalents of “thrift” and “Shein,” then translated the results for consistency in our analysis.
            # """)

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
                                mode='lines',
                                name=f"{keyword}",
                                line=dict(color=line_colors[keyword], width=2),
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
                            mode='lines',
                            name=f"{keyword}",
                            line=dict(color=line_colors[keyword], width=2),
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


            st.markdown('''Utilizing Google Trends methodology, the above showcases consumer interest in different fashion brands
             measured by the number of related Google searches. We specifically identify fast fashion chains and compare rates to
              sustainable alternatives, focusing on the top five apparel-importing countries. Although Google Trends is a mere
               proxy measure of consumer demand, it provides a relatively good understanding of what kinds of brands are driving
                global trends in sustainable vs. fast fashion.''')

            # st.write('''While Google search trends provide a practical way to approximate consumer interest, 
            #          this method has several important limitations:''')
            # st.markdown("""
            # - Search data can be biased, particularly when comparing online-only brands to brick-and-mortar alternatives, 
            #             as consumer discovery and engagement differ between digital and physical retail.
            # - Trends reflect search intent & curiosity —- not purchasing behavior.
            # - Increasing internet access and growth of e-commerce over time can distort long-term trends, 
            #             especially in the earlier years of the dataset.
            # - Some brands, like Shein (founded in 2008), did not exist before certain dates, so search interest prior to their 
            #             launch is not meaningful and has been excluded from our analysis.
            # """)
            # st.write('''Despite these caveats, Google search data offers a useful - if imperfect - means of gauging shifts 
            #          in consumer interest between fast fashion and more sustainable shopping options over time.''')

            st.markdown("""
            <div style="
                background-color: rgba(255, 255, 255, 0.75); 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                font-size: 16px;
            ">
            <p><strong>While Google search trends provide a practical way to approximate consumer interest, 
            this method has several important limitations:</strong></p>

            <ul>
                <li>Search data can be biased, particularly when comparing online-only brands to brick-and-mortar alternatives, 
                    as consumer discovery and engagement differ between digital and physical retail.</li>
                <li>Trends reflect search intent & curiosity — not purchasing behavior.</li>
                <li>Increasing internet access and growth of e-commerce over time can distort long-term trends, 
                    especially in the earlier years of the dataset.</li>
                <li>Some brands, like Shein (founded in 2008), did not exist before certain dates, so search interest prior to their 
                    launch is not meaningful and has been excluded from our analysis.</li>
            </ul>

            <p>Despite these caveats, Google search data offers a useful — if imperfect — means of gauging shifts 
            in consumer interest between fast fashion and more sustainable shopping options over time.</p>
            </div>
            """, unsafe_allow_html=True)


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
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
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
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
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
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
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
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
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
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
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
        <h4>
            According to Businesswaste.co.uk, United States, China, India, Italy, and Germany export the most textile waste 
            <a href="https://www.businesswaste.co.uk/your-waste/textile-recycling/fashion-waste-facts-and-statistics/#:~:text=China%20and%20the%20USA%20are,the%20way%20across%20the%20continent" target="_blank">globally</a>. 
            In the following visualizations we highlight four of some of the most common types of textile waste: 
            <span style='background-color:#D98C5F; font-weight:bold;'>silk, wool, rags, and worn clothes.</span> 
            Specifications can be traced from leftover textile manufacturing fabrics (notably silk and wool waste), every-day 
            household supplies (cleaning/used rags), and consumer behavioral habits resulting in high clothing waste (i.e., 
            worn clothes).
        </h4>
        ''', unsafe_allow_html=True)

        st.markdown('''
        _A breakdown of our textile waste data:_

        - **Silk Waste**: Leftover or unusable pieces from silk production.  
        - **Wool Waste**: Scraps from wool processing or discarded woolen goods.  
        - **Rags**: Old textiles, often used for industrial cleaning or recycling.  
        - **Worn Clothes**: Used clothing collected for resale, reuse, or recycling.
        ''')
        
        st.markdown("""
        <div style="
            background-color: rgba(255, 255, 255, 0.75); 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.2); 
            font-size: 16px;
        ">
        It is important to note that our waste categories represent a mere fraction of the total textile waste generated across select countries. In reality, this snapshot does not account for the plethora of different kinds of textile waste that exists in landfills. Nevertheless, our estimates provide a robust and reliable comparison using available data.
        </div>
        """, unsafe_allow_html=True)


        st.markdown('''
        _Why Do Countries Export Textile Waste?_

        - **Waste Diversion**: Exporting waste helps reduce the amount sent to local landfills or incinerators.  
        - **Resource Efficiency**: Reusing or recycling clothing abroad can reduce the environmental impact by up to 70% compared to making new textiles.  
        - **Global Redistribution**: Exported textiles are often reused in lower- and middle-income countries, providing affordable clothing and supporting local economies.  
        - **Job Creation**: The trade in used textiles supports jobs in recipient countries, such as market sellers and recyclers.  
        ''')
        # st.markdown('''
        #         <h4>
        #             We focus on 
        #             <span style='background-color:#D98C5F; font-weight:bold;'>silk waste, rags, wool waste, and worn clothes</span> 
        #             as our primary metrics for textile waste. While these represent only a subset of global textile waste and doesn't
        #             capture the full diversity of textile waste, they offer a consistent and reliable basis for comparison given current data limitations.
        #             </h4>
        #             ''', unsafe_allow_html=True)
        
#         st.write('''These categories cover a broad spectrum of textile waste, from manufacturing by-products (silk and wool waste) to post-consumer items (worn clothes, rags), 
#                 reflecting both industrial and household contributions to textile waste flows. 

#                     Textile Waste metric is calculated as sum(silk waste + wool waste + rags + worn clothes)  

# - Silk Waste: By-products and unusable remnants from silk production and processing.
# - Rags: Discarded textiles, often cut or sorted for industrial cleaning or recycling.
# - Wool Waste: Scraps and leftovers from wool processing or discarded woolen goods.
# - Worn Clothes: Used clothing, typically collected for resale, reuse, or recycling.
#     ''')
        
#         st.markdown('''
#                 <h4>
#                     The United States, China, India, Italy, and Germany - all developed countries - are the largest exporters of textile waste. 
#                     This reflects high levels of textile consumption, efficient collection systems, and established waste management policies
#                     </h4>
#                     ''', unsafe_allow_html=True)
        

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

        st.markdown('''Here we see the total export value (in USD) of textile waste from the top five exporting countries: _United States of America, Germany, China, Italy, and India_. To reiterate, tracking waste export values is vital to cast light on the largest contributors to the global stream of textile waste, which environmentally and economically impacts exporters and importers alike.
        ''')

        # st.markdown('''
        #         <h3>
        #             <span style = font-weight:bold;'>Environmental Implications</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        
        # st.markdown('''
        #         - **Waste Diversion**: Exporting textile waste helps divert large quantities from domestic landfills and incinerators, potentially reducing environmental burdens at home.
        #         - **Resource Efficiency**: By extending the life cycle of clothing through reuse and recycling abroad, these exports lower the carbon and water footprint compared to producing new textiles-emissions can be reduced by up to 70%.
        #         - **Global Redistribution**: Much of the exported textile waste is reused in lower- and middle-income countries, providing affordable clothing and supporting local economies.
        #          ''')
        
        ####### TEXTILE EXPORTS BAR GRAPH #######
        textile_exp_df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Textile_Waste_Exports.csv')

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
        bar_texts = []
        for label, wt in dropdown_options:
            values = get_focus_values(wt)
            bar_data.append(values.values)
            x_labels.append(values.index)
            bar_texts.append([f"${v:,.0f}" for v in values.values])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x_labels[0],
            y=bar_data[0],
            marker_color='#3A506B',
            text=bar_texts[0],
            textposition='outside',
            hovertemplate='%{x}: %{y:,.0f} USD<extra></extra>'
        ))

        buttons = []
        for i, (label, wt) in enumerate(dropdown_options):
            clean_label = label.replace('**', '<b>').replace('**', '</b>')
            buttons.append(dict(
                label=clean_label,
                method='update',
                args=[
                    {'y': [bar_data[i]], 'x': [x_labels[i]], 'text': [bar_texts[i]]},
                    {'title': f"<b>Top 5 Textile Waste Exporters: focus on {clean_label}</b>"}
                ]
            ))

        fig.update_layout(
            height = 600,
            updatemenus=[dict(
                buttons=buttons,
                direction='down',
                showactive=True,
                x=-0.05,
                xanchor='left',
                y=1.15,
                yanchor='top'
            )],
            title=dict(
                text='<b>Top 5 Textile Waste Exporters</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=22, color='#3A506B', family='Montserrat, Montserrat, sans-serif')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                automargin=True,
                tickfont=dict(size=14, color='#3A506B', family='Montserrat, sans-serif')
            ),
            margin=dict(l=80, r=40, t=100, b=80),
            bargap=0.3,
            showlegend=False
        )

        st.plotly_chart(fig)

        # st.markdown('''
        #         <h3>
        #             <span style= font-weight:bold;'>Social and Economic Impacts</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        # st.markdown('''
        # - **Job Creation**: The trade in used textiles supports thousands of jobs in receiving countries, both in formal and informal sectors. For example, Nordic exports alone are estimated to support over 10,000 market sellers in Africa.
        # - **Access to Affordable Clothing**: Imports of used clothing make apparel more affordable in importing countries, though there are concerns about negative impacts on local textile industries.
        # ''')

        ##### top 5 textile waste exporters #####
        textile_exp_df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Textile_Waste_Exports.csv')

        agg = textile_exp_df.groupby('Textile Type')['Export Value (USD)'].sum().reset_index()

        agg = agg.dropna(subset=['Export Value (USD)'])

        agg = agg.sort_values('Export Value (USD)', ascending = False)

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
                showgrid=True,
                zeroline=False,
                showticklabels=True,
                title='<b>Total Export Value (USD)</b>',
                title_font=dict(size=16, color='#3A506B', family='Montserrat, sans-serif')
            ),
            xaxis=dict(
                showgrid=True,
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

        st.markdown('''The above chart measuring ‘Total Value per Textile Type,’ breaks down the global export value (in USD) for different categories of textile waste: 
        _Worn Clothes, Used/New Rags, Wool Waste, and Silk Waste_. Interestingly, we see that worn clothes dominate textile waste exports by a significant margin, 
        with a total export value exceeding \\$151 million. Used and new rags follow distantly at around \\$21.7 million, while wool waste and silk waste account 
        for much smaller shares, at \\$3.7 million and \\$3.1 million, respectively.''')

        # st.markdown('''
        #         <h3>
        #             <span style= font-weight:bold;'>Challenges and Risks</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        # st.markdown('''
        # - **Waste Transfer**: There is ongoing debate about whether this practice truly supports circularity or simply shifts the waste problem to countries with less capacity for responsible disposal or recycling. In many cases, textiles that cannot be reused eventually end up in landfills or are openly burned in recipient countries, especially in Africa and Asia.
        # - **Regulatory Scrutiny**: Growing environmental concerns have led some governments (e.g., Sweden, Denmark, France) to propose stricter regulations on textile waste exports, aiming to ensure that exports do not simply offload environmental burdens onto less-equipped nations.
        # ''')

        #### total export value per textile type ####

        textile_exp_df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Textile_Waste_Exports.csv')

        countries = [
            'United States of America',
            'France',
            'Japan',
            'Germany',
            'United Kingdom'
        ]
        textile_exp_df = textile_exp_df[textile_exp_df['Exporter Country'].isin(countries)]
        textile_exp_df['Export Value (USD)'] = pd.to_numeric(textile_exp_df['Export Value (USD)'], errors='coerce')
        textile_types = textile_exp_df['Textile Type'].unique()

        country_colors = {
            'United States of America': '#3A506B',
            'France': '#D98C5F',
            'Japan': '#EAE0D5',
            'Germany': '#8A9A5B',
            'United Kingdom': '#B7B7D7'
        }

        # ---------- Trace Construction ----------
        traces_per_type = []
        for ttype in textile_types:
            traces = []
            for country in countries:
                subset = textile_exp_df[(textile_exp_df['Textile Type'] == ttype) & (textile_exp_df['Exporter Country'] == country)]
                traces.append(go.Scatter(
                    x=subset['Year'],
                    y=subset['Export Value (USD)'],
                    mode='lines',  # Only lines, no markers
                    name=country,
                    line=dict(color=country_colors[country], width=2),
                    visible=(ttype == textile_types[0])
                ))
            traces_per_type.extend(traces)

        # ---------- Figure and Dropdown ----------
        fig = go.Figure(data=traces_per_type)

        buttons = []
        for i, ttype in enumerate(textile_types):
            vis = [False] * len(traces_per_type)
            for j in range(len(countries)):
                vis[i * len(countries) + j] = True
            buttons.append(dict(
                label=ttype,
                method='update',
                args=[
                    {'visible': vis},
                    {'title': f'<b>Export Value Over Time: {ttype}</b>'}
                ]
            ))

        fig.update_layout(
            template='plotly_white',
            updatemenus=[dict(
                type="dropdown",
                direction="down",
                buttons=buttons,
                x=0.1,
                y=1.15,
                showactive=True,
                bgcolor='white',
                bordercolor='#3A506B',
                font=dict(size=12, color='#3A506B')
            )],
            title=dict(
                text=f'<b>Export Value Over Time: {textile_types[0]}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=22)
            ),
            xaxis=dict(
                title='Year',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
            ),
            yaxis=dict(
                title='Export Value (USD)',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
            ),
            legend=dict(
                orientation='h',
                y=-0.2,
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
            margin=dict(t=120, b=80),
            hovermode='closest'
        )


        st.plotly_chart(fig)

        st.markdown('''This chart complements the previous one, providing a time-series analysis of silk waste export values from 2004 to 2025 for major exporting countries: _United States, China, India, Italy, and Germany._''')


        # st.markdown('''<i>*"Exporting used textiles is a fundamental part of the textile circular economy-an approach 
        #             that minimizes waste by keeping products in use for as long as possible. Rather than discarding 
        #             garments into landfills or incinerators, exporting worn clothing extends their life cycle, 
        #             reduces environmental impact, and creates economic opportunities."*</i>''', unsafe_allow_html = True)


    ### Conditional Network Visualization (India textile shipments) ###
    # if map_choice == "Top Countries Exporting the Most Textile Waste" and country_choice == "India":
    #     st.markdown("---")
    #     st.markdown("""
    #     <div style="text-align:center; color:#D98C5F;">
    #         <h2><b>Explore India</b></h2>
    #     </div>
    #     """, unsafe_allow_html=True)

    #     st.markdown("### **India's Textile Shipments Network**")
    #     india_shipments_df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/India_Shipments.csv')

    #     country_coords = {
    #         'India': [20.5937, 78.9629],
    #         'United States': [37.0902, -95.7129],
    #         'Canada': [56.1304, -106.3468],
    #         'China': [35.8617, 104.1954],
    #         'South Korea': [35.9078, 127.7669],
    #         'Netherlands': [52.1326, 5.2913],
    #         'Slovenia': [46.1512, 14.9955],
    #         'Indonesia': [0.7893, 113.9213],
    #         'Colombia':[4.5709, -74.2973],
    #         'Ethiopia': [9.1450, 40.4897],
    #         'Japan': [36.2048, 138.2529],
    #         'Philippines': [12.8797, 121.7740],
    #         'Poland': [51.9194, 19.1451],
    #         'Dominican Republic': [18.7357, -70.1627],
    #         'Germany': [51.1657, 10.4515],
    #         'Taiwan': [23.6978, 120.9605],
    #         'Spain': [40.4637, -3.7492],
    #         'Saudi Arabia': [23.8859, 45.0792],
    #         'Brazil': [-14.2350, -51.9253],
    #     }

    #     m2 = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')

    #     india_lat, india_lon = country_coords['India']

    #     for idx, row in india_shipments_df.iterrows():
    #         destination = row['Destination']
    #         qty = row['Qty']

    #         # Check if destination exists in our coordinates dictionary
    #         if destination in country_coords:
    #             dest_lat, dest_lon = country_coords[destination]

    #             # Add destination marker
    #             folium.CircleMarker(
    #                 location=[dest_lat, dest_lon],
    #                 radius=4,
    #                 color='#A3C9A8',
    #                 fill=True,
    #                 fill_opacity=1,
    #                 #tooltip=f"{destination}: {qty}",
    #                 popup=f"<b>{destination}</b><br>Quantity: {qty}"
    #             ).add_to(m2)

    #             # Add line from India to destination
    #             folium.PolyLine(
    #                 locations=[
    #                     [india_lat, india_lon],
    #                     [dest_lat, dest_lon]
    #                 ],
    #                 color = '#D98C5F',
    #                 weight = 3,
    #                 opacity = 0.4
    #             ).add_to(m2)

    #     folium.CircleMarker(
    #         location=[india_lat, india_lon],
    #         radius=10,
    #         color='#6C7A89',
    #         fill=True,
    #         fill_opacity=1,
    #         tooltip = 'India'
    #     ).add_to(m2)

    #     st_folium(m2, use_container_width=True, height=600)

    #     st.markdown("""
    #     | Abbreviation | Meaning | Description |
    #     |:------------|:---------|:------------|
    #     | **kgs** | Kilograms | Weight measurement: 1 kg = 1,000 grams |
    #     | **mts** | Metric Tons | Weight measurement: 1 metric ton = 1,000 kilograms |
    #     | **pcs** | Pieces | Count of individual items or garments |
    #     | **unt** | Units | General count of goods |
    #     """)


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
                The United States, China, Netherlands, Mexico, and Russia are the main importers of 
                <a href="https://www.volza.com/p/textile-waste/import/" target="_blank">
                textile waste</a>. These countries often import waste for recycling, reprocessing, or resale, showing how waste materials are redistributed globally for further use.
                </h3>
                ''', unsafe_allow_html=True)


        st.markdown('''
        _What Happens to Imported Textile Waste?_

        - Secondary Markets: Many importing countries have large markets for second-hand clothing, supporting local jobs and making clothing more affordable.  
        - Industrial Reuse: Some waste is processed into materials for insulation, cleaning rags, or recycled fibers for new products.
        ''')

        st.markdown('''
        _Environmental and Social Challenges_

        - Waste Management Strain: In some developing countries, the amount and quality of imported textiles exceed what can be reused or recycled. This leads to more waste ending up in landfills, open dumps, or being burned, which harms the environment and public health.
        - Pollution: Decomposing textiles can release harmful chemicals and microplastics, polluting air, soil, and water.
        - Flooding and Disease: Textile waste can block drainage systems, leading to flooding and increased risk of water-borne diseases.
        ''')

        st.markdown('''
        _Policy and Regulation_

        - Trade Restrictions: Some countries have banned or restricted used clothing imports to protect local industries and reduce environmental harm.
        - EU Policy Changes: The European Union is tightening controls on textile waste exports, especially to non-OECD countries, to prevent negative impacts and encourage recycling within the EU.
        ''')        

        ##### WASTE IMPORTERS #####
        df = pd.read_csv('https://raw.githubusercontent.com/QMSS-G5063-2025/Group_I_TextileIndustry/refs/heads/main/final_project/Textile_Waste_Imports.csv')

        focus_countries = ['United States of America', 'China', 'Netherlands', 'Mexico', 'Russian Federation']
        df = df[df['Importer Country'].isin(focus_countries)]

        df['Import Value (USD)'] = pd.to_numeric(df['Import Value (USD)'], errors='coerce').fillna(0)

        waste_types = df['Textile Type'].unique()

        # def get_country_imports(waste_type=None):
        #     if waste_type is None:  
        #         d = df.groupby('Importer Country')['Import Value (USD)'].sum()
        #     else:
        #         d = df[df['Textile Type'] == waste_type].groupby('Importer Country')['Import Value (USD)'].sum()
        #     return d.reindex(focus_countries, fill_value=0)

        # dropdown_options = [('**Textile Waste**', None)] 
        # dropdown_options += [(wt, wt) for wt in waste_types]

        # bar_data = []
        # x_labels = []
        # for label, wt in dropdown_options:
        #     imports = get_country_imports(wt)
        #     sorted_imports = imports.sort_values(ascending=False)
        #     bar_data.append(sorted_imports.values)
        #     x_labels.append(sorted_imports.index)

        # fig = go.Figure()

        # fig.add_trace(go.Bar(
        #     x=x_labels[0],
        #     y=bar_data[0],
        #     marker_color='#3A506B'
        # ))

        # buttons = []
        # for i, (label, wt) in enumerate(dropdown_options):
        #     clean_label = label.replace('**', '<b>').replace('**', '</b>')
        #     buttons.append(dict(
        #         label=clean_label,
        #         method='update',
        #         args=[
        #             {'y': [bar_data[i]], 'x': [x_labels[i]]},
        #             {'title': f"Top 5 Textile Waste Importers: focus on {clean_label}"}
        #         ]
        #     ))

        # fig.update_layout(
        #     updatemenus=[dict(
        #         buttons=buttons,
        #         direction='down',
        #         showactive=True,
        #         x=-0.05,
        #         xanchor='left',
        #         y=1.15,
        #         yanchor='top'
        #     )],
        #     title="Top 5 Textile Waste Importers",
        #     title_x=0.5,
        #     yaxis_title='Total Import Value (USD)',
        #     xaxis_title='Country'
        # )

        def get_country_imports(waste_type=None):
            if waste_type is None:  # Total
                d = df.groupby('Importer Country')['Import Value (USD)'].sum()
            else:
                d = df[df['Textile Type'] == waste_type].groupby('Importer Country')['Import Value (USD)'].sum()
            # Ensure all focus countries are present, fill missing with 0
            return d.reindex(focus_countries, fill_value=0)

        # Prepare data for dropdown options
        dropdown_options = [('**Textile Waste**', None)]  # Main total option
        dropdown_options += [(wt, wt) for wt in waste_types]

        bar_data = []
        x_labels = []
        bar_texts = []
        for label, wt in dropdown_options:
            imports = get_country_imports(wt)
            sorted_imports = imports.sort_values(ascending=False)
            bar_data.append(sorted_imports.values)
            x_labels.append(sorted_imports.index)
            bar_texts.append([f"${v:,.0f}" for v in sorted_imports.values])

        # Create the figure
        fig = go.Figure()

        # Add the initial (total) bar chart
        fig.add_trace(go.Bar(
            x=x_labels[0],
            y=bar_data[0],
            marker_color='#3A506B',
            text=bar_texts[0],
            textposition='outside',
            hovertemplate='%{x}: %{y:,.0f} USD<extra></extra>'
        ))

        # Dropdown menu buttons
        buttons = []
        for i, (label, wt) in enumerate(dropdown_options):
            clean_label = label.replace('**', '<b>').replace('**', '</b>')
            buttons.append(dict(
                label=clean_label,
                method='update',
                args=[
                    {'y': [bar_data[i]], 'x': [x_labels[i]], 'text': [bar_texts[i]]},
                    {'title': f"<b>Top 5 Textile Waste Importers: focus on {clean_label}</b>"}
                ]
            ))

        # Set up the dropdown menu and layout styling
        fig.update_layout(
            height = 600,
            updatemenus=[dict(
                buttons=buttons,
                direction='down',
                showactive=True,
                x=-0.05,
                xanchor='left',
                y=1.15,
                yanchor='top'
            )],
            title=dict(
                text='<b>Top 5 Textile Waste Importers</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=22, color='#3A506B', family='Montserrat, Montserrat, sans-serif')
            ),
            title_x=0.5,
            yaxis_title='Total Import Value (USD)',
            xaxis_title='Country',
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,246,250,0.3)',
            font=dict(
                family='Montserrat, sans-serif',
                color='#3A506B',
                size=12
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                zeroline=False
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)',
                automargin=True,
                tickfont=dict(size=14, color='#3A506B', family='Montserrat, sans-serif')
            ),
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

        st.markdown('''The graph above narrows in on the top 5 Textile Waste Importers, highlighting stark differences in the total import value ($USD) of textile waste. Such includes countries: _United States, China, Netherlands, Mexico, and the Russian Federation_. This metric is crucial for understanding international flows of discarded textiles, which has direct implications for waste management and recycling industries, in addition to all kinds of environmental challanges.''')


        # st.markdown('''
        #         <h3>
        #             <span style= font-weight:bold;'>Social and Economic Impacts</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        # st.markdown('''
        # - **Secondary Markets**: Many importing countries have large markets for second-hand clothing and textiles, which provide affordable apparel to local populations and support jobs in sorting, resale, and repair industries.
        # - **Industrial Reuse**: Some textile waste is processed for industrial applications, such as insulation, cleaning rags, or recycled fibers for new products.
        # ''')

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
            height = 600,
            title=dict(
                text='<b>Total Import Value per Textile Type</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=22, color='#3A506B', family='Montserrat, Montserrat, sans-serif')
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showticklabels=True,
                title='<b>Total Import Value (USD)</b>',
                title_font=dict(size=16, color='#3A506B', family='Montserrat, sans-serif')
            ),
            xaxis=dict(
                showgrid=True,
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

        st.markdown('''The above bar chart quantifies the total value (in USD) of different categories of textile waste imported globally: Worn Clothes, Used/New Rags, Wool Waste, and Silk Waste. These are some of the most comon types of textile waste products we see traversing the waste stream today.''')


        # st.markdown('''
        #         <h3>
        #             <span style= font-weight:bold;'>Environmental and Infrastructural Challenges</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        # st.markdown('''
        # - **Waste Management Strain**: In many developing countries (e.g., Ghana, Kenya), the volume and low quality of imported textiles far exceed local demand or recycling capacity. As a result, a significant portion ends up in landfills, open dumps, or is burned, causing severe environmental and health risks.
        # - **Pollution**: Decomposing textiles can release toxic chemicals, microplastics, and greenhouse gases, polluting air, soil, and water. Inadequate waste infrastructure exacerbates these impacts.
        # - **Flooding and Disease**: Textile waste can clog drainage systems, increasing the risk of flooding and waterborne diseases in urban areas.
        # ''')

        ##### LINE GRAPH TEXTILE TYPES #####

        df['Import Value (USD)'] = pd.to_numeric(df['Import Value (USD)'], errors='coerce')

        countries = ['United States of America', 'China', 'Netherlands', 'Mexico', 'Russian Federation']
        country_colors = {
            'United States of America': '#3A506B',
            'China': '#D98C5F',
            'Netherlands': '#EAE0D5',
            'Mexico': '#8A9A5B',
            'Russian Federation': '#B7B7D7'
        }
        df = df[df['Importer Country'].isin(countries)]

        textile_types = df['Textile Type'].unique()

        fig = go.Figure()

        traces_per_type = []
        for ttype in textile_types:
            for country in countries:
                subset = df[(df['Textile Type'] == ttype) & (df['Importer Country'] == country)]
                traces_per_type.append(go.Scatter(
                    x=subset['Year'],
                    y=subset['Import Value (USD)'],
                    mode='lines',
                    name=country,
                    line=dict(color=country_colors[country], width=2),
                    visible=(ttype == textile_types[0])
                ))

        # Dropdown buttons
        buttons = []
        for i, ttype in enumerate(textile_types):
            vis = [False] * len(traces_per_type)
            for j in range(len(countries)):
                vis[i * len(countries) + j] = True
            buttons.append(dict(
                label=ttype,
                method='update',
                args=[
                    {'visible': vis},
                    {'title': f'<b>Import Value Over Time: {ttype}</b>'}
                ]
            ))

        # Layout
        fig = go.Figure(data=traces_per_type)
        fig.update_layout(
            template='plotly_white',
            updatemenus=[dict(
                type='dropdown',
                direction='down',
                buttons=buttons,
                x=0.1,
                y=1.15,
                showactive=True,
                bgcolor='white',
                bordercolor='#3A506B',
                font=dict(size=12, color='#3A506B')
            )],
            title=dict(
                text=f'<b>Import Value Over Time: {textile_types[0]}</b>',
                x=0.5,
                xanchor='center',
                font=dict(family='Montserrat, sans-serif', color='#3A506B', size=22)
            ),
            xaxis=dict(
                title='Year',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
            ),
            yaxis=dict(
                title='Import Value (USD)',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.5)'
            ),
            legend=dict(
                orientation='h',
                y=-0.2,
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
            margin=dict(t=120, b=80),
            hovermode='closest'
        )

        st.plotly_chart(fig)

        st.markdown('''Shown over time, the above graph tracks the annual import value of silk waste from 2004 to 2025 for the five major importers: United States, China, Netherlands, Mexico, and Russian Federation''')

        # st.markdown('''
        #         <h3>
        #             <span style= font-weight:bold;'>Policy and Regulatory Context</span> 
        #             </h3>
        #             ''', unsafe_allow_html=True)
        # st.markdown('''
        # - **Trade Restrictions**: Some countries (e.g., Rwanda, Kenya, Tanzania, Uganda, Burundi) have implemented or attempted bans on used clothing imports to protect local industries and reduce environmental harm.
        # - **EU Policy Changesn**: The European Union is moving toward stricter controls on textile waste exports, particularly to non-OECD countries, to address the negative impacts of waste dumping abroad and to promote circular economy practices within the EU. 
        # ''')

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
    st.markdown("""
    Inspiration for this project lies around 5,000 miles (8,000 kilometers) away from New York City, 
    in one of the oldest and driest deserts in the world – the Atacama Desert in northern Chile. 
    From a distance, mounts of clothing and textile scraps seemingly blend in with the dunes and dry hills in the landscape. 
    From up close, bright colors begin to stand out from discarded ripped jeans, leather boots, heals and old bracelets against 
    the warm desert sand.
    """)

    st.markdown("""The _Cemetery of Clothes_, as the locals refer to it, is a reflection of the effects of overproduction, 
    fast fashion and a lack of policy regulations on the textile industry. An estimated **59,000 tons** of clothing and other 
    textiles are imported to Chile each year, of which almost **40,000 tons** deemed [irrecoverable](https://www.aljazeera.com/gallery/2021/11/8/chiles-desert-dumping-ground-for-fast-fashion-leftovers). 
    The growing piles permeate serious environmental impacts on the land, releasing toxic chemicals, like methane and formaldehyde,
     and contaminating the ground with imparishable microplastics. Fast fashion clothing is mainly made out of polyester 
     (plastic), which is [non-biodegradable](https://earth.org/fast-fashions-detrimental-effect-on-the-environment/). 
     With no proper management nor supervision, the Cemetery also presents an inevitable fire hazard as it spreads across 
     741 acres (300 hectares) of arid land.""")


    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://camo.githubusercontent.com/770c460a9993f2f0f4256c9498abc15698d1be5768d84b40344d5bea25dd23f9/68747470733a2f2f69636865662e626263692e636f2e756b2f6163652f77732f3830302f63707370726f6470622f414132332f70726f64756374696f6e2f5f3132323935353533345f61746163616d612d342e6a70672e77656270" width="900">
            <p style="font-size: 0.9em; color: gray;">The Cemetery of Clothes</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    This space was created with the objective of harnessing the power of data and visualization to facilitate understanding 
    of the contributors, dynamics, and nuances of a growingly underregulated industry. Information was gathered to show global
     textile trade and networks, consumer behaviour, and waste exports/exports. Our interactive graphs provide anyone the means 
     to engage with textile data at a deeper level. Our hope is that graphs not only highlight the major players fueling the 
     industry, but also encourage reflection on how consumption patterns in a handful of nations can influence envrionmental and 
     sustainability challenges experienced worldwide.
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
