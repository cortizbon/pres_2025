import pandas as pd
import streamlit as st
import plotly.express as px
from utils import DIC_COLORES, convert_df, get_dic_colors, get_dic_colors_area, create_dataframe_sankey
from io import BytesIO


st.set_page_config(layout='wide', page_title="ofiscal - PePE", page_icon='imgs/favicon.jpeg')


df = pd.read_csv('presupuesto_2025.csv')
df['Apropiación a precios corrientes'] = (df['Apropiación a precios corrientes'] / 1000000000).round(2)



st.title("Presupuesto General de la Nación - 2025")

st.divider()

tab1, tab2 = st.tabs(['Treemap', "Descarga"])

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
    st.header("Descarga de información")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')
