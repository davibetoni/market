import sys
import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip

param1 = sys.argv[1]
param2 = sys.argv[2]

print(f"Parâmetro 1: {param1}")
print(f"Parâmetro 2: {param2}")

# Load the shapefile
shapefile_path = 'app/jobs/esi/files/35SEE250GC_SIR.shp'
BorderBRU = gpd.read_file(shapefile_path)

# Set the CRS (replace with the correct EPSG code for your shapefile)
BorderBRU.crs = "EPSG:4326"  # Example: WGS 84

# Load the CSV data
csv_path = 'app/jobs/esi/files/DomicilioRenda_SP2.csv'
BRU = pd.read_csv(csv_path, sep=';')

# Convert necessary columns to string
BRU['Cod_setor'] = BRU['Cod_setor'].astype(str)
BorderBRU['CD_GEOCODI'] = BorderBRU['CD_GEOCODI'].astype(str)

# Merge dataframes
merged_data = BorderBRU.merge(BRU, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')

# Convert income-related columns to numeric
income_columns = ['V005', 'V006', 'V007', 'V008', 'V009', 'V010', 'V011', 'V012', 'V013', 'V014']
merged_data[income_columns] = merged_data[income_columns].apply(pd.to_numeric, errors='coerce')

# Filter for Bauru and only urban areas
bauru_data = merged_data[(merged_data['NM_MUNICIP'] == 'BAURU') & (merged_data['TIPO'] == 'URBANO')].copy()

# Define dominant groups
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

# Function to get the dominant group
def get_dominant_group(row):
    max_value = row[income_columns].max()
    if pd.isna(max_value) or max_value <= 0:  # Check if max_value is NaN or less than or equal to zero
        return 'Sem Rendimento'
    dominant_group = row[income_columns].idxmax()
    return dominant_groups[dominant_group]

# Apply the function to create a new column for dominant groups
bauru_data['Dominant_Group'] = bauru_data.apply(get_dominant_group, axis=1)

# Define colors for each dominant group
color_map = {
    'Até 1/8 SM': 'lightblue',
    'Mais de 1/8 a 1/4 SM': 'blue',
    'Mais de 1/4 a 1/2 SM': 'cyan',
    'Mais de 1/2 a 1 SM': 'green',
    'Mais de 1 a 2 SM': 'yellow',
    'Mais de 2 a 3 SM': 'orange',
    'Mais de 3 a 5 SM': 'red',
    'Mais de 5 a 10 SM': 'darkred',
    'Mais de 10 SM': 'purple',
    'Sem Rendimento': 'gray'
}

# Create a Folium map centered around Bauru
m = folium.Map(location=[-22.3192, -49.0709], zoom_start=12)

# Add GeoJSON layer with color based on the dominant group
folium.GeoJson(
    bauru_data,
    style_function=lambda feature: {
        'fillColor': color_map[feature['properties']['Dominant_Group']],
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.5,
    },
    tooltip=GeoJsonTooltip(
        fields=[
            'V001', 'V002', 'V003', 'V004',
            'V005', 'V006', 'V007', 'V008',
            'V009', 'V010', 'V011', 'V012',
            'V013', 'V014', 'Dominant_Group', 'NM_MUNICIP'
        ],
        aliases=[
            'Total de Domicílios Particulares Improvisados: ',
            'Total do Rendimento Nominal Mensal dos Domicílios Particulares: ',
            'Total do Rendimento Nominal Mensal dos Domicílios Permanentes: ',
            'Total do Rendimento Nominal Mensal dos Domicílios Improvisados: ',
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
            'Dominant Group: ',
            'Cidade: '
        ],
        localize=True,
        sticky=False,
        labels=True,
    )
).add_to(m)

m.save('app/views/layouts/_relative_map.html.erb')