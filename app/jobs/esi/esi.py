import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip

shapefile_path = 'app/jobs/esi/files/35SEE250GC_SIR.shp'
BorderBRU = gpd.read_file(shapefile_path)

BorderBRU.crs = "EPSG:4326" 

csv_path = 'app/jobs/esi/files/DomicilioRenda_SP2.csv'
BRU = pd.read_csv(csv_path, sep=';')

BRU['Cod_setor'] = BRU['Cod_setor'].astype(str)
BorderBRU['CD_GEOCODI'] = BorderBRU['CD_GEOCODI'].astype(str)

merged_data = BorderBRU.merge(BRU, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')

income_columns = ['V005', 'V006', 'V007', 'V008', 'V009', 'V010', 'V011', 'V012', 'V013', 'V014']
merged_data[income_columns] = merged_data[income_columns].apply(pd.to_numeric, errors='coerce')

bauru_data = merged_data[(merged_data['NM_MUNICIP'] == 'BAURU') & (merged_data['TIPO'] == 'URBANO') & (merged_data['Cod_setor'] != '350600305000453')].copy()

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

color_map = {
    'Mais de 2 a 3 SM': 'cyan',
    'Mais de 3 a 5 SM': 'yellow',
    'Mais de 5 a 10 SM': 'red',
    'Mais de 10 SM': 'purple'
}

m = folium.Map(location=[-22.3192, -49.0709], zoom_start=12)

folium.GeoJson(
    bauru_data_filtered,
    style_function=lambda feature: {
        'fillColor': color_map.get(feature['properties']['Dominant_Group'], 'gray'),
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.5,
    },
    tooltip=GeoJsonTooltip(
        fields=[
            'V005', 'V006', 'V007', 'V008',
            'V009', 'V010', 'V011', 'V012',
            'V013', 'V014', 'Dominant_Group',
            'CD_GEOCODI'
        ],
        aliases=[
            'Domicílios com Rendimento até 1/8 SM: ',
            'Domicílios com Rendimento > 1/8 a 1/4 SM: ',
            'Domicílios com Rendimento > 1/4 a 1/2 SM: ',
            'Domicílios com Rendimento > 1/2 a 1 SM: ',
            'Domicílios com Rendimento > 1 a 2 SM: ',
            'Domicílios com Rendimento > 2 a 3 SM: ',
            'Domicílios com Rendimento > 3 a 5 SM: ',
            'Domicílios com Rendimento > 5 a 10 SM: ',
            'Domicílios com Rendimento > 10 SM: ',
            'Domicílios sem Rendimento: ',
            'Grupo Dominante: ',
            'Código da Região: '

        ],
        localize=True,
        sticky=False,
        labels=True,
    )
).add_to(m)

m.save('app/views/layouts/_relative_map.html.erb')