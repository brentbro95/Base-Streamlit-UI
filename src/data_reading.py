from pathlib import Path
import pandas as pd


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