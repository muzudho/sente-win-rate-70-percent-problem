#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import pandas as pd

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, round_letro
from library.file_paths import get_even_series_rule_csv_file_path, get_selection_series_rule_csv_file_path


CSV_FILE_PATH_P = './data/p.csv'
CSV_FILE_PATH_MRP = './data/report_selection_series_rule.csv'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


#############
# Even table
#############

class EvenTable():


    def __init__(self, p, failure_rate, best_p, best_p_error, best_number_of_series, best_p_step, best_q_step, best_span, latest_p, latest_p_error, latest_number_of_series, latest_p_step, latest_q_step, latest_span, candidates):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)

        self._p=p
        self._failure_rate=failure_rate
        self._best_p=best_p
        self._best_p_error=best_p_error
        self._best_number_of_series=best_number_of_series
        self._best_p_step=best_p_step
        self._best_q_step=best_q_step
        self._best_span=best_span
        self._latest_p=latest_p
        self._latest_p_error=latest_p_error
        self._latest_number_of_series=latest_number_of_series
        self._latest_p_step=latest_p_step
        self._latest_q_step=latest_q_step
        self._latest_span=latest_span
        self._candidates=candidates


    @property
    def p(self):
        return self._p


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def best_p(self):
        return self._best_p


    @property
    def best_p_error(self):
        return self._best_p_error


    @property
    def best_number_of_series(self):
        return self._best_number_of_series


    @property
    def best_p_step(self):
        return self._best_p_step


    @property
    def best_q_step(self):
        return self._best_q_step


    @property
    def best_span(self):
        return self._best_span


    @property
    def latest_p(self):
        return self._latest_p


    @property
    def latest_p_error(self):
        return self._latest_p_error


    @property
    def latest_number_of_series(self):
        return self._latest_number_of_series


    @property
    def latest_p_step(self):
        return self._latest_p_step


    @property
    def latest_q_step(self):
        return self._latest_q_step


    @property
    def latest_span(self):
        return self._latest_span


    @property
    def candidates(self):
        return self._candidates


def append_default_record_to_df_even(df, p, failure_rate):
    index = len(df.index)

    # TODO int 型が float になって入ってしまうのを防ぎたい ----> 防げない？
    df.loc[index, ['p']] = p
    df.loc[index, ['failure_rate']] = failure_rate
    df.loc[index, ['best_p']] = 0
    df.loc[index, ['best_p_error']] = 0.51
    df.loc[index, ['best_number_of_series']] = 1
    df.loc[index, ['best_p_step']] = 0
    df.loc[index, ['best_q_step']] = 1
    df.loc[index, ['best_span']] = 1
    df.loc[index, ['latest_p']] = 0
    df.loc[index, ['latest_p_error']] = 0.51
    df.loc[index, ['latest_number_of_series']] = 1
    df.loc[index, ['latest_p_step']] = 0
    df.loc[index, ['latest_q_step']] = 1
    df.loc[index, ['latest_span']] = 1
    df.loc[index, ['candidates']] = ''


def get_df_even(turn_system, generation_algorythm):

    csv_file_path = get_even_series_rule_csv_file_path(turn_system=turn_system, generation_algorythm=generation_algorythm)

    # ファイルが存在しなかった場合
    if not os.path.isfile(csv_file_path):
        csv_file_path = get_even_series_rule_csv_file_path()


    df = pd.read_csv(csv_file_path, encoding="utf8")
    #
    # NOTE pandas のデータフレームの列の型の初期値が float なので、それぞれ設定しておく
    #
    df['p'].astype('float')
    df['failure_rate'].astype('float')
    df['best_p'].fillna(0.0).astype('float')
    df['best_p_error'].fillna(0.0).astype('float')
    df['best_number_of_series'].fillna(0).astype('int')
    df['best_p_step'].fillna(0).astype('int')
    df['best_q_step'].fillna(0).astype('int')
    df['best_span'].fillna(0).astype('int')
    df['latest_p'].fillna(0.0).astype('float')
    df['latest_p_error'].fillna(0.0).astype('float')
    df['latest_number_of_series'].fillna(0).astype('int')
    df['latest_p_step'].fillna(0).astype('int')
    df['latest_q_step'].fillna(0).astype('int')
    df['latest_span'].fillna(0).astype('int')
    df['candidates'].fillna('').astype('string')
    return df


def df_even_to_csv(df, turn_system, generation_algorythm):
    # ファイルが存在しなかった場合、新規作成
    csv_file_path = get_even_series_rule_csv_file_path(turn_system=turn_system, generation_algorythm=generation_algorythm)

    # CSV保存
    df.to_csv(
            csv_file_path,
            # ［シリーズ・ルール候補］列は長くなるので末尾に置きたい
            columns=['p', 'failure_rate', 'best_p', 'best_p_error', 'best_number_of_series', 'best_p_step', 'best_q_step', 'best_span', 'latest_p', 'latest_p_error', 'latest_number_of_series', 'latest_p_step', 'latest_q_step', 'latest_span', 'candidates'],
            index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


##########
# P table
##########

def get_df_p():
    df = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")

    return df


###################################
# Muzudho recommended points table
###################################

def append_default_record_to_df_ssr(df, p, failure_rate):
    index = len(df.index)

    # TODO int 型が float になって入ってしまうのを防ぎたい ----> 防げない？
    # NOTE pandas の DataFrame に int 型の数値を入れると、小数点を付けて保存されてしまうため、 int 型の数は文字列として入れる。（ただし、取り出すときは float 型になる）
    df.loc[index, ['p']] = p
    df.loc[index, ['failure_rate']] = failure_rate
    df.loc[index, ['number_of_series']] = '0'
    df.loc[index, ['p_step']] = '0'
    df.loc[index, ['q_step']] = '1'
    df.loc[index, ['span']] = '1'
    df.loc[index, ['presentable']] = ''
    df.loc[index, ['comment']] = ''
    df.loc[index, ['candidates']] = ''


def get_df_selection_series_rule(turn_system):
    csv_file_path = get_selection_series_rule_csv_file_path(turn_system=turn_system)

    # ファイルが存在しなかった場合
    if not os.path.isfile(csv_file_path):
        csv_file_path = get_selection_series_rule_csv_file_path(turn_system=None)

    df = pd.read_csv(csv_file_path, encoding="utf8")

    df['p'].astype('float')
    df['failure_rate'].astype('float')
    df['number_of_series'].fillna(0).astype('int')
    df['p_step'].fillna(0).astype('int')
    df['q_step'].fillna(1).astype('int')
    df['span'].fillna(1).astype('int')
    df['presentable'].astype('string')
    df['comment'].astype('string')
    df['candidates'].astype('string')

    return df


def df_ssr_to_csv(df, turn_system):
    df.to_csv(get_selection_series_rule_csv_file_path(turn_system=turn_system),
            # ［計算過程］列は長くなるので末尾に置きたい
            columns=['p', 'failure_rate', 'number_of_series', 'p_step', 'q_step', 'span', 'presentable', 'comment', 'candidates'],
            index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


##############################
# Muzudho single points table
##############################

def get_df_muzudho_single_points(turn_system):
    if turn_system == WHEN_FROZEN_TURN:
        df = pd.read_csv(get_muzudho_single_points_csv_file_path(turn_system=WHEN_FROZEN_TURN), encoding="utf8")
        df['p'].astype('float')
        df['p_step'].fillna(0).astype('int')
        df['q_step'].fillna(1).astype('int')
        df['span'].fillna(1).astype('int')
        df['presentable'].astype('string')
        df['comment'].astype('string')
        df['candidates'].astype('string')

        return df


    raise ValueError(f"{turn_system=}")


def get_df_report_selection_series_rule():
    df = pd.read_csv(CSV_FILE_PATH_MRP, encoding="utf8")
    df['p'].astype('float')
    df['p_time'].fillna(0).astype('int')
    df['q_time'].fillna(0).astype('int')

    return df


########################
# Calculate probability
########################

def get_df_let_calculate_probability():
    df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8")

    return df
