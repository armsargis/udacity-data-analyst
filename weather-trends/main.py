import pandas as pd
from pandas import DataFrame

WINDOW_SIZE = 7


def compute_moving_averages(file: str, post_processor=lambda x: x) -> DataFrame:
    data: DataFrame = post_processor(pd.read_csv(file))
    data['moving_avg_temp'] = data['avg_temp'].rolling(window=WINDOW_SIZE).mean()
    return data


def fill_no_data_cells(df: DataFrame) -> DataFrame:
    median = df.median()
    return df.fillna(median)


def merge(left: DataFrame, right: DataFrame) -> DataFrame:
    joined = pd.merge(left.drop(columns=['avg_temp']), right.drop(columns=['avg_temp']), on=['year'])
    return joined.iloc[WINDOW_SIZE - 1:]


if __name__ == '__main__':
    yerevan_averages = compute_moving_averages('csv/yerevan-results.csv', fill_no_data_cells)
    global_averages = compute_moving_averages('csv/global-results.csv',
                                              lambda df: df[(df.year >= 1780) & (df.year <= 2013)])

    merged = merge(yerevan_averages, global_averages)
    merged.rename({'moving_avg_temp_x': 'Yerevan', 'moving_avg_temp_y': 'Global'}, axis=1, inplace=True)
    chart = merged.plot(
        x='year',
        y=['Yerevan', 'Global'],
        title='Weather trends',
        ylabel='temp',
        grid=True,
        figsize=(10, 4)
    )
    chart.get_figure().savefig("weather-trends.png")
