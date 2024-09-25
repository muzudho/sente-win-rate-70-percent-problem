#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import pandas as pd

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN
from file_paths import get_even_csv_file_path, get_muzudho_recommends_points_csv_file_path


CSV_FILE_PATH_P = './data/p.csv'
CSV_FILE_PATH_MRP = './data/report_muzudho_recommends_points.csv'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


def append_default_record_to_df_even(df, p, failure_rate):
    #                    p, failure_rate, best_p, best_p_error, best_number_of_series, best_b_step, best_w_step, best_span, latest_p, latest_p_error, latest_number_of_series, latest_b_step, latest_w_step, latest_span, process
    df.loc[len(df.index)] = [p, failure_rate,      0,         0.51,               2000000,           0,           1,         1,        0,           0.51,                 2000000,             0,             0,           0,       0]


def get_df_even(turn_system):

    csv_file_path = get_even_csv_file_path(turn_system=turn_system)

    # ファイルが存在しなかった場合
    if not os.path.isfile(csv_file_path):
        csv_file_path = get_even_csv_file_path(turn_system=None)


    if turn_system == WHEN_FROZEN_TURN:
        df = pd.read_csv(csv_file_path, encoding="utf8")

        #
        # NOTE pandas のデータフレームの列の型の初期値が float なので、それぞれ設定しておく
        #
        df['p'].astype('float')
        df['failure_rate'].astype('float')
        df['best_p'].fillna(0.0).astype('float')
        df['best_p_error'].fillna(0.0).astype('float')
        df['best_number_of_series'].fillna(0).astype('int')
        df['best_b_step'].fillna(0).astype('int')
        df['best_w_step'].fillna(0).astype('int')
        df['best_span'].fillna(0).astype('int')
        df['latest_p'].fillna(0.0).astype('float')
        df['latest_p_error'].fillna(0.0).astype('float')
        df['latest_number_of_series'].fillna(0).astype('int')
        df['latest_b_step'].fillna(0).astype('int')
        df['latest_w_step'].fillna(0).astype('int')
        df['latest_span'].fillna(0).astype('int')
        df['process'].fillna('').astype('string')

        return df


    if turn_system == WHEN_ALTERNATING_TURN:
        df = pd.read_csv(csv_file_path, encoding="utf8")

        #
        # NOTE pandas のデータフレームの列の型の初期値が float なので、それぞれ設定しておく
        #
        df['p'].astype('float')
        df['best_p'].fillna(0.0).astype('float')
        df['best_p_error'].fillna(0.0).astype('float')
        df['best_number_of_series'].fillna(0).astype('int')
        df['best_b_step'].fillna(0).astype('int')
        df['best_w_step'].fillna(0).astype('int')
        df['best_span'].fillna(0).astype('int')
        df['latest_p'].fillna(0.0).astype('float')
        df['latest_p_error'].fillna(0.0).astype('float')
        df['latest_number_of_series'].fillna(0).astype('int')
        df['latest_b_step'].fillna(0).astype('int')
        df['latest_w_step'].fillna(0).astype('int')
        df['latest_span'].fillna(0).astype('int')
        df['process'].fillna('').astype('string')

        return df


    raise ValueError(f"{turn_system=}")


def get_df_p():
    df = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")

    return df


def get_df_muzudho_recommends_points(turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
        df = pd.read_csv(get_muzudho_recommends_points_csv_file_path(turn_system=WHEN_ALTERNATING_TURN), encoding="utf8")
        df['p'].astype('float')
        df['number_of_series'].fillna(0).astype('int')
        df['b_step'].fillna(0).astype('int')
        df['w_step'].fillna(1).astype('int')
        df['span'].fillna(1).astype('int')
        df['presentable'].astype('string')
        df['comment'].astype('string')
        df['process'].astype('string')

        return df


    if turn_system == WHEN_FROZEN_TURN:
        df = pd.read_csv(get_muzudho_recommends_points_csv_file_path(turn_system=WHEN_FROZEN_TURN), encoding="utf8")
        df['p'].astype('float')
        df['number_of_series'].fillna(0).astype('int')
        df['b_step'].fillna(0).astype('int')
        df['w_step'].fillna(1).astype('int')
        df['span'].fillna(1).astype('int')
        df['presentable'].astype('string')
        df['comment'].astype('string')
        df['process'].astype('string')

        return df


    raise ValueError(f"{turn_system=}")


def get_df_muzudho_single_points(turn_system):
    if turn_system == WHEN_FROZEN_TURN:
        df = pd.read_csv(get_muzudho_single_points_csv_file_path(turn_system=WHEN_FROZEN_TURN), encoding="utf8")
        df['p'].astype('float')
        df['b_step'].fillna(0).astype('int')
        df['w_step'].fillna(1).astype('int')
        df['span'].fillna(1).astype('int')
        df['presentable'].astype('string')
        df['comment'].astype('string')
        df['process'].astype('string')

        return df


    raise ValueError(f"{turn_system=}")


def get_df_report_muzudho_recommends_points():
    df = pd.read_csv(CSV_FILE_PATH_MRP, encoding="utf8")
    df['p'].astype('float')
    df['b_time'].fillna(0).astype('int')
    df['w_time'].fillna(0).astype('int')

    return df


def get_df_let_calculate_probability():
    df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8")

    return df
