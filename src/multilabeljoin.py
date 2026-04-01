# Вариант 1: Последовательное объединение

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Считываем данные
df = pd.read_csv('data.csv')
gdf_regions = gpd.read_file('regions.geojson')  # полигоны регионов

# 2. Создаем точки из координат
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# 3. ПРОСТРАНСТВЕННОЕ ОБЪЕДИНЕНИЕ (координаты -> регион)
# Определяем, в какой регион попадает каждая точка
gdf_points = gpd.sjoin(gdf_points, gdf_regions, how='left', predicate='within')

# 4. ВРЕМЕННОЕ ОБЪЕДИНЕНИЕ (время)
# Преобразуем время к нужному формату (например, по часам/дням)
gdf_points['date'] = pd.to_datetime(gdf_points['date'])
gdf_points['hour'] = gdf_points['date'].dt.hour
gdf_points['day_of_week'] = gdf_points['date'].dt.dayofweek

# Создаем временной справочник (например, тарифы по часам)
time_rates = pd.DataFrame({
    'hour': range(24),
    'tariff': [1.0, 1.0, 0.8, 0.8, 0.8, 1.0, 1.5, 2.0, ...]  # пример
})

# Объединяем по часу
gdf_points = gdf_points.merge(time_rates, on='hour', how='left')

# 5. АТРИБУТИВНОЕ ОБЪЕДИНЕНИЕ (регион + категория)
# Создаем справочник: регион + категория -> коэффициент
region_category_mapping = pd.DataFrame({
    'region_name': ['Москва', 'Москва', 'СПб', 'СПб'],
    'category': ['A', 'B', 'A', 'B'],
    'coefficient': [1.2, 1.0, 1.1, 0.9]
})

# Объединяем по двум ключам
gdf_points = gdf_points.merge(
    region_category_mapping,
    on=['region_name', 'category'],
    how='left'
)

print(f"Итоговый датафрейм: {gdf_points.shape}")
print(gdf_points[['lat', 'lon', 'region_name', 'hour', 'tariff', 'coefficient']].head())
# Вариант 2: Создание составного ключа

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Подготовка данных
df = pd.read_csv('data.csv')
gdf_regions = gpd.read_file('regions.geojson')

# 2. Пространственное объединение (координаты)
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
gdf_points = gpd.sjoin(gdf_points, gdf_regions, how='left', predicate='within')

# 3. Создаем составной ключ для последующих объединений
# Например: регион + дата + категория
gdf_points['composite_key'] = (
    gdf_points['region_name'].astype(str) + '_' +
    gdf_points['date'].dt.strftime('%Y-%m-%d') + '_' +
    gdf_points['category'].astype(str)
)

# 4. Создаем справочник с составными ключами
reference_df = pd.DataFrame({
    'composite_key': ['Москва_2024-01-01_A', 'Москва_2024-01-01_B', 'СПб_2024-01-01_A'],
    'target_value': [100, 80, 90],
    'description': ['Москва A 01.01', 'Москва B 01.01', 'СПб A 01.01']
})

# 5. Объединяем по составному ключу
gdf_points = gdf_points.merge(reference_df, on='composite_key', how='left')

print(f"Добавлено {gdf_points['target_value'].notna().sum()} значений")
# Вариант 3: Многоуровневое объединение (рекомендуемый подход)

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

# 1. Загрузка данных
df = pd.read_csv('data.csv')
gdf_regions = gpd.read_file('regions.geojson')
df_rates = pd.read_excel('rates.xlsx')  # ставки: регион, час, день_недели, ставка
df_weather = pd.read_csv('weather.csv')  # погода: регион, дата, температура, осадки

# 2. Пространственное обогащение (точка -> регион)
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
gdf = gpd.sjoin(gdf, gdf_regions[['region_name', 'geometry']], 
                how='left', predicate='within')

# 3. Временная обработка (извлечение компонентов)
gdf['date'] = pd.to_datetime(gdf['date'])
gdf['hour'] = gdf['date'].dt.hour
gdf['day_of_week'] = gdf['date'].dt.dayofweek
gdf['month'] = gdf['date'].dt.month
gdf['is_weekend'] = gdf['day_of_week'].isin([5, 6]).astype(int)

# 4. Объединение с тарифами (по региону + часу + дню недели)
gdf = gdf.merge(
    df_rates,
    on=['region_name', 'hour', 'day_of_week'],
    how='left'
)

# 5. Объединение с погодой (по региону + дате)
gdf = gdf.merge(
    df_weather,
    on=['region_name', 'date'],
    how='left'
)

# 6. Агрегация статистики по региону (дополнительные признаки)
region_stats = gdf.groupby('region_name').agg({
    'target': ['mean', 'std', 'count'],
    'temperature': 'mean'
}).reset_index()
region_stats.columns = ['region_name', 'region_target_mean', 
                        'region_target_std', 'region_count', 'region_temp_mean']

gdf = gdf.merge(region_stats, on='region_name', how='left')

# 7. Проверка результата
print(f"✅ Итоговый датафрейм: {gdf.shape}")
print(f"📊 Колонки: {gdf.columns.tolist()}")
print(f"🔍 Пропусков после объединения:\n{gdf.isnull().sum()}")
#Вариант 4: Использование groupby для сложных условий

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Подготовка данных
df = pd.read_csv('data.csv')
gdf_regions = gpd.read_file('regions.geojson')

# 2. Пространственное объединение
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
gdf = gpd.sjoin(gdf, gdf_regions, how='left', predicate='within')

# 3. Создаем словарь с правилами для разных комбинаций
def get_rule(row):
    """Применяем правила на основе нескольких условий"""
    # Пространственные условия
    if row['region_name'] == 'Москва':
        base = 100
    elif row['region_name'] == 'СПб':
        base = 80
    else:
        base = 60
    
    # Временные условия
    hour = pd.to_datetime(row['date']).hour
    if 7 <= hour <= 10:  # утренний час пик
        multiplier = 1.5
    elif 17 <= hour <= 20:  # вечерний час пик
        multiplier = 1.3
    else:
        multiplier = 1.0
    
    # Категориальные условия
    if row.get('category') == 'VIP':
        multiplier *= 1.2
    
    return base * multiplier

# Применяем правила
gdf['calculated_value'] = gdf.apply(get_rule, axis=1)

print(gdf[['region_name', 'date', 'category', 'calculated_value']].head())