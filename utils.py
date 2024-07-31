import pandas as pd

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def get_dic_colors(filtro):
    dic_colors = {}
    rank = filtro.groupby('Sector')['Apropiación a precios corrientes'].sum().rank().reset_index(name='rank')
    for _, info in rank.iterrows():
        sector_ = info['Sector']
        rank_ = info['rank']

        if rank_ > 26:
            dic_colors[sector_] = DIC_COLORES['ax_viol'][1]
        elif rank_ > 20:
            dic_colors[sector_] = DIC_COLORES['az_verd'][2]
        else:
            dic_colors[sector_] = DIC_COLORES['ro_am_na'][3]
    return dic_colors

def get_dic_colors_area(df):
    dic_colors = {}
    filtro = df[df['Año'] == 2024]
    rank = filtro.groupby('Sector')['apropiacion_cons_2024'].sum().rank().reset_index(name='rank')
    for _, info in rank.iterrows():
        sector_ = info['Sector']
        rank_ = info['rank']

        if rank_ > 26:
            dic_colors[sector_] = DIC_COLORES['ax_viol'][1]
        elif rank_ > 20:
            dic_colors[sector_] = DIC_COLORES['az_verd'][2]
        else:
            dic_colors[sector_] = DIC_COLORES['ro_am_na'][3]
    return dic_colors

DIC_COLORES = {'verde':["#009966"],
               'ro_am_na':["#FFE9C5", "#F7B261","#D8841C", "#dd722a","#C24C31", "#BC3B26"],
               'az_verd': ["#CBECEF", "#81D3CD", "#0FB7B3", "#009999"],
               'ax_viol': ["#D9D9ED", "#2F399B", "#1A1F63", "#262947"],
               'ofiscal': ["#F9F9F9", "#2635bf"]}

def create_dataframe_sankey(data, value_column, *columns, **filtros):
    for col in columns:
        if col not in data.columns:
            raise ValueError

    
    groups = {idx: data[column].unique().tolist() for idx, column in enumerate(columns)}
    groupbys = []

    nodes_list = []
    pos_list = []
    
    colors_nodes = dict(enumerate(["#2F399B", "#F7B261", "#0FB7B3", "#81D3CD"]))
    for idx, column in enumerate(columns):
        for i, value in enumerate(data[column].unique()):
            if str(idx) in filtros.keys():
                if value in filtros[str(idx)]:
                    continue           
            nodes_list.append(value)
            pos_list.append(idx)


    nodes = pd.DataFrame({'names':nodes_list,
                  'pos':pos_list}).reset_index().rename(columns={'index':'id'})
    nodes['x_pos'] = (nodes['pos'] / (len(columns) - 1)) + 0.02
    nodes['x_pos'] = [0.96 if v >=1 else v for v in nodes['x_pos']]
    nodes['color'] = nodes['pos'].map(colors_nodes)

    colors_links = dict(enumerate(["#D9D9ED", "#FFE9C5", "#CBECEF"]))

    for idx, col in enumerate(columns[:-1]):
        i = (data
             .groupby([columns[idx], columns[idx + 1]])[value_column]
             .sum()
             .reset_index())
        
        
        i.columns = ['source', 'target', 'value']
        i = i[~i['source'].isin(list(filtros.values())[0])]
        
        i['color'] = colors_links[idx]
        groupbys.append(i)

    conc = pd.concat(groupbys, ignore_index=True)

    dict_info = dict(nodes[[ 'names', 'id']].values)

    conc['source'] = conc['source'].map(dict_info)
    conc['target'] = conc['target'].map(dict_info)
    

    return nodes, dict_info, conc