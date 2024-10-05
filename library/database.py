#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import datetime
import pandas as pd

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_OUT_OF_ERROR, OUT_OF_P, EVEN, round_letro, Converter, ThreeRates
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths, TheoreticalProbabilityFilePaths, TheoreticalProbabilityBestFilePaths, KakukinDataFilePaths


CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


####################
# Kakukin Data Sheet
####################

class KakukinDataSheetRecord():


    def __init__(self, p, failure_rate, turn_system_name, head_step, tail_step, span, shortest_coins, upper_limit_coins, trials_series, series_shortest_coins, series_longest_coins, wins_a, wins_b, succucessful_series, s_ful_wins_a, s_ful_wins_b, s_pts_wins_a, s_pts_wins_b, failed_series, f_ful_wins_a, f_ful_wins_b, f_pts_wins_a, f_pts_wins_b, no_wins_ab):
        self._p = p
        self._failure_rate = failure_rate
        self._turn_system_name = turn_system_name
        self._head_step = head_step
        self._tail_step = tail_step
        self._span = span
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._trials_series = trials_series
        self._series_shortest_coins = series_shortest_coins
        self._series_longest_coins = series_longest_coins
        self._wins_a = wins_a
        self._wins_b = wins_b
        self._succucessful_series = succucessful_series
        self._s_ful_wins_a = s_ful_wins_a
        self._s_ful_wins_b = s_ful_wins_b
        self._s_pts_wins_a = s_pts_wins_a
        self._s_pts_wins_b = s_pts_wins_b
        self._failed_series = failed_series
        self._f_ful_wins_a = f_ful_wins_a
        self._f_ful_wins_b = f_ful_wins_b
        self._f_pts_wins_a = f_pts_wins_a
        self._f_pts_wins_b = f_pts_wins_b
        self._no_wins_ab = no_wins_ab


    @property
    def p(self):
        return self._p


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def turn_system_name(self):
        return self._turn_system_name


    @property
    def head_step(self):
        return self._head_step


    @property
    def tail_step(self):
        return self._tail_step


    @property
    def span(self):
        return self._span


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def trials_series(self):
        return self._trials_series


    @property
    def series_shortest_coins(self):
        return self._series_shortest_coins


    @property
    def series_longest_coins(self):
        return self._series_longest_coins


    @property
    def wins_a(self):
        return self._wins_a


    @property
    def wins_b(self):
        return self._wins_b


    @property
    def succucessful_series(self):
        return self._succucessful_series


    @property
    def s_ful_wins_a(self):
        return self._s_ful_wins_a


    @property
    def s_ful_wins_b(self):
        return self._s_ful_wins_b


    @property
    def s_pts_wins_a(self):
        return self._s_pts_wins_a


    @property
    def s_pts_wins_b(self):
        return self._s_pts_wins_b


    @property
    def failed_series(self):
        return self._failed_series


    @property
    def f_ful_wins_a(self):
        return self._f_ful_wins_a


    @property
    def f_ful_wins_b(self):
        return self._f_ful_wins_b


    @property
    def f_pts_wins_a(self):
        return self._f_pts_wins_a


    @property
    def f_pts_wins_b(self):
        return self._f_pts_wins_b


    @property
    def no_wins_ab(self):
        return self._no_wins_ab


class KakukinDataSheetTable():


    _dtype = {
        'p':'float64',
        'failure_rate':'float64',
        'turn_system_name':'object',     # string 型は無いから object
        'head_step':'int64',
        'tail_step':'int64',
        'span':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'trials_series':'int64',
        'series_shortest_coins':'int64',
        'series_longest_coins':'int64',
        'wins_a':'float64',
        'wins_b':'float64',
        'succucessful_series':'float64',
        's_ful_wins_a':'float64',
        's_ful_wins_b':'float64',
        's_pts_wins_a':'float64',
        's_pts_wins_b':'float64',
        'failed_series':'float64',
        'f_ful_wins_a':'float64',
        'f_ful_wins_b':'float64',
        'f_pts_wins_a':'float64',
        'f_pts_wins_b':'float64',
        'no_wins_ab':'float64'}


    @classmethod
    def read_df(clazz, failure_rate, turn_system_id, trials_series):
        """

        Parameters
        ----------
        failure_rate : float
            ［将棋の引分け率］
        turn_system_id : int
            ［手番が回ってくる制度］
        trials_series : int
            ［試行シリーズ数］
        """

        csv_file_path = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=failure_rate,
                turn_system_id=turn_system_id,
                trials_series=trials_series)

        # ファイルが存在しなかった場合
        if not os.path.isfile(csv_file_path):
            return None


        df = pd.read_csv(csv_file_path, encoding="utf8",
                dtype=clazz._dtype)

        return df


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        on_each : func
            record 引数を受け取る関数
        """
        for         p  ,     failure_rate  ,     turn_system_name  ,     head_step  ,     tail_step  ,     span  ,     shortest_coins  ,     upper_limit_coins  ,     trials_series  ,     series_shortest_coins  ,     series_longest_coins  ,     wins_a  ,     wins_b  ,     succucessful_series  ,     s_ful_wins_a  ,     s_ful_wins_b  ,     s_pts_wins_a  ,     s_pts_wins_b  ,     failed_series  ,     f_ful_wins_a  ,     f_ful_wins_b  ,     f_pts_wins_a  ,     f_pts_wins_b  ,     no_wins_ab in\
            zip(df['p'], df['failure_rate'], df['turn_system_name'], df['head_step'], df['tail_step'], df['span'], df['shortest_coins'], df['upper_limit_coins'], df['trials_series'], df['series_shortest_coins'], df['series_longest_coins'], df['wins_a'], df['wins_b'], df['succucessful_series'], df['s_ful_wins_a'], df['s_ful_wins_b'], df['s_pts_wins_a'], df['s_pts_wins_b'], df['failed_series'], df['f_ful_wins_a'], df['f_ful_wins_b'], df['f_pts_wins_a'], df['f_pts_wins_b'], df['no_wins_ab']):

            # レコード作成
            record = KakukinDataSheetRecord(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system_name=turn_system_name,
                    head_step=head_step,
                    tail_step=tail_step,
                    span=span,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    trials_series=trials_series,
                    series_shortest_coins=series_shortest_coins,
                    series_longest_coins=series_longest_coins,
                    wins_a=wins_a,
                    wins_b=wins_b,
                    succucessful_series=succucessful_series,
                    s_ful_wins_a=s_ful_wins_a,
                    s_ful_wins_b=s_ful_wins_b,
                    s_pts_wins_a=s_pts_wins_a,
                    s_pts_wins_b=s_pts_wins_b,
                    failed_series=failed_series,
                    f_ful_wins_a=f_ful_wins_a,
                    f_ful_wins_b=f_ful_wins_b,
                    f_pts_wins_a=f_pts_wins_a,
                    f_pts_wins_b=f_pts_wins_b,
                    no_wins_ab=no_wins_ab)

            on_each(record)


class EmpiricalProbabilityRecord():


    def __init__(self, p, failure_rate, turn_system_name, trials_series, best_p, best_p_error, best_h_step, best_t_step, best_span, latest_p, latest_p_error, latest_h_step, latest_t_step, latest_span, candidates):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_h_step = round_letro(best_h_step)
        best_t_step = round_letro(best_t_step)
        best_span = round_letro(best_span)
        latest_h_step = round_letro(latest_h_step)
        latest_t_step = round_letro(latest_t_step)
        latest_span = round_letro(latest_span)

        self._p=p
        self._failure_rate=failure_rate
        self._turn_system_name=turn_system_name
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
    def turn_system_name(self):
        return self._turn_system_name


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


class EmpiricalProbabilityTable():
    """経験的確率論テーブル
    旧名： EvenTable
    """


    _dtype = {
        'p':'float64',
        'failure_rate':'float64',
        'turn_system_name':'object',     # string 型は無いから object
        'trials_series':'int64',
        'best_p':'float64',
        'best_p_error':'float64',
        'best_h_step':'int64',
        'best_t_step':'int64',
        'best_span':'int64',
        'latest_p':'float64',
        'latest_p_error':'float64',
        'latest_h_step':'int64',
        'latest_t_step':'int64',
        'latest_span':'int64',
        'candidates':'object'}


    @staticmethod
    def append_default_record(df, spec, trials_series):
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
        df.loc[ index, ['turn_system_name']] = Converter.turn_system_id_to_code(spec.turn_system_id)
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


    @staticmethod
    def update_record(df, specified_p, trials_series,
            best_p, best_p_error, best_h_step, best_t_step, best_span,
            latest_p, latest_p_error, latest_h_step, latest_t_step, latest_span,
            candidates):
        """レコード更新
        
        Parameters
        ----------
        trials_series : int
            ［試行シリーズ数］
        best_p : float
            ［調整後の表が出る確率］列を更新
        best_p_error : float
            ［調整後の表が出る確率の５割との誤差］
        best_h_step : int
            ［表番で勝ったときの勝ち点］列を更新
        best_t_step : int
            ［裏番で勝ったときの勝ち点］列を更新
        best_span : int
            ［目標の点数］列を更新 
        latest_p : float
            ［調整後の表が出る確率］列を更新
        latest_p_error : float
            ［調整後の表が出る確率の５割との誤差］
        latest_h_step : int
            ［表番で勝ったときの勝ち点］列を更新
        latest_t_step : int
            ［裏番で勝ったときの勝ち点］列を更新
        latest_span : int
            ［目標の点数］列を更新 
        candidates : str
            ［シリーズ・ルール候補］
        """
        df.loc[df['p']==specified_p, ['trials_series']] = trials_series
        df.loc[df['p']==specified_p, ['best_p']] = best_p
        df.loc[df['p']==specified_p, ['best_p_error']] = best_p_error
        df.loc[df['p']==specified_p, ['best_h_step']] = best_h_step
        df.loc[df['p']==specified_p, ['best_t_step']] = best_t_step
        df.loc[df['p']==specified_p, ['best_span']] = best_span
        df.loc[df['p']==specified_p, ['latest_p']] = latest_p
        df.loc[df['p']==specified_p, ['latest_p_error']] = latest_p_error
        df.loc[df['p']==specified_p, ['latest_h_step']] = latest_h_step
        df.loc[df['p']==specified_p, ['latest_t_step']] = latest_t_step
        df.loc[df['p']==specified_p, ['latest_span']] = latest_span
        df.loc[df['p']==specified_p, ['candidates']] = candidates


    @classmethod
    def read_df(clazz, failure_rate, turn_system_id, trials_series):
        """

        Parameters
        ----------
        failure_rate : float
            ［将棋の引分け率］
        turn_system_id : int
            ［手番が回ってくる制度］
        trials_series : int
            ［試行シリーズ数］
        """

        csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv(failure_rate=failure_rate, turn_system_id=turn_system_id, trials_series=trials_series)

        # ファイルが存在しなかった場合
        if not os.path.isfile(csv_file_path):
            csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv()


        df = pd.read_csv(csv_file_path, encoding="utf8",
                dtype=clazz._dtype)

        return df


    @staticmethod
    def to_csv(df, failure_rate, turn_system_id, trials_series):
        # ファイルが存在しなかった場合、新規作成
        csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv(failure_rate=failure_rate, turn_system_id=turn_system_id, trials_series=trials_series)

        print(f"[{datetime.datetime.now()}] write file to `{csv_file_path}` ...")

        # CSV保存
        df.to_csv(
                csv_file_path,
                # ［シリーズ・ルール候補］列は長くなるので末尾に置きたい
                columns=['p', 'failure_rate', 'turn_system_name', 'trials_series', 'best_p', 'best_p_error', 'best_h_step', 'best_t_step', 'best_span', 'latest_p', 'latest_p_error', 'latest_h_step', 'latest_t_step', 'latest_span', 'candidates'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        """
        for         p,       failure_rate,       turn_system_name,   trials_series,       best_p,       best_p_error,       best_h_step,       best_t_step,       best_span,       latest_p,       latest_p_error,       latest_h_step,       latest_t_step,       latest_span,       candidates in\
            zip(df['p'], df['failure_rate'], df['turn_system_name'], df['trials_series'], df['best_p'], df['best_p_error'], df['best_h_step'], df['best_t_step'], df['best_span'], df['latest_p'], df['latest_p_error'], df['latest_h_step'], df['latest_t_step'], df['latest_span'], df['candidates']):

            # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
            trials_series = round_letro(trials_series)
            best_h_step = round_letro(best_h_step)
            best_t_step = round_letro(best_t_step)
            best_span = round_letro(best_span)
            latest_h_step = round_letro(latest_h_step)
            latest_t_step = round_letro(latest_t_step)
            latest_span = round_letro(latest_span)

            # レコード作成
            record = EmpiricalProbabilityRecord(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system_name=turn_system_name,
                    trials_series=trials_series,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_h_step=best_h_step,
                    best_t_step=best_t_step,
                    best_span=best_span,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_h_step=latest_h_step,
                    latest_t_step=latest_t_step,
                    latest_span=latest_span,
                    candidates=candidates)

            on_each(record)


class CalculateProbabilityTable():


    @staticmethod
    def get_df_let_calculate_probability():
        df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8",
                dtype={
                    'p':'float64',
                    'p_time':'int64',
                    'q_time':'int64',
                    'best_p':'float64',
                    'best_p_error':'float64',
                    'comment':'object'
                })

        return df


class TheoreticalProbabilityRecord():


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, theoretical_a_win_rate, theoretical_a_win_rate_abs_error, theoretical_no_win_match_rate):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._theoretical_a_win_rate = theoretical_a_win_rate
        self._theoretical_a_win_rate_abs_error = theoretical_a_win_rate_abs_error
        self._theoretical_no_win_match_rate = theoretical_no_win_match_rate


    @property
    def turn_system_name(self):
        return self._turn_system_name


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def p(self):
        return self._p


    @property
    def span(self):
        return self._span


    @property
    def t_step(self):
        return self._t_step


    @property
    def h_step(self):
        return self._h_step


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def theoretical_a_win_rate(self):
        return self._theoretical_a_win_rate


    @property
    def theoretical_a_win_rate_abs_error(self):
        return self._theoretical_a_win_rate_abs_error


    @property
    def theoretical_no_win_match_rate(self):
        return self._theoretical_no_win_match_rate


class TheoreticalProbabilityTable():
    """理論的確率データ"""


    _dtype = {
        'turn_system_name':'object',     # string 型は無い？
        'failure_rate':'float64',
        'p':'float64',
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'theoretical_a_win_rate':'float64',
        'theoretical_a_win_rate_abs_error':'float64',
        'theoretical_no_win_match_rate':'float64'}


    @classmethod
    def new_data_frame(clazz):
        df = pd.DataFrame.from_dict({
                'turn_system_name': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'theoretical_a_win_rate': [],
                'theoretical_a_win_rate_abs_error': [],
                'theoretical_no_win_match_rate': []}).astype(clazz._dtype)

        return df


    @classmethod
    def read_df(clazz, spec, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        df : DataFrame
            データフレーム
        is_new : bool
            新規作成されたか？
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)


        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                df = TheoreticalProbabilityTable.new_data_frame()
            else:
                df = None

        else:
            df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)


        return df, is_new


    @staticmethod
    def append_new_record(df, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, theoretical_a_win_rate, theoretical_no_win_match_rate):
        index = len(df.index)


        df.loc[index, [ 'turn_system_name']] = turn_system_name   # FIXME ここで型エラー？

        df.loc[index, ['failure_rate']] = failure_rate
        df.loc[index, ['p']] = p
        df.loc[index, ['span']] = span
        df.loc[index, ['t_step']] = t_step
        df.loc[index, ['h_step']] = h_step
        df.loc[index, ['shortest_coins']] = shortest_coins
        df.loc[index, ['upper_limit_coins']] = upper_limit_coins

        # あとで設定する
        if theoretical_a_win_rate is None:
            df.loc[index, ['theoretical_a_win_rate']] = OUT_OF_P
            df.loc[index, ['theoretical_a_win_rate_abs_error']] = abs(OUT_OF_P - EVEN)
        else:
            df.loc[index, ['theoretical_a_win_rate']] = theoretical_a_win_rate
            df.loc[index, ['theoretical_a_win_rate_abs_error']] = abs(theoretical_a_win_rate - EVEN)

        # あとで設定する
        if theoretical_no_win_match_rate is None:
            df.loc[index, ['theoretical_no_win_match_rate']] = OUT_OF_P
        else:
            df.loc[index, ['theoretical_no_win_match_rate']] = theoretical_no_win_match_rate


    @staticmethod
    def to_csv(df, spec):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)

        df.to_csv(csv_file_path,
                columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'theoretical_a_win_rate', 'theoretical_a_win_rate_abs_error', 'theoretical_no_win_match_rate'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        return csv_file_path


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        on_each : func
            record 引数を受け取る関数
        """
        for         turn_system_name  ,     failure_rate  ,     p  ,     span  ,     t_step  ,     h_step  ,     shortest_coins  ,     upper_limit_coins  ,     theoretical_a_win_rate  ,     theoretical_a_win_rate_abs_error  ,     theoretical_no_win_match_rate in\
            zip(df['turn_system_name'], df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['theoretical_a_win_rate'], df['theoretical_a_win_rate_abs_error'], df['theoretical_no_win_match_rate']):

            # レコード作成
            record = TheoreticalProbabilityRecord(
                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    theoretical_a_win_rate=theoretical_a_win_rate,
                    theoretical_a_win_rate_abs_error=theoretical_a_win_rate_abs_error,
                    theoretical_no_win_match_rate=theoretical_no_win_match_rate)

            on_each(record)


class TheoreticalProbabilityTrialResultsRecord():
    """理論的確率の試行結果レコード"""


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, trial_a_win_rate, trial_a_win_rate_abs_error, trial_no_win_match_rate):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._trial_a_win_rate = trial_a_win_rate
        self._trial_a_win_rate_abs_error = trial_a_win_rate_abs_error
        self._trial_no_win_match_rate = trial_no_win_match_rate


    @property
    def turn_system_name(self):
        return self._turn_system_name


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def p(self):
        return self._p


    @property
    def span(self):
        return self._span


    @property
    def t_step(self):
        return self._t_step


    @property
    def h_step(self):
        return self._h_step


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def trial_a_win_rate(self):
        return self._trial_a_win_rate


    @property
    def trial_a_win_rate_abs_error(self):
        return self._trial_a_win_rate_abs_error


    @property
    def trial_no_win_match_rate(self):
        return self._trial_no_win_match_rate


class TheoreticalProbabilityTrialResultsTable():
    """理論的確率の試行結果テーブル"""


    _dtype = {
        'turn_system_name':'object',     # string 型は無い？
        'failure_rate':'float64',
        'p':'float64',
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'trial_a_win_rate':'float64',
        'trial_a_win_rate_abs_error':'float64',
        'trial_no_win_match_rate':'float64'}


    @classmethod
    def new_data_frame(clazz):
        df = pd.DataFrame.from_dict({
                'turn_system_name': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'trial_a_win_rate': [],
                'trial_a_win_rate_abs_error': [],
                'trial_no_win_match_rate': []}).astype(clazz._dtype)

        return df


    @classmethod
    def read_df(clazz, spec, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        df : DataFrame
            データフレーム
        is_new : bool
            新規作成されたか？
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityTrialResultsFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)


        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                df = TheoreticalProbabilityTrialResultsTable.new_data_frame()
            else:
                df = None

        else:
            df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)


        return df, is_new


    @staticmethod
    def append_new_record(df, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, trial_a_win_rate, trial_no_win_match_rate):
        index = len(df.index)


        df.loc[index, [ 'turn_system_name']] = turn_system_name   # FIXME ここで型エラー？

        df.loc[index, ['failure_rate']] = failure_rate
        df.loc[index, ['p']] = p
        df.loc[index, ['span']] = span
        df.loc[index, ['t_step']] = t_step
        df.loc[index, ['h_step']] = h_step
        df.loc[index, ['shortest_coins']] = shortest_coins
        df.loc[index, ['upper_limit_coins']] = upper_limit_coins

        # あとで設定する
        if trial_a_win_rate is None:
            df.loc[index, ['trial_a_win_rate']] = OUT_OF_P
            df.loc[index, ['trial_a_win_rate_abs_error']] = abs(OUT_OF_P - EVEN)
        else:
            df.loc[index, ['trial_a_win_rate']] = trial_a_win_rate
            df.loc[index, ['trial_a_win_rate_abs_error']] = abs(trial_a_win_rate - EVEN)

        # あとで設定する
        if trial_no_win_match_rate is None:
            df.loc[index, ['trial_no_win_match_rate']] = OUT_OF_P

        else:
            df.loc[index, ['trial_no_win_match_rate']] = trial_no_win_match_rate


    @staticmethod
    def to_csv(df, spec):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityTrialResultsFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)

        df.to_csv(csv_file_path,
                columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'trial_a_win_rate', 'trial_a_win_rate_abs_error', 'trial_no_win_match_rate'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        return csv_file_path


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        on_each : func
            record 引数を受け取る関数
        """
        for         turn_system_name,         failure_rate  ,     p  ,     span  ,     t_step  ,     h_step  ,     shortest_coins  ,     upper_limit_coins  ,     trial_a_win_rate  ,     trial_a_win_rate_abs_error  ,     trial_no_win_match_rate in\
            zip(df['turn_system_name']  , df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['trial_a_win_rate'], df['trial_a_win_rate_abs_error'], df['trial_no_win_match_rate']):

            # レコード作成
            record = EmpiricalProbabilityRecord(
                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    trial_a_win_rate=trial_a_win_rate,
                    trial_a_win_rate_abs_error=trial_a_win_rate_abs_error,
                    trial_no_win_match_rate=trial_no_win_match_rate)

            on_each(record)


class TheoreticalProbabilityBestRecord():
    """理論的確率ベスト・レコード"""


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, theoretical_a_win_rate, theoretical_no_win_match_rate):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._theoretical_a_win_rate = theoretical_a_win_rate
        self._theoretical_no_win_match_rate = theoretical_no_win_match_rate


    @property
    def turn_system_name(self):
        return self._turn_system_name


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def p(self):
        return self._p


    @property
    def span(self):
        return self._span


    @property
    def t_step(self):
        return self._t_step


    @property
    def h_step(self):
        return self._h_step


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def theoretical_a_win_rate(self):
        return self._theoretical_a_win_rate


    @property
    def theoretical_no_win_match_rate(self):
        return self._theoretical_no_win_match_rate


class TheoreticalProbabilityBestTable():
    """理論的確率ベスト・テーブル"""


    _dtype = {
        'turn_system_name':'object',     # string 型は無い？
        'failure_rate':'float64',
        'p':'float64',
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'theoretical_a_win_rate':'float64',
        'theoretical_no_win_match_rate':'float64'}


    @classmethod
    def new_data_frame(clazz):
        df = pd.DataFrame.from_dict({
                'turn_system_name': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'theoretical_a_win_rate': [],
                'theoretical_no_win_match_rate': []}).astype(clazz._dtype)

        return df


    @staticmethod
    def create_none_record():
        return TheoreticalProbabilityBestRecord(
                turn_system_name=None,
                failure_rate=None,
                p=None,
                span=None,
                t_step=None,
                h_step=None,
                shortest_coins=None,
                upper_limit_coins=None,
                theoretical_a_win_rate=None,
                theoretical_no_win_match_rate=None)


    @staticmethod
    def append_record(df, record):
        index = len(df.index)
        df.loc[index, ['turn_system_name'] ] = record.turn_system_name
        df.loc[index, ['failure_rate']] = record.failure_rate
        df.loc[index, ['p']] = record.p
        df.loc[index, ['span']] = record.span
        df.loc[index, ['t_step']] = record.t_step
        df.loc[index, ['h_step']] = record.h_step
        df.loc[index, ['shortest_coins']] = record.shortest_coins
        df.loc[index, ['upper_limit_coins']] = record.upper_limit_coins
        df.loc[index, ['theoretical_a_win_rate']] = record.theoretical_a_win_rate
        df.loc[index, ['theoretical_no_win_match_rate']] = record.theoretical_no_win_match_rate


    @staticmethod
    def upsert_record(df, record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        df : DataFrame
            データフレーム
        record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        is_dirty : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """

        # 該当レコードセット
        key = (df['span']==span) & (df['t_step']==t_step) & (df['h_step']==h_step)

        # TODO データが既存なら、差異があれば、上書き
        if key.any():
            is_dirty =\
                df.loc[key, ['turn_system_name'] ] != record.turn_system_name or\
                df.loc[key, ['failure_rate']] != record.failure_rate or\
                df.loc[key, ['p']] != record.p or\
                df.loc[key, ['span']] != record.span or\
                df.loc[key, ['t_step']] != record.t_step or\
                df.loc[key, ['h_step']] != record.h_step or\
                df.loc[key, ['shortest_coins']] != record.shortest_coins or\
                df.loc[key, ['upper_limit_coins']] != record.upper_limit_coins or\
                df.loc[key, ['theoretical_a_win_rate']] != record.theoretical_a_win_rate or\
                df.loc[key, ['theoretical_no_win_match_rate']] != record.theoretical_no_win_match_rate

            if is_dirty:
                df.loc[key, ['turn_system_name'] ] = record.turn_system_name
                df.loc[key, ['failure_rate']] = record.failure_rate
                df.loc[key, ['p']] = record.p
                df.loc[key, ['span']] = record.span
                df.loc[key, ['t_step']] = record.t_step
                df.loc[key, ['h_step']] = record.h_step
                df.loc[key, ['shortest_coins']] = record.shortest_coins
                df.loc[key, ['upper_limit_coins']] = record.upper_limit_coins
                df.loc[key, ['theoretical_a_win_rate']] = record.theoretical_a_win_rate
                df.loc[key, ['theoretical_no_win_match_rate']] = record.theoretical_no_win_match_rate

        # データが既存でないなら、新規追加
        else:
            self.append_record(df=df, record=record)
            is_dirty = True


        return is_dirty


    @classmethod
    def read_df(clazz, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？

        Returns
        -------
        df : DataFrame
            データフレーム
        is_new : bool
            新規作成されたか？
        """

        csv_file_path = TheoreticalProbabilityBestFilePaths.as_csv()

        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                df = TheoreticalProbabilityBestTable.new_data_frame()
            else:
                df = None

        else:
            df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)
        

        return df, is_new


    @staticmethod
    def get_record_by_key(df, key):
        """
        Returns
        -------

        """
        return TheoreticalProbabilityBestRecord(
                turn_system_name=df.loc[key, ['turn_system_name']].iat[0,0],
                failure_rate=df.loc[key, ['failure_rate']].iat[0,0],
                p=df.loc[key, ['p']].iat[0,0],
                span=df.loc[key, ['span']].iat[0,0],
                t_step=df.loc[key, ['t_step']].iat[0,0],
                h_step=df.loc[key, ['h_step']].iat[0,0],
                shortest_coins=df.loc[key, ['shortest_coins']].iat[0,0],
                upper_limit_coins=df.loc[key, ['upper_limit_coins']].iat[0,0],
                theoretical_a_win_rate=df.loc[key, ['theoretical_a_win_rate']].iat[0,0],
                theoretical_no_win_match_rate=df.loc[key, ['theoretical_no_win_match_rate']].iat[0,0])


    @staticmethod
    def to_csv(df):
        """CSV形式でファイルへ保存

        Parameters
        ----------
        df : DataFrame
            データフレーム
        
        Returns
        -------
        csv_file_path : str
            書き込んだファイルへのパス
        """
        # CSVファイルパス（書き込むファイル）
        csv_file_path = TheoreticalProbabilityBestFilePaths.as_csv()

        df.to_csv(csv_file_path,
                columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'theoretical_a_win_rate', 'theoretical_no_win_match_rate'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        return csv_file_path


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        """
        for         turn_system_name,       failure_rate,       p,       span,       t_step,       h_step,       shortest_coins,       upper_limit_coins,       theoretical_a_win_rate,       theoretical_no_win_match_rate in\
            zip(df['turn_system_name'], df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['theoretical_a_win_rate'], df['theoretical_no_win_match_rate']):

            # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
            span = round_letro(span)
            t_step = round_letro(t_step)
            h_step = round_letro(h_step)
            shortest_coins = round_letro(shortest_coins)
            upper_limit_coins = round_letro(upper_limit_coins)

            # レコード作成
            record = TheoreticalProbabilityBestRecord(
                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    theoretical_a_win_rate=theoretical_a_win_rate,
                    theoretical_no_win_match_rate=theoretical_no_win_match_rate)

            on_each(record)
