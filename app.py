import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import DIC_COLORES, convert_df, get_dic_colors, get_dic_colors_area, create_dataframe_sankey
from io import BytesIO
from plotly.subplots import make_subplots

st.set_page_config(layout='wide', page_title="ofiscal - PePE", page_icon='imgs/favicon.jpeg')


df = pd.read_csv('datos_totales.csv')
df['Apropiación a precios constantes (2025)'] = (df['Apropiación a precios constantes (2025)'] / 1000000000).round(2)
dict_gasto = {'Funcionamiento':DIC_COLORES['az_verd'][2],
              'Deuda':DIC_COLORES['ax_viol'][1],
              'Inversión':DIC_COLORES['ro_am_na'][3]}



st.title("Presupuesto General de la Nación - 2025")

st.divider()

tab1, tab2, tab3 = st.tabs(['Treemap', "Histórico", "Descarga"])

with tab1:

    st.header("Treemap")

    dic_treemap = get_dic_colors(df)
    dic_treemap['(?)'] = "#D9D9ED"
    fig = px.treemap(df, 
                     path=[px.Constant('PGN'),     'Sector', 
                               'Entidad', 
                               'Tipo de gasto'],
                    values="Apropiación a precios corrientes",
                    color='Sector',
                    color_discrete_map=dic_treemap,
                    title="Matriz de composición anual del PGN <br><sup>Cifras en miles de millones de pesos</sup>")
    
    fig.update_layout(width=1000, height=600)
    
    st.plotly_chart(fig)
    

with tab2:
    piv_2025 = df.groupby('Año')['Apropiación a precios constantes (2025)'].sum().reset_index()
    piv_corr = df.groupby('Año')['Apropiación a precios corrientes'].sum().reset_index()

    #piv_2024['Apropiación a precios constantes (2024)'] /= 1000

    fig = make_subplots(rows=1, cols=2, x_title='Año',  )
    
    fig.add_trace(
        go.Line(
            x=piv_2025['Año'], y=piv_2025['Apropiación a precios constantes (2025)'], 
            name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto = (df
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                      .sum()
                      .reset_index())
    piv_tipo_gasto['total'] = piv_tipo_gasto.groupby(['Año'])['Apropiación a precios constantes (2025)'].transform('sum')

    piv_tipo_gasto['%'] = ((piv_tipo_gasto['Apropiación a precios constantes (2025)'] / piv_tipo_gasto['total']) * 100).round(2)

        
    for i, group in piv_tipo_gasto.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['%'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


    st.plotly_chart(fig)
    
with tab3:
    st.header("Descarga de información")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')
