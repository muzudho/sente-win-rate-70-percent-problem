#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import pandas as pd


CSV_FILE_PATH_AT = './data/generate_even_when_alternating_turn.csv'
CSV_FILE_PATH_FT = './data/generate_even_when_frozen_turn.csv'

CSV_FILE_PATH_MR_AT = './data/muzudho_recommends_points_when_alternating_turn.csv'
CSV_FILE_PATH_MR_FT = './data/muzudho_recommends_points_when_frozen_turn.csv'

CSV_FILE_PATH_SR_FT = './data/muzudho_single_points_when_frozen_turn.csv'

CSV_FILE_PATH_P = './data/p.csv'
CSV_FILE_PATH_MRP = './data/report_muzudho_recommends_points.csv'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


def get_df_generate_even_when_alternating_turn():
    df = pd.read_csv(CSV_FILE_PATH_AT, encoding="utf8")

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


def get_df_generate_even_when_frozen_turn():
    df = pd.read_csv(CSV_FILE_PATH_FT, encoding="utf8")

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


def get_df_p():
    df = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")

    return df


def get_df_muzudho_recommends_points_when_alternating_turn():
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


def get_df_muzudho_recommends_points_when_frozen_turn():
    df = pd.read_csv(CSV_FILE_PATH_MR_FT, encoding="utf8")
    df['p'].astype('float')
    df['b_step'].fillna(0).astype('int')
    df['w_step'].fillna(1).astype('int')
    df['span'].fillna(1).astype('int')
    df['presentable'].astype('string')
    df['comment'].astype('string')
    df['process'].astype('string')

    return df


def get_df_muzudho_single_points_when_frozen_turn():
    df = pd.read_csv(CSV_FILE_PATH_SR_FT, encoding="utf8")
    df['p'].astype('float')
    df['b_step'].fillna(0).astype('int')
    df['w_step'].fillna(1).astype('int')
    df['span'].fillna(1).astype('int')
    df['presentable'].astype('string')
    df['comment'].astype('string')
    df['process'].astype('string')

    return df


def get_df_report_muzudho_recommends_points():
    df = pd.read_csv(CSV_FILE_PATH_MRP, encoding="utf8")
    df['p'].astype('float')
    df['b_time'].fillna(0).astype('int')
    df['w_time'].fillna(0).astype('int')

    return df


def get_df_let_calculate_probability():
    df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8")

    return df
