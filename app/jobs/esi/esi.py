import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip, GeoJsonPopup
import json
import sys

params = json.loads(sys.argv[1])

combined_income = []
for item in params['income']:
    combined_income.extend(json.loads(item))

shapefile_path = 'app/jobs/esi/files/35SEE250GC_SIR.shp'
csv_path = 'app/jobs/esi/files/DomicilioRenda_SP2.csv'
concorrencias_path = 'app/jobs/esi/files/concorrencias.csv'
imoveis_path = 'app/jobs/esi/files/imoveisFinal.csv'

BorderBRU = gpd.read_file(shapefile_path)
BorderBRU.crs = "EPSG:4326"

BRU = pd.read_csv(csv_path, sep=';')
BRU['Cod_setor'] = BRU['Cod_setor'].astype(str)
BorderBRU['CD_GEOCODI'] = BorderBRU['CD_GEOCODI'].astype(str)

merged_data = BorderBRU.merge(BRU, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')

income_columns = ['V005', 'V006', 'V007', 'V008', 'V009', 'V010', 'V011', 'V012', 'V013', 'V014']
merged_data[income_columns] = merged_data[income_columns].apply(pd.to_numeric, errors='coerce')

bauru_data = merged_data[
    (merged_data['NM_MUNICIP'] == 'BAURU') & 
    (merged_data['TIPO'] == 'URBANO') & 
    (merged_data['CD_GEOCODI'] != '350600305000453') &
    (merged_data['Cod_setor'].isin(combined_income))
].copy()

dominant_groups = {
    'V005': 'Até 1/8 SM',
    'V006': 'Mais de 1/8 a 1/4 SM',
    'V007': 'Mais de 1/4 a 1/2 SM',
    'V008': 'Mais de 1/2 a 1 SM',
    'V009': 'Mais de 1 a 2 SM',
    'V010': 'Mais de 2 a 3 SM',
    'V011': 'Mais de 3 a 5 SM',
    'V012': 'Mais de 5 a 10 SM',
    'V013': 'Mais de 10 SM',
    'V014': 'Sem Rendimento'
}

def get_dominant_group(row):
    max_value = row[income_columns].max()
    if pd.isna(max_value) or max_value <= 0:
        return 'Sem Rendimento'
    dominant_group = row[income_columns].idxmax()
    return dominant_groups[dominant_group]

bauru_data['Dominant_Group'] = bauru_data.apply(get_dominant_group, axis=1)

bauru_data_filtered = bauru_data[bauru_data['Dominant_Group'].isin([
    'Mais de 2 a 3 SM', 'Mais de 3 a 5 SM', 'Mais de 5 a 10 SM', 'Mais de 10 SM'
])]

concorrencias_data = pd.read_csv(concorrencias_path, sep=';')
concorrencias_data['Cod_setor'] = concorrencias_data['Cod_setor'].astype(str)

bauru_data_filtered = bauru_data_filtered.merge(
    concorrencias_data[['Cod_setor', 'Nome_Mercado']], 
    left_on='Cod_setor', 
    right_on='Cod_setor', 
    how='left'
)

def get_markets(row):
    if pd.isna(row['Nome_Mercado']):
        return 'Nenhum mercado disponível'
    return row['Nome_Mercado']

bauru_data_filtered['Nearby_Markets'] = bauru_data_filtered.apply(get_markets, axis=1)

if params.get('another_markets') == '1':
    bauru_data_filtered = bauru_data_filtered[
        bauru_data_filtered['Cod_setor'].isin(concorrencias_data['Cod_setor'])
    ]
else:
    bauru_data_filtered = bauru_data_filtered[
        ~bauru_data_filtered['Cod_setor'].isin(concorrencias_data['Cod_setor'])
    ]


imoveis_data = pd.read_csv(imoveis_path, sep=';')
imoveis_data['Cod_setor'] = imoveis_data['Cod_setor'].astype(str)

if 'trading' in params:
    trading_value = int(params['trading'])
    imoveis_data = imoveis_data[imoveis_data['perto_de_comercio'] == trading_value]

if 'busy_streets' in params:
    busy_streets_value = int(params['busy_streets'])
    imoveis_data = imoveis_data[imoveis_data['perto_de_avenidas'] == busy_streets_value]

if 'type' in params:
    valid_types = params['type'] # ['compra', 'aluguel']
    if isinstance(valid_types, str):
        valid_types = [valid_types]

    imoveis_data = imoveis_data[imoveis_data['compra_ou_aluguel'].isin(valid_types)]

bauru_data_filtered = bauru_data_filtered[
    bauru_data_filtered['Cod_setor'].isin(imoveis_data['Cod_setor'])
]

bauru_data_filtered = bauru_data_filtered.merge(
    imoveis_data[['Cod_setor', 'valor', 'bairro', 'link', 'compra_ou_aluguel']],
    left_on='Cod_setor',
    right_on='Cod_setor',
    how='left'
)

color_map = {
    'Mais de 2 a 3 SM': 'cyan',
    'Mais de 3 a 5 SM': 'yellow',
    'Mais de 5 a 10 SM': 'red',
    'Mais de 10 SM': 'purple'
}

m = folium.Map(location=[-22.3192, -49.0709], zoom_start=12)

desired_tooltip_fields = {
    'Dominant_Group': 'Grupo Dominante: ',
    'CD_GEOCODI': 'Código da Região: ',
    'Nearby_Markets': 'Mercados Próximos: ',
    'valor': 'Valor do Imóvel: ',
    'bairro': 'Bairro: ',
    'compra_ou_aluguel': 'Compra ou Aluguel: '
}

tooltip_fields = [field for field in desired_tooltip_fields if field in bauru_data_filtered.columns]
tooltip_aliases = [desired_tooltip_fields[field] for field in tooltip_fields]

popup_template = """
    <a href="{link}" target="_blank">Clique aqui para ver o imóvel</a>
"""

folium.GeoJson(
    bauru_data_filtered,
    style_function=lambda feature: {
        'fillColor': color_map.get(feature['properties']['Dominant_Group'], 'gray'),
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.5,
    },
    tooltip=GeoJsonTooltip(
        fields=tooltip_fields,
        aliases=tooltip_aliases,
        localize=True,
        sticky=False,
        labels=True,
    ),
    popup=GeoJsonPopup(
        fields=['link'],
        labels=False,
        parse_html=True,
        localize=True,
        aliases=['Link para o imóvel: '],
        template=popup_template
    )
).add_to(m)

m.save('app/views/layouts/_relative_map.html.erb')
