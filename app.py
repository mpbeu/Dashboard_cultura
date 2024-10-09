import pandas as pd
import json
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


#path = "C:/Users/marc_/marcelo_drive/Cientista Chefe/Piloto dashboard/"
path = "files/"

df_mun = pd.read_excel(f"{path}Base municipios cultura.xlsx", sheet_name="Base municípios")
df_reg = pd.read_excel(f"{path}Base municipios cultura.xlsx", sheet_name="Base regiões")
df_est = pd.read_excel(f"{path}Base municipios cultura.xlsx", sheet_name="Base estado")



def indicadores(df):
    # Recursos Cultura
    df['Gasto municipal per capita com cultura'] = df['desp_cultura_percapita_real']

    # Equipamentos culturais por 100 mil habitantes
    df['Bibliotecas públicas por 100 mil hab.'] =  df['bibliotecas'] / df['populacao'] * 100000
    # df['Bibliotecas públicas por 100 mil hab.'] = df['Bibliotecas públicas por 100 mil hab.'].map('{:,.1f}'.format)

    df['Museus por 100 mil hab.'] =  df['museus'] / df['populacao'] * 100000
    # df['Museus por 100 mil hab.'] = df['Museus por 100 mil hab.'].map('{:,.1f}'.format)

    df['Teatros por 100 mil hab.'] =  df['teatros'] / df['populacao'] * 100000
    # df['Teatros por 100 mil hab.'] = df['Teatros por 100 mil hab.'].map('{:,.1f}'.format)

    df['Equipamentos por 100 mil hab.'] =  ( df['bibliotecas'] + df['museus'] + df['teatros'] ) / df['populacao'] * 100000
    # df['Equipamentos por 100 mil hab.'] = df['Equipamentos por 100 mil hab.'].map('{:,.1f}'.format)

    # Artes nas escolas
    df['Perc. alunos em escola com sala de artes'] = df['alunos_sala_artes'] / df['alunos_publico'] * 100
    df['Perc. alunos em escola com material de artes'] = df['alunos_material_artes'] / df['alunos_publico'] * 100
    df['Perc. alunos em escola com sala e material de artes'] = df['alunos_sala_material_artes'] / df['alunos_publico'] * 100

    df['Perc. alunos com disciplina de artes'] = df['alunos_discip_artes_2017'] / df['alunos_2017'] * 100
    df['Perc. alunos com atividade de artes'] = df['alunos_atividade_artes_2017'] / df['alunos_2017'] * 100

    # Economia da cultura
    df['Empresas do setor por mil hab.'] = df['empresas_cultura'] / df['populacao'] * 1000
    df['Empregados no setor por mil hab.'] = df['empregos_cultura'] / df['populacao'] * 1000
    df['Salário médio do setor'] = df['salario_medio_cultura_real']
    df['Empregados e MEI do setor por 1000 hab.'] = df['ocupado_formal_cultura'] /df['populacao'] * 1000
    
    # SES
    df['Taxa de homicídio'] = df['cvli'] / df['populacao'] * 100000
    df['INSE'] = df['inse']
    df['Perc. alunos INSE baixo'] = df['perc_inse']


# Produzindo estatísticas por região
indicadores(df_mun)
indicadores(df_reg)
indicadores(df_est)



# Classificação das colunas

classif = {'contextual': ['IDH',
                          'INSE',
                          'Perc. alunos INSE baixo',
                          'Taxa de homicídio'] ,
           'insumos':    ['Gasto municipal per capita com cultura',
                          'Repasse estadual/federal per capita para cultura',
                          'Agentes culturais por 10 mil hab.',
                          'Equipamentos por 100 mil hab.'],
           'atividades': ['Nº de projetos aprovados', 
                          'Nº de pessoas envolvidas nos projetos', 
                          'Volume de recursos aprovados',
                          'Nº de profissionais capacitados',
                          'Platarformas digitais  de divulgação'],
           'produtos':   ['Perc. alunos em escola com sala de artes', 
                          'Perc. alunos em escola com material de artes', 
                          'Perc. alunos em escola com sala e material de artes', 
                          'Nº profissionais de artes na escola por 1000 alunos'],
           'resultados': ['Empregados e MEI do setor por 1000 hab.',
                          'Empregados no setor por mil hab.', 
                          'Empresas do setor por mil hab.', 
                          'Salário médio do setor', 
                          'Público de eventos/festividades relacionadas à cultura local',
                          'Perc. alunos com disciplina de artes', 
                          'Perc. alunos com atividade de artes',
                          'Nº beneficiados com cursos e oficinas por mil hab.'
                          ]
           }

   

with open(f'{path}geojson_2022.json', "r") as f:
    geo_json_mun = json.load(f)

with open(f'{path}geojson_regioes_ce.json', "r") as f:
    geo_json_reg = json.load(f)


gdf = gpd.GeoDataFrame.from_features(geo_json_reg['features'])
gdf['centroid'] = gdf.geometry.centroid
gdf['ID0'] = gdf['ID0'].astype(int)
df_reg = pd.merge(df_reg, gdf[['ID0', 'centroid']], on='ID0', how='left')
df_reg['lat'] = df_reg['centroid'].apply(lambda point: point.y)
df_reg['lon'] = df_reg['centroid'].apply(lambda point: point.x)

gdf = gpd.GeoDataFrame.from_features(geo_json_mun['features'])
gdf['centroid'] = gdf.geometry.centroid
gdf['codarea'] = gdf['codarea'].astype(int)
df_mun = pd.merge(df_mun, gdf[['codarea', 'centroid']], left_on='co_municipio', right_on='codarea', how='left')
df_mun['lat'] = df_mun['centroid'].apply(lambda point: point.y)
df_mun['lon'] = df_mun['centroid'].apply(lambda point: point.x)



def choropleth(input_df, input_column, locations_id, ano, input_geojson, featurekey_id, 
               lat_center, lon_center, width_map=500, height_map=500, zoom_map=5.7):  
    
    choropleth = px.choropleth_mapbox(
            data_frame=input_df.loc[input_df['ano']==ano], 
            geojson=input_geojson,  
            locations=locations_id,
            featureidkey=featurekey_id,
            color=input_column,
            color_continuous_scale= 'ylgn',  #'thermal',            
            range_color=(input_df[input_column].min(), input_df[input_column].quantile(0.90)), # 0.92 evita Fortaleza 
            mapbox_style='white-bg',
            zoom=zoom_map,
            center={"lat": lat_center, "lon": lon_center},
            opacity=1,
            labels={input_column: input_column, 'regiao': 'Região', 'nome_municipio': 'Município'},
            width=width_map,
            height=height_map,
            #title='Mapa de regiões',
            hover_name='regiao',  # Add this line to set hover name
            hover_data={'regiao': False, input_column: True, var_secundaria: True}  # Include only desired hover data
    )    
    return(choropleth)
    

# Streamlit
st.set_page_config(
    page_title='Dashbord Cultura',
    layout="wide",
    initial_sidebar_state='auto') 


st.title("Painel de Monitoramento da Cultura")

# Radio button to choose between Country and State level data
view = st.radio(
    "Selecione o nível geográfico",
    ("Estado e suas regiões", "Municípios em uma região")
)

with st.sidebar:  

    st.markdown("<h2 style='font-size:1.2em'>Selecione o ano</h2>", unsafe_allow_html=True)
    ano = st.selectbox('Ano', [2023,2022,2021,2020,2019], index=0, key='ano')    

    st.markdown("<h2 style='font-size:1.2em'>Selecione o indicador principal</h2>", unsafe_allow_html=True)
    cat1 = st.selectbox('Categoria', list(classif.keys()), index=list(classif.keys()).index('resultados'), key='cat1')
    var_principal = st.selectbox('Indicador', classif[cat1], index=0, key='var_principal')            

    st.markdown("<h2 style='font-size:1.2em'>Selecione o indicador relacionado</h2>", unsafe_allow_html=True)
    cat2 = st.selectbox('Categoria', list(classif.keys()), index=list(classif.keys()).index('insumos'),  key='cat2')
    var_secundaria = st.selectbox('Indicador', classif[cat2], index=0, key='var_secundaria')

    st.markdown("<h2 style='font-size:1.2em'>Selecione o indicador contextual</h2>", unsafe_allow_html=True)
    cat3 = st.selectbox('Categoria do indicador', list(classif.keys()), key='cat3')
    var_tamanho1 = st.selectbox('Indicador', classif[cat3], index=0, key='var_tamanho1') 



# Color palette para as regiões
colors = {}
color_palette = px.colors.qualitative.Vivid
for i, reg in enumerate(df_reg['regiao'].unique()):
    colors[reg] = color_palette[i % len(color_palette)]




# Show data based on selection
if view == "Estado e suas regiões":
    st.subheader("Estado e suas regiões")

    col = st.columns((2.5, 3, 3), gap='medium')


    # Plot séries temporais

    def plot_dual_axis(df_est, var_principal, var_secundaria):
        # Adicionando colunas temporárias no DataFrame
        df_est['temp1'] = df_est[var_principal]  # Variável na escala de 0 a 1 (ou qualquer outra menor)
        df_est['temp2'] = df_est[var_secundaria]  # Variável na escala de 1000 a 5000 (ou qualquer outra maior)

        # Criação das duas séries de dados
        trace1 = go.Scatter(x=df_est['ano'], y=df_est['temp1'], name=var_principal, 
                            yaxis='y1', mode='lines+markers', line=dict(color='green'))
        trace2 = go.Scatter(x=df_est['ano'], y=df_est['temp2'], name=var_secundaria, 
                            yaxis='y2', mode='lines+markers', line=dict(color='orange'))

        # Layout com dois eixos Y
        layout = go.Layout(
            title=dict(text=f'{var_principal}<br>e {var_secundaria}',
                       x=0.5,  # Center the title
                       xanchor='center'
            ),
            xaxis=dict(title='Ano'),
            yaxis=dict(title=var_principal, side='left', showgrid=True),  # Eixo Y da variável principal
            yaxis2=dict(title=var_secundaria, side='right', overlaying='y', showgrid=False),  # Eixo Y da variável secundária
            showlegend=False,
            annotations=[
                dict(x=0.05, y=0.9, xref='paper', yref='paper', 
                    text=var_principal, showarrow=False, font=dict(size=12, color='green')),
                dict(x=0.05, y=0.8, xref='paper', yref='paper', 
                    text=var_secundaria, showarrow=False, font=dict(size=12, color='orange'))
            ],
            width=400,
            height=500,
        )

        # Criação da figura
        fig0 = go.Figure(data=[trace1, trace2], layout=layout)

        # Plotando o gráfico com Streamlit
        st.plotly_chart(fig0)


    # Plot séries temporais
    
    with col[0]:
        plot_dual_axis(df_est, var_principal, var_secundaria)


    # Plot mapa
    
    with col[1]:

        # Normalizando as variáveis
        df_reg['marker_size'] = ( (df_reg.loc[df_reg['ano']==ano, var_secundaria] - df_reg.loc[df_reg['ano']==ano, var_secundaria].min()) /
                            (df_reg.loc[df_reg['ano']==ano, var_secundaria].max() - df_reg.loc[df_reg['ano']==ano, var_secundaria].min()) ) *40
        df_reg.loc[df_reg.marker_size < 1, 'marker_size'] = 2

        fig1 = choropleth(input_df=df_reg, input_column=var_principal, ano=ano, locations_id='ID0', 
                            input_geojson=geo_json_reg, featurekey_id='properties.ID0', 
                            lat_center = -5.1, lon_center= -39.4,
                            )

        fig1.add_scattermapbox(
                lat=df_reg['lat'],  # Latitude
                lon=df_reg['lon'],  # Longitudelat
                mode='markers',
                marker=dict(
                    size=df_reg.loc[df_reg['ano']==ano, 'marker_size'],  
                    sizemode='diameter',
                    color='gray',
                    opacity=0.5,
                    showscale=False
                ),
                hoverinfo='none',
                showlegend=False        
            )

                                
        # Customize layout
        fig1.update_layout(
                title={
                    'text': f'{var_principal}<br>e {var_secundaria}<br>Ano: {ano}',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                coloraxis_colorbar={
                    'title': {
                        'text': var_principal,
                        'side': 'right'
                    }
                }
            )

        st.plotly_chart(fig1)


    # Plot scatter
    
    with col[2]:

        # Calculate medians
        median_var_principal = df_reg.loc[df_reg['ano']==ano, var_principal].median()
        median_var_secundaria = df_reg.loc[df_reg['ano']==ano, var_secundaria].median()

        df_reg['dot_size1'] = ( (df_reg.loc[df_reg['ano']==ano, var_tamanho1] - df_reg.loc[df_reg['ano']==ano, var_tamanho1].min()) /
                            (df_reg.loc[df_reg['ano']==ano, var_tamanho1].max() - df_reg.loc[df_reg['ano']==ano, var_tamanho1].min()) ) *30
        df_reg.loc[df_reg.dot_size1 < 1 , 'dot_size1'] = 1
        
        # Create a scatter plot using the selected variables
        fig_scatter1 = px.scatter(df_reg.loc[df_reg['ano']==ano], x=var_secundaria, y=var_principal, 
                                size=df_reg.loc[df_reg['ano']==ano, 'dot_size1'], color='regiao', color_discrete_map=colors,
                                size_max=20, hover_name='regiao', 
                                hover_data=[var_secundaria, var_principal, var_tamanho1])
        
        # Add vertical line at median of principal variable
        fig_scatter1.add_vline(x=median_var_secundaria, line_width=2, line_dash='dot', line_color='red')
        # Add horizontal line at median of secondary variable
        fig_scatter1.add_hline(y=median_var_principal, line_width=2, line_dash='dot', line_color='red')


        fig_scatter1.update_layout(title={
                    'text': f'{var_principal}<br>e {var_secundaria}<br>Ano: {ano}',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis_title=var_secundaria, 
                yaxis_title=var_principal, 
                width=550,
                xaxis_title_standoff=10,  # Adjust this value to move the x-axis title closer
                yaxis_title_standoff=10,  # Adjust this value to move the y-axis title closer
                annotations=[
                    dict(
                        text=f'*Tamanho dos círculos proporcional a {var_tamanho1}',
                        xref='paper',  # Reference the entire plotting area
                        yref='paper',  # Reference the entire plotting area
                        x=0,  # Center the annotation horizontally
                        y=-0.20,  # Position it below the graph
                        showarrow=False,  # No arrow for the annotation
                        font=dict(size=12)  # Font size for the annotation
                            )
                        ]
            )    


        # Display scatter plot in Streamlit
        st.plotly_chart(fig_scatter1)



    # Gráficos de barra

    fig_bar3 = px.bar(df_reg.loc[df_reg['ano']==ano].sort_values(var_principal, ascending=False), y='regiao', x=var_principal, hover_name='regiao', 
                        hover_data=[var_principal], color='regiao', color_discrete_map=colors, orientation='h')
    fig_bar3.update_layout( 
        title=dict(
            text=f'{var_principal}<br>Ano: {ano}',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis_title='', yaxis_title='', width=500, #width=750, 
        showlegend=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig_bar4 = px.bar(df_reg.loc[df_reg['ano']==ano].sort_values(var_secundaria, ascending=False), y='regiao', x=var_secundaria, hover_name='regiao', 
                        hover_data=[var_secundaria], color='regiao', color_discrete_map=colors, orientation='h')
    fig_bar4.update_layout(
        title=dict(
            text=f'{var_secundaria}<br>Ano: {ano}',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis_title='', yaxis_title='', width=500, #width=750, 
        showlegend=False
    )
    
    col2 = st.columns((4, 4), gap='medium')
    with col2[0]:
        st.plotly_chart(fig_bar3)
    with col2[1]:
        st.plotly_chart(fig_bar4)





#------- Painel Municípios em Região selecionada -------

elif view == "Municípios em uma região":

    st.subheader("Região e seus municípios")

    regiao = st.selectbox('Região', df_mun['regiao'].unique(), label_visibility="collapsed")

    df_mun_temp = df_mun[(df_mun.regiao == regiao) & (df_mun.ano == ano)]

    col = st.columns((2, 3, 3), gap='large')


    # Plot séries temporais

    with col[0]:
        

        df_reg_temp = df_reg[(df_reg.regiao == regiao)]

        value_2019_3 = df_reg_temp.loc[df_reg_temp['ano'] == 2019, var_principal].values[0]
        value_2019_4 = df_reg_temp.loc[df_reg_temp['ano'] == 2019, var_secundaria].values[0]

        df_reg_temp['temp3'] = df_reg_temp[var_principal] / value_2019_3 * 100
        df_reg_temp['temp4'] = df_reg_temp[var_secundaria] / value_2019_4 * 100
        
        fig0 = px.line(df_reg_temp, 
                    x='ano', 
                    y=['temp3', 'temp4'], 
                    color_discrete_sequence=['green', 'orange'],
                    labels={'ano': 'Ano', 'temp3': var_principal, 'temp4': var_secundaria}, 
                    # title=var_principal + ' vs ' + var_secundaria)}
                    title='Evolução dos indicadores para a região'
        )        
        
        fig0.update_layout(showlegend=False)
        
        fig0.update_layout(
            width=400, 
            height=500,
            annotations=[dict(x=0.05, y=0.9,xref='paper', yref='paper', text=var_principal, showarrow=False, font=dict(size=12, color='green')
                ),
                dict(x=0.05, y=0.8, xref='paper', yref='paper', text=var_secundaria, showarrow=False, font=dict(size=12, color='orange')
                )
            ]
        )
        
        st.plotly_chart(fig0)


    # Plot mapa 
    
    with col[1]:

        lat_center = df_reg.loc[(df_reg.regiao == regiao) & (df_reg.ano == ano), 'lat'].values[0]
        lon_center = df_reg.loc[(df_reg.regiao == regiao) & (df_reg.ano == ano), 'lon'].values[0]


        fig2 = choropleth(input_df=df_mun_temp, input_column=var_principal, ano=ano, locations_id='co_municipio', 
                            input_geojson=geo_json_mun, featurekey_id='properties.codarea', 
                            lat_center =lat_center , lon_center=lon_center,
                            zoom_map=7)
            

        df_mun_temp['marker_size'] = ((df_mun_temp.loc[df_mun_temp['ano'] == ano, var_secundaria] - 
                                    df_mun_temp.loc[df_mun_temp['ano'] == ano, var_secundaria].min()) 
                                    / (df_mun_temp.loc[df_mun_temp['ano'] == ano, var_secundaria].max() - 
                                        df_mun_temp.loc[df_mun_temp['ano'] == ano, var_secundaria].min() )) *30


        fig2.add_scattermapbox(
                lat=df_mun_temp['lat'],  # Latitude
                lon=df_mun_temp['lon'],  # Longitude
                mode='markers',
                marker=dict(
                    size=df_mun_temp.loc[df_mun_temp['ano'] == ano, 'marker_size'],   
                    sizemode='diameter',
                    color='orange',
                    opacity=0.5,
                    showscale=False
                ),
                hoverinfo='none',
                showlegend=False        
            )


        # Customize layout
        fig2.update_layout(
                title={
                    'text': f'{var_principal}<br>e {var_secundaria}<br>Ano: {ano}',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={'r': 0, 't': 0, 'l': 2, 'b': 0},
                coloraxis_colorbar={
                    'title': {
                        'text': var_principal,
                        'side': 'right'
                    }
                }
            )


        st.plotly_chart(fig2)



    # Scatter plots

    with col[2]:

    # Calculate medians
        median_var_principal2 = df_mun_temp.loc[df_mun_temp['ano'] == ano, var_principal].median()
        median_var_secundaria2 = df_mun_temp.loc[df_mun_temp['ano'] == ano, var_secundaria].median()

        # Allow user to select variables for size of the dots
        col1, col2 = st.columns(2)
        with col1:
            cat4 = st.selectbox('Categoria do indicador', list(classif.keys()), key='cat4')
        with col2:
            var_tamanho2 = st.selectbox('Indicador', classif[cat4], index=0, key='var_tamanho2')    
        
        df_mun_temp['dot_size2'] = ( (df_mun_temp.loc[df_mun_temp['ano']==ano, var_tamanho2] - df_mun_temp.loc[df_mun_temp['ano']==ano, var_tamanho2].min()) /
                            (df_mun_temp.loc[df_mun_temp['ano']==ano, var_tamanho2].max() - df_mun_temp.loc[df_mun_temp['ano']==ano, var_tamanho2].min()) ) *30

    # Create a scatter plot using the selected variables
        fig_scatter2 = px.scatter(df_mun_temp.loc[df_mun_temp['ano']==ano], x=var_secundaria, y=var_principal, 
                                size=df_mun_temp.loc[df_mun_temp['ano']==ano, 'dot_size2'], hover_name='nome_municipio', 
                                hover_data=[var_secundaria, var_principal, var_tamanho2])

        # Add vertical ano horizontal lines at median values
        fig_scatter2.add_vline(x=median_var_secundaria2, line_width=2, line_dash='dot', line_color='red')
        fig_scatter2.add_hline(y=median_var_principal2, line_width=2, line_dash='dot', line_color='red')

        fig_scatter2.update_layout(title=f'Ano: {ano}', xaxis_title=var_secundaria, yaxis_title=var_principal, width=550)    

        # Display scatter plot in Streamlit
        st.plotly_chart(fig_scatter2)   


    # Gráficos de barra

    # Color palette para as regiões
    colors2 = {}
    color_palette = px.colors.qualitative.Vivid
    for i, mun in enumerate(df_mun_temp['nome_municipio'].unique()):
        colors2[mun] = color_palette[i % len(color_palette)]

    

    fig_bar3 = px.bar(df_mun_temp.sort_values(var_principal, ascending=False), y='nome_municipio', x=var_principal, hover_name='nome_municipio', 
                        hover_data=[var_principal], color='nome_municipio', color_discrete_map=colors2, orientation='h')
    fig_bar3.update_layout( 
        title=dict(
            text=f'{var_principal}<br>Ano: {ano}',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis_title='', yaxis_title='', width=750, height= 100 + df_mun_temp['nome_municipio'].nunique()*25,
        showlegend=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig_bar4 = px.bar(df_mun_temp.sort_values(var_secundaria, ascending=False), y='nome_municipio', x=var_secundaria, hover_name='nome_municipio', 
                        hover_data=[var_secundaria], color='nome_municipio', color_discrete_map=colors2, orientation='h')
    fig_bar4.update_layout(
        title=dict(
            text=f'{var_secundaria}<br>Ano: {ano}',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis_title='', yaxis_title='', width=750, height= 100 + df_mun_temp['nome_municipio'].nunique()*25,
        showlegend=False
    )
    
    col2 = st.columns((4, 4), gap='medium')
    with col2[0]:
        st.plotly_chart(fig_bar3)
    with col2[1]:
        st.plotly_chart(fig_bar4)
