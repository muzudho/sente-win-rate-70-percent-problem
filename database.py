#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import pandas as pd

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN
from file_paths import get_even_csv_file_path


CSV_FILE_PATH_MR_AT = './data/muzudho_recommends_points_when_alternating_turn.csv'
CSV_FILE_PATH_MR_FT = './data/muzudho_recommends_points_when_frozen_turn.csv'

CSV_FILE_PATH_SR_FT = './data/muzudho_single_points_when_frozen_turn.csv'

CSV_FILE_PATH_P = './data/p.csv'
CSV_FILE_PATH_MRP = './data/report_muzudho_recommends_points.csv'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


def get_df_generate_even(turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
        df = pd.read_csv(get_even_csv_file_path(turn_system=WHEN_ALTERNATING_TURN), encoding="utf8")

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

    if turn_system == WHEN_FROZEN_TURN:
        df = pd.read_csv(file_paths(turn_system=WHEN_FROZEN_TURN), encoding="utf8")

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
        df = pd.read_csv(CSV_FILE_PATH_MR_AT, encoding="utf8")
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
        df = pd.read_csv(CSV_FILE_PATH_MR_FT, encoding="utf8")
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
        df = pd.read_csv(CSV_FILE_PATH_SR_FT, encoding="utf8")
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
