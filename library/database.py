#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import datetime
import pandas as pd

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_OUT_OF_ERROR, Converter, round_letro
from library.file_paths import get_even_data_csv_file_path, get_selection_series_rule_csv_file_path


CSV_FILE_PATH_P = './data/p.csv'
CSV_FILE_PATH_MRP = './data/report_selection_series_rule.csv'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


#############
# Even table
#############

class EvenTable():


    def __init__(self, p, failure_rate, turn_system, trials_series, best_p, best_p_error, best_h_step, best_t_step, best_span, latest_p, latest_p_error, latest_h_step, latest_t_step, latest_span, candidates):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_h_step = round_letro(best_h_step)
        best_t_step = round_letro(best_t_step)
        best_span = round_letro(best_span)
        latest_h_step = round_letro(latest_h_step)
        latest_t_step = round_letro(latest_t_step)
        latest_span = round_letro(latest_span)

        self._p=p
        self._failure_rate=failure_rate
        self._turn_system=turn_system
        self._trials_series=trials_series
        self._best_p=best_p
        self._best_p_error=best_p_error
        self._best_h_step=best_h_step
        self._best_t_step=best_t_step
        self._best_span=best_span
        self._latest_p=latest_p
        self._latest_p_error=latest_p_error
        self._latest_h_step=latest_h_step
        self._latest_t_step=latest_t_step
        self._latest_span=latest_span
        self._candidates=candidates


    @property
    def p(self):
        return self._p


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def turn_system(self):
        return self._turn_system


    @property
    def best_p(self):
        return self._best_p


    @property
    def best_p_error(self):
        return self._best_p_error


    @property
    def trials_series(self):
        return self._trials_series


    @property
    def best_h_step(self):
        return self._best_h_step


    @property
    def best_t_step(self):
        return self._best_t_step


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
    def latest_h_step(self):
        return self._latest_h_step


    @property
    def latest_t_step(self):
        return self._latest_t_step


    @property
    def latest_span(self):
        return self._latest_span


    @property
    def candidates(self):
        return self._candidates


def append_default_record_to_df_even(df, spec, trials_series):
    """
    Parameters
    ----------
    spec : Specification
        ［仕様］
    """
    index = len(df.index)

    # TODO int 型が float になって入ってしまうのを防ぎたい ----> 防げない？
    df.loc[index, ['p']] = spec.p
    df.loc[index, ['failure_rate']] = spec.failure_rate
    df.loc[index, ['turn_system']] = Converter.turn_system_to_code(spec.turn_system)
    df.loc[index, ['trials_series']] = trials_series
    df.loc[index, ['best_p']] = 0
    df.loc[index, ['best_p_error']] = ABS_OUT_OF_ERROR
    df.loc[index, ['best_h_step']] = 0
    df.loc[index, ['best_t_step']] = 1
    df.loc[index, ['best_span']] = 1
    df.loc[index, ['latest_p']] = 0
    df.loc[index, ['latest_p_error']] = ABS_OUT_OF_ERROR
    df.loc[index, ['latest_h_step']] = 0
    df.loc[index, ['latest_t_step']] = 1
    df.loc[index, ['latest_span']] = 1
    df.loc[index, ['candidates']] = ''


def get_df_even(failure_rate, turn_system, generation_algorythm, trials_series):
    """

    Parameters
    ----------
    failure_rate : float
        ［将棋の引分け率］
    turn_system : int
        ［手番が回ってくる制度］
    generation_algorythm : int
        ［生成アルゴリズム］
    trials_series : int
        ［試行シリーズ数］
    """

    csv_file_path = get_even_data_csv_file_path(failure_rate=failure_rate, turn_system=turn_system, generation_algorythm=generation_algorythm, trials_series=trials_series)

    # ファイルが存在しなかった場合
    if not os.path.isfile(csv_file_path):
        csv_file_path = get_even_data_csv_file_path()


    df = pd.read_csv(csv_file_path, encoding="utf8")

    #
    # NOTE pandas のデータフレームの列の型の初期値が float なので、それぞれ設定しておく
    #
    df['p'].astype('float64')
    df['failure_rate'].astype('float64')
    df['turn_system'].fillna(0).astype('object')    # string 型は無い？
    df['trials_series'].fillna(0).astype('int64')
    df['best_p'].fillna(0.0).astype('float64')
    df['best_p_error'].fillna(0.0).astype('float64')
    df['best_h_step'].fillna(0).astype('int64')
    df['best_t_step'].fillna(0).astype('int64')
    df['best_span'].fillna(0).astype('int64')
    df['latest_p'].fillna(0.0).astype('float64')
    df['latest_p_error'].fillna(0.0).astype('float64')
    df['latest_h_step'].fillna(0).astype('int64')
    df['latest_t_step'].fillna(0).astype('int64')
    df['latest_span'].fillna(0).astype('int64')
    df['candidates'].fillna('').astype('object')    # string 型は無い？

    return df


def df_even_to_csv(df, failure_rate, turn_system, generation_algorythm, trials_series):
    # ファイルが存在しなかった場合、新規作成
    csv_file_path = get_even_data_csv_file_path(failure_rate=failure_rate, turn_system=turn_system, generation_algorythm=generation_algorythm, trials_series=trials_series)

    print(f"[{datetime.datetime.now()}] write file to `{csv_file_path}` ...")

    # CSV保存
    df.to_csv(
            csv_file_path,
            # ［シリーズ・ルール候補］列は長くなるので末尾に置きたい
            columns=['p', 'failure_rate', 'turn_system', 'trials_series', 'best_p', 'best_p_error', 'best_h_step', 'best_t_step', 'best_span', 'latest_p', 'latest_p_error', 'latest_h_step', 'latest_t_step', 'latest_span', 'candidates'],
            index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


##########
# P table
##########

def get_df_p():
    df = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")

    return df


###################################
# Selection series rule table
###################################

class SelectionSeriesRuleTable():


    def __init__(self, p, failure_rate, h_step, t_step, span, presentable, comment, candidates):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        h_step = round_letro(h_step)
        t_step = round_letro(t_step)
        span = round_letro(span)

        self._p=p
        self._failure_rate=failure_rate
        self._h_step=h_step
        self._t_step=t_step
        self._span=span
        self._presentable=presentable
        self._comment=comment
        self._candidates=candidates


    @property
    def p(self):
        return self._p


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def h_step(self):
        return self._h_step


    @property
    def t_step(self):
        return self._t_step


    @property
    def span(self):
        return self._span


    @property
    def presentable(self):
        return self._presentable


    @property
    def comment(self):
        return self._comment


    @property
    def candidates(self):
        return self._candidates


def append_default_record_to_df_ssr(df, p, failure_rate):
    index = len(df.index)

    # TODO int 型が float になって入ってしまうのを防ぎたい ----> 防げない？
    # NOTE pandas の DataFrame に int 型の数値を入れると、小数点を付けて保存されてしまうため、 int 型の数は文字列として入れる。（ただし、取り出すときは float 型になる）
    df.loc[index, ['p']] = p
    df.loc[index, ['failure_rate']] = failure_rate
    df.loc[index, ['trials_series']] = '0'
    df.loc[index, ['h_step']] = '0'
    df.loc[index, ['t_step']] = '1'
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

    df['p'].astype('float64')
    df['failure_rate'].astype('float64')
    df['trials_series'].fillna(0).astype('int64')
    df['h_step'].fillna(0).astype('int64')
    df['t_step'].fillna(1).astype('int64')
    df['span'].fillna(1).astype('int64')
    df['presentable'].astype('object')    # string 型は無い？
    df['comment'].astype('object')    # string 型は無い？
    df['candidates'].astype('object')    # string 型は無い？

    return df


def df_ssr_to_csv(df, turn_system):

    csv_file_path = get_selection_series_rule_csv_file_path(turn_system=turn_system)

    print(f"[{datetime.datetime.now()}] write file to `{csv_file_path}` ...")

    df.to_csv(csv_file_path,
            # ［計算過程］列は長くなるので末尾に置きたい
            columns=['p', 'failure_rate', 'trials_series', 'h_step', 't_step', 'span', 'presentable', 'comment', 'candidates'],
            index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


########################
# Calculate probability
########################

def get_df_let_calculate_probability():
    df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8")

    return df
