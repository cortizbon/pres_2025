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
sectors = list(df['Sector'].unique())


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

    st.header("Histórico por sector")

    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['Sector'] == sector]

    pivot_sector = filter_sector.pivot_table(index='Año', values='Apropiación a precios constantes (2025)', aggfunc='sum').reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True)
    
    fig.add_trace(
        go.Line(
            x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2025)'], 
            name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto_sector = (filter_sector
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_sector.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2025)'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')


    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

    st.plotly_chart(fig)

    st.subheader(f"Variación histórica por sector: {sector}")



    pivot_sector = pivot_sector.set_index('Año')
    pivot_sector['pct'] = pivot_sector['Apropiación a precios constantes (2025)'].pct_change()
    pivot_sector['pct'] = (pivot_sector['pct'] * 100).round(2)
    den = max(pivot_sector.index) - min(pivot_sector.index)
    pivot_sector['CAGR'] = ((pivot_sector.loc[max(pivot_sector.index), 'Apropiación a precios constantes (2025)'] / pivot_sector.loc[min(pivot_sector.index), 'Apropiación a precios constantes (2025)']) ** (1/12)) - 1
    pivot_sector['CAGR'] = (pivot_sector['CAGR'] * 100).round(2)
    pivot_sector = pivot_sector.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año')

    fig.add_trace(
            go.Bar(x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2025)'],
                name='Apropiación a precios constantes (2025)', marker_color=DIC_COLORES['ofiscal'][1]),
            row=1, col=1, 
        )

    fig.add_trace(go.Line(
                x=pivot_sector['Año'], 
                y=pivot_sector['pct'], 
                name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
            ),
            row=1, col=2
        )
    fig.add_trace(
            go.Line(
                x=pivot_sector['Año'], y=pivot_sector['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
            ),
            row=1, col=2
        )
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>")

    st.plotly_chart(fig)

    st.header('Histórico por entidades')
    sector = st.selectbox("Seleccione el sector", sectors, key=3)
    filter_sector = df[df['Sector'] == sector]
 
    entities_sector = filter_sector['Entidad'].unique()
    entidad = st.selectbox("Seleccione la entidad",
                            entities_sector)
    
    filter_entity = filter_sector[filter_sector['Entidad'] == entidad]

    pivot_entity = filter_entity.pivot_table(index='Año',
                                           values='Apropiación a precios constantes (2025)',
                                           aggfunc='sum')
    
    pivot_entity = pivot_entity.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True)
    
    fig.add_trace(
        go.Line(
            x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2025)'], 
            name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )
    piv_tipo_gasto_entity = (filter_entity
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_entity.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2025)'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')

    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

    st.plotly_chart(fig)

    if pivot_entity['Año'].nunique() <=1:
        st.warning(f"La entidad {entidad} solo tiene información de un año.")
        st.stop()

    st.subheader(f"Variación histórica por entidad: {entidad}")

    pivot_entity = pivot_entity.set_index('Año')
    pivot_entity['pct'] = pivot_entity['Apropiación a precios constantes (2025)'].pct_change()
    pivot_entity['pct'] = (pivot_entity['pct'] * 100).round(2)
    den = max(pivot_entity.index) - min(pivot_entity.index)
    pivot_entity['CAGR'] = ((pivot_entity.loc[max(pivot_entity.index), 'Apropiación a precios constantes (2025)'] / pivot_entity.loc[min(pivot_entity.index), 'Apropiación a precios constantes (2025)'] ) ** (1/den)) - 1
    pivot_entity['CAGR'] = (pivot_entity['CAGR'] * 100).round(2)
    pivot_entity = pivot_entity.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año')

    fig.add_trace(
        go.Bar(x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2025)'],
               name='Apropiación a precios constantes (2025)', marker_color=DIC_COLORES['ofiscal'][1]),
        row=1, col=1, 
    )

    fig.add_trace(go.Line(
            x=pivot_entity['Año'], 
            y=pivot_entity['pct'], 
            name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Line(
            x=pivot_entity['Año'], y=pivot_entity['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
        ),
        row=1, col=2
    )
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>")

    st.plotly_chart(fig)

    
    
with tab3:
    st.header("Descarga de información")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')
