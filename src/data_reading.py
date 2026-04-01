from pathlib import Path
import pandas as pd
#

def merge_csv_from_folder(input_dir: str, output_dir: str, output_filename: str = "merged_dataset.csv") -> pd.DataFrame:
    """
    Считывает все CSV-файлы из указанной папки,
    объединяет их в один DataFrame
    и сохраняет результат в указанную папку.

    Параметры:
    input_dir : str
        Путь к папке с CSV-файлами.
    output_dir : str
        Путь к папке, куда сохранить итоговый файл.
    output_filename : str
        Имя итогового CSV-файла.

    Возвращает:
    pd.DataFrame
        Объединённый датасет.
    """

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Создаём папку для сохранения, если её нет
    output_path.mkdir(parents=True, exist_ok=True)

    # Находим все CSV-файлы в папке
    csv_files = list(input_path.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"В папке {input_dir} не найдено CSV-файлов.")

    # Считываем все CSV в список DataFrame
    dataframes = [pd.read_csv(file) for file in csv_files]

    # Объединяем в один датасет
    merged_df = pd.concat(dataframes, how='outer', ignore_index=True)

    # Сохраняем итоговый файл
    save_path = output_path / output_filename
    merged_df.to_csv(save_path, index=False)

    return merged_df

# ================================
# Считывание по границам
import pandas as pd
import geopandas as gpd

# 1. Считываем CSV файл с данными (например, о продажах или событиях)
df_csv = pd.read_csv('data.csv')
print(f"CSV data shape: {df_csv.shape}")
print(df_csv.head())

# 2. Считываем GeoJSON файл с геометрией (например, границы районов)
gdf_geo = gpd.read_file('boundaries.geojson')
print(f"GeoJSON data shape: {gdf_geo.shape}")
print(gdf_geo.head())

# 3. Объединяем по общему ключу (например, по названию района или ID)
# Вариант 1: merge по колонке
merged = df_csv.merge(gdf_geo, on='district_name', how='inner')

# Вариант 2: если нужно сохранить все точки из CSV и добавить геометрию
merged = df_csv.merge(gdf_geo[['district_name', 'geometry']], 
                      on='district_name', 
                      how='left')

# 4. Конвертируем обратно в GeoDataFrame для работы с картами
merged_gdf = gpd.GeoDataFrame(merged, geometry='geometry', crs=gdf_geo.crs)

print(f"Merged data shape: {merged_gdf.shape}")
print(merged_gdf.head())


# ================================
# Считывание по точкам

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Считываем CSV с координатами
df_points = pd.read_csv('points.csv')
print(f"Points data: {df_points.shape}")

# 2. Создаем геометрию из широты и долготы
geometry = [Point(xy) for xy in zip(df_points['lon'], df_points['lat'])]
gdf_points = gpd.GeoDataFrame(df_points, geometry=geometry, crs='EPSG:4326')

# 3. Считываем GeoJSON с полигонами
gdf_polygons = gpd.read_file('polygons.geojson')

# 4. Пространственное объединение (какая точка в каком полигоне)
joined = gpd.sjoin(gdf_points, gdf_polygons, how='left', predicate='within')

print(f"Joined data shape: {joined.shape}")
print(joined.head())

# ================================
# Считывание по точкам 2
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Считываем CSV с координатами
df = pd.read_csv('data.csv')
print(f"CSV shape: {df.shape}")
print(df[['lat', 'lon']].head())

# 2. Создаем геометрию из lat/lon (точки)
# Важно: сначала lon (долгота), потом lat (широта)
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]

# 3. Преобразуем в GeoDataFrame
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
print(f"Points GeoDataFrame created")

# 4. Считываем GeoJSON с полигонами
gdf_polygons = gpd.read_file('boundaries.geojson')
print(f"Polygons shape: {gdf_polygons.shape}")

# 5. Пространственное объединение (какая точка попадает в какой полигон)
joined = gpd.sjoin(gdf_points, gdf_polygons, how='left', predicate='within')

print(f"Joined shape: {joined.shape}")

# 6. Смотрим результат
print("\nРезультат объединения:")
print(joined[['lat', 'lon', 'index_right']].head())

# 7. Если нужно получить названия районов
# Предполагаем, что в gdf_polygons есть колонка 'district_name'
print("\nДобавление названий районов:")
print(joined[['lat', 'lon', 'district_name']].head())

# ================================
# Считывание по точкам 3

import pandas as pd
import geopandas as gpd

# 1. Считываем CSV с названием района
df = pd.read_csv('data.csv')
print(f"CSV columns: {df.columns.tolist()}")

# 2. Считываем GeoJSON с геометрией районов
gdf = gpd.read_file('boundaries.geojson')

# 3. Объединяем по названию района (если колонки совпадают)
merged = df.merge(gdf[['district_name', 'geometry']], 
                  left_on='district',      # колонка в CSV
                  right_on='district_name', # колонка в GeoJSON
                  how='left')

# 4. Преобразуем обратно в GeoDataFrame
merged_gdf = gpd.GeoDataFrame(merged, geometry='geometry', crs=gdf.crs)

print(f"Merged shape: {merged_gdf.shape}")
print(merged_gdf.head())

'''
Пример использования. 
Важно! В случае, если вы работаете с структурно разными CSV файлами
на выходе вы можете получить "Грязный" датафрейм и итоговый файл

df = merge_csv_from_folder(
    input_dir="data/input_csv",
    output_dir="data/output",
    output_filename="all_data.csv"
)

print(df.head())
'''

"""
Варианты merged

merged_df = merged_df.merge(df, 
                                   on=key_columns, 
                                   how=merge_strategy)
 "inner" — внутреннее объединение по ключам
 "concat" — вертикальное склеивание
 "outer" — внешнее объединение
 "left" / "right" — левое/правое объединение

Для временных рядов и ML → "left" с чётким master-файлом, содержащим временные метки и target

Для объединения партиций → "concat" (если структура одинаковая)

Для разведочного анализа → "outer" чтобы увидеть все связи

Для production пайплайна → "inner" или "left" для предсказуемой структуры
"""