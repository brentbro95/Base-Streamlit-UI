
# Пример функции экстраполяции и интерполяции
# Работает с датафреймом df


def fill_missing_by_interpolation(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Заполняет пропуски в числовых столбцах:
    1. интерполяцией внутри ряда,
    2. экстраполяцией по краям через forward/backward fill.

    Параметры:
    df : pd.DataFrame
        Исходный датафрейм.
    columns : list[str]
        Список числовых столбцов для обработки.

    Возвращает:
    pd.DataFrame
        Копия датафрейма с заполненными пропусками.
    """
    df = df.copy()

    for col in columns:
        # Пропускаем столбец, если его нет
        if col not in df.columns:
            continue

        # Пропускаем нечисловые признаки
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Интерполяция внутри данных
        df[col] = df[col].interpolate(method="linear", limit_direction="both")

        # Подстраховка:
        # если после интерполяции что-то осталось на краях, добиваем ближайшими значениями
        df[col] = df[col].ffill().bfill()

    return df

'''ПРИМЕР

# Применяем отдельно к train и test
X_train_interp = fill_missing_by_interpolation(X_train_pre, num_cols)
X_test_interp = fill_missing_by_interpolation(X_test_pre, num_cols)

display(X_train_interp.head())
'''