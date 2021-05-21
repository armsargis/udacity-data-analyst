import math

import pandas as pd
from pandas import DataFrame

WINDOW_SIZE = 7


def compute_moving_averages(df: DataFrame, post_processor=lambda x: x) -> DataFrame:
    data: DataFrame = post_processor(df)
    data['moving_avg_temp'] = data['avg_temp'].rolling(window=WINDOW_SIZE).mean()
    return data


def merge(left: DataFrame, right: DataFrame) -> DataFrame:
    joined = pd.merge(left.drop(columns=['avg_temp']), right.drop(columns=['avg_temp']), on=['year'])
    return joined.iloc[WINDOW_SIZE - 1:]


def align_yerevan_results(yerevan_data: DataFrame, global_data: DataFrame) -> DataFrame:
    corr = yerevan_data['avg_temp'].median() / global_data['avg_temp'].median()

    def correlate(row):
        if math.isnan(row['avg_temp_y']):
            return row['avg_temp_x'] * corr
        else:
            return row['avg_temp_y']

    aligned_results = pd.merge(global_data, yerevan_data, how='left', on=['year'])
    aligned_results['avg_temp'] = aligned_results.apply(lambda row: correlate(row), axis=1)
    aligned_results.drop(['avg_temp_x', 'avg_temp_y'], axis=1, inplace=True)

    return aligned_results


if __name__ == '__main__':
    yerevan_results = pd.read_csv('csv/yerevan-results.csv')
    global_results = pd.read_csv('csv/global-results.csv')

    yerevan_aligned_results = align_yerevan_results(yerevan_results, global_results)

    global_averages = compute_moving_averages(global_results)
    yerevan_averages = compute_moving_averages(yerevan_aligned_results)

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
