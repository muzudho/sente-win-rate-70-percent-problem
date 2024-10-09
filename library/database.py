#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import time
import random
import datetime
import numpy as np
import pandas as pd

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_OUT_OF_ERROR, OUT_OF_P, EVEN, round_letro, Converter, ThreeRates
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths, TheoreticalProbabilityFilePaths, TheoreticalProbabilityBestFilePaths, KakukinDataSheetFilePaths


CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


###########
# MARK: KDS
###########

class KakukinDataSheetRecord():
    """［かくきんデータ・シート］レコード"""


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, trial_series, series_shortest_coins, series_longest_coins, wins_a, wins_b, succucessful_series, s_ful_wins_a, s_ful_wins_b, s_pts_wins_a, s_pts_wins_b, failed_series, f_ful_wins_a, f_ful_wins_b, f_pts_wins_a, f_pts_wins_b, no_wins_ab):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._tail_step = t_step
        self._head_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._trial_series = trial_series
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
        return self._tail_step


    @property
    def h_step(self):
        return self._head_step


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def trial_series(self):
        return self._trial_series


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
    """［かくきんデータ・シート］テーブル"""


    _dtype = {
        'turn_system_name':'object',    # string型は無い？
        'failure_rate':'float64',
        'p':'float64',
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'trial_series':'int64',
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


    def __init__(self, df, trial_series, turn_system_id, failure_rate):
        """初期化

        Parameters
        ----------
        df : DataFrame
            データフレーム
        """
        self._df = df
        self._trial_series = trial_series
        self._turn_system_id = turn_system_id
        self._failure_rate = failure_rate


    @classmethod
    def new_empty_table(clazz, trial_series, turn_system_id, failure_rate):
        kds_df = pd.DataFrame.from_dict({
                'p':[], # インデックス
                'turn_system_name':[],
                'failure_rate':[],
                'span':[],
                't_step':[],
                'h_step':[],
                'shortest_coins':[],
                'upper_limit_coins':[],
                'trial_series':[],
                'series_shortest_coins':[],
                'series_longest_coins':[],
                'wins_a':[],
                'wins_b':[],
                'succucessful_series':[],
                's_ful_wins_a':[],
                's_ful_wins_b':[],
                's_pts_wins_a':[],
                's_pts_wins_b':[],
                'failed_series':[],
                'f_ful_wins_a':[],
                'f_ful_wins_b':[],
                'f_pts_wins_a':[],
                'f_pts_wins_b':[],
                'no_wins_ab':[]})
        clazz.setup_data_frame(df=kds_df)
        return KakukinDataSheetTable(
                df=kds_df,
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)


    @classmethod
    def read_csv(clazz, trial_series, turn_system_id, failure_rate, new_if_it_no_exists=False):
        """

        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［手番が回ってくる制度］
        failure_rate : float
            ［将棋の引分け率］
        """

        csv_file_path = KakukinDataSheetFilePaths.as_sheet_csv(
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)

        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                kds_table = KakukinDataSheetTable.new_empty_table(
                        trial_series=trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate)
            else:
                kds_table = None
        else:
            df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=df)
            kds_table = KakukinDataSheetTable(
                    df=df,
                    trial_series=trial_series,
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate)


        return kds_table, is_new


    @property
    def df(self):
        """データフレーム"""
        return self._df


    @property
    def trial_series(self):
        return self._trial_series

    
    @property
    def turn_system_id(self):
        return self._turn_system_id
    

    @property
    def failure_rate(self):
        return self._failure_rate


    @classmethod
    def setup_data_frame(clazz, df):
        """データフレームの設定"""

        # データ型の設定
        df.astype(clazz._dtype)

        # trial_series と turn_system_name と failure_rate はファイル名と同じはず
        df.set_index(
                ['p'],
                inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します


    def assert_welcome_record(self, welcome_record):
        if welcome_record.trial_series != self._trial_series:
            raise ValueError(f"ファイル名と trial_series 列で内容が異なるのはおかしいです {welcome_record.trial_series=}  {self._trial_series=}")

        specified_turn_system_name = Converter.turn_system_id_to_name(self._turn_system_id)
        if welcome_record.turn_system_name != specified_turn_system_name:
            raise ValueError(f"ファイル名と turn_system_name 列で内容が異なるのはおかしいです {welcome_record.turn_system_name=}  {specified_turn_system_name=}")

        if welcome_record.failure_rate != self._failure_rate:
            raise ValueError(f"ファイル名と failure_rate 列で内容が異なるのはおかしいです {welcome_record.failure_rate=}  {self._failure_rate=}")


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        shall_record_change : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """

        self.assert_welcome_record(welcome_record=welcome_record)


        # インデックス
        # -----------
        # index : any
        #   インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
        #   <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        index = welcome_record.p


        # データ変更判定
        # -------------
        is_new_index = index not in self._df['span']

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # trial_series と turn_system_name と failure_rate はファイル名と同じはず
            shall_record_change =\
                self._df['span'][index] != welcome_record.span or\
                self._df['t_step'][index] != welcome_record.t_step or\
                self._df['h_step'][index] != welcome_record.h_step or\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['trial_series'][index] != welcome_record.trial_series or\
                self._df['series_shortest_coins'][index] != welcome_record.series_shortest_coins or\
                self._df['series_longest_coins'][index] != welcome_record.series_longest_coins or\
                self._df['wins_a'][index] != welcome_record.wins_a or\
                self._df['wins_b'][index] != welcome_record.wins_b or\
                self._df['succucessful_series'][index] != welcome_record.succucessful_series or\
                self._df['s_ful_wins_a'][index] != welcome_record.s_ful_wins_a or\
                self._df['s_ful_wins_b'][index] != welcome_record.s_ful_wins_b or\
                self._df['s_pts_wins_a'][index] != welcome_record.s_pts_wins_a or\
                self._df['s_pts_wins_b'][index] != welcome_record.s_pts_wins_b or\
                self._df['failed_series'][index] != welcome_record.failed_series or\
                self._df['f_ful_wins_a'][index] != welcome_record.f_ful_wins_a or\
                self._df['f_ful_wins_b'][index] != welcome_record.f_ful_wins_b or\
                self._df['f_pts_wins_a'][index] != welcome_record.f_pts_wins_a or\
                self._df['f_pts_wins_b'][index] != welcome_record.f_pts_wins_b or\
                self._df['no_wins_ab'][index] != welcome_record.no_wins_ab


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # p はインデックス
                'span': welcome_record.span,
                't_step': welcome_record.t_step,
                'h_step': welcome_record.h_step,
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'trial_series': welcome_record.trial_series,
                'series_shortest_coins': welcome_record.series_shortest_coins,
                'series_longest_coins': welcome_record.series_longest_coins,
                'wins_a': welcome_record.wins_a,
                'wins_b': welcome_record.wins_b,
                'succucessful_series': welcome_record.succucessful_series,
                's_ful_wins_a': welcome_record.s_ful_wins_a,
                's_ful_wins_b': welcome_record.s_ful_wins_b,
                's_pts_wins_a': welcome_record.s_pts_wins_a,
                's_pts_wins_b': welcome_record.s_pts_wins_b,
                'failed_series': welcome_record.failed_series,
                'f_ful_wins_a': welcome_record.f_ful_wins_a,
                'f_ful_wins_b': welcome_record.f_ful_wins_b,
                'f_pts_wins_a': welcome_record.f_pts_wins_a,
                'f_pts_wins_b': welcome_record.f_pts_wins_b,
                'no_wins_ab': welcome_record.no_wins_ab}

        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        # CSVファイルパス
        csv_file_path = KakukinDataSheetFilePaths.as_sheet_csv(
                trial_series=self._trial_series,
                turn_system_id=self._turn_system_id,
                failure_rate=self._failure_rate)

        # p はインデックス
        self._df.to_csv(csv_file_path,
                columns=['turn_system_name', 'failure_rate', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'trial_series', 'series_shortest_coins', 'series_longest_coins', 'wins_a', 'wins_b', 'succucessful_series', 's_ful_wins_a', 's_ful_wins_b', 's_pts_wins_a', 's_pts_wins_b', 'failed_series', 'f_ful_wins_a', 'f_ful_wins_b', 'f_pts_wins_a', 'f_pts_wins_b', 'no_wins_ab'])

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(      turn_system_name  ,     failure_rate  ,     p  ,     span  ,     t_step  ,     h_step  ,     shortest_coins  ,     upper_limit_coins  ,     trial_series  ,     series_shortest_coins  ,     series_longest_coins  ,     wins_a  ,     wins_b  ,     succucessful_series  ,     s_ful_wins_a  ,     s_ful_wins_b  ,     s_pts_wins_a  ,     s_pts_wins_b  ,     failed_series  ,     f_ful_wins_a  ,     f_ful_wins_b  ,     f_pts_wins_a  ,     f_pts_wins_b  ,     no_wins_ab) in\
            enumerate(zip(df['turn_system_name'], df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['trial_series'], df['series_shortest_coins'], df['series_longest_coins'], df['wins_a'], df['wins_b'], df['succucessful_series'], df['s_ful_wins_a'], df['s_ful_wins_b'], df['s_pts_wins_a'], df['s_pts_wins_b'], df['failed_series'], df['f_ful_wins_a'], df['f_ful_wins_b'], df['f_pts_wins_a'], df['f_pts_wins_b'], df['no_wins_ab'])):

            # p はインデックス
            p = df.index[row_number]

            # レコード作成
            record = KakukinDataSheetRecord(
                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    trial_series=trial_series,
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


###########
# MARK: TPB
###########

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
        # turn_system_name, failure_rate, p はインデックス
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'theoretical_a_win_rate':'float64',
        'theoretical_no_win_match_rate':'float64'}


    def __init__(self, df):
        self._df = df


    @classmethod
    def setup_data_frame(clazz, df):
        """データフレームの設定"""

        # データ型の設定
        df.astype(clazz._dtype)

        df.set_index(
                ['turn_system_name', 'failure_rate', 'p'],
                inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します


    @classmethod
    def new_empty_table(clazz):
        # turn_system_name, failure_rate, p はインデックス
        tpb_df = pd.DataFrame.from_dict({
                'turn_system_name': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'theoretical_a_win_rate': [],
                'theoretical_no_win_match_rate': []})
        clazz.setup_data_frame(df=tpd_df)
        return TheoreticalProbabilityBestTable(df=tpb_df)


    @classmethod
    def read_csv(clazz, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？

        Returns
        -------
        tpb_table : TheoreticalProbabilityBestTable
            テーブル
        is_new : bool
            新規作成されたか？
        """

        csv_file_path = TheoreticalProbabilityBestFilePaths.as_csv()

        is_new = not os.path.isfile(csv_file_path)
        # ファイルが存在しなかった場合
        if is_new:
            if new_if_it_no_exists:
                tpb_table = TheoreticalProbabilityBestTable.new_empty_table()
            else:
                tpb_table = None

        # ファイルが存在した場合
        else:
            tpb_df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=tpb_df)
            tpb_table = TheoreticalProbabilityBestTable(df=tpb_df)


        return tpb_table, is_new


    @property
    def df(self):
        return self._df


    def create_none_record(self):
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


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        shall_record_change : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """


        # インデックス
        # -----------
        # index : any
        #   インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
        #   <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        # turn_system_name, failure_rate, p はインデックス
        index = (welcome_record.turn_system_name, welcome_record.failure_rate, welcome_record.p)


        # データ変更判定
        # -------------
        is_new_index = index not in self._df['turn_system_name']


        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # turn_system_name, failure_rate, p はインデックス
            shall_record_change =\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['theoretical_a_win_rate'][index] != welcome_record.theoretical_a_win_rate or\
                self._df['theoretical_no_win_match_rate'][index] != welcome_record.theoretical_no_win_match_rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # turn_system_name, failure_rate, p はインデックス
                'span': welcome_record.span,
                't_step': welcome_record.t_step,
                'h_step': welcome_record.h_step,
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'theoretical_a_win_rate': welcome_record.theoretical_a_win_rate,
                'theoretical_no_win_match_rate': welcome_record.theoretical_no_win_match_rate}

        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self):
        """CSV形式でファイルへ保存
        
        Returns
        -------
        csv_file_path : str
            書き込んだファイルへのパス
        """
        # CSVファイルパス（書き込むファイル）
        csv_file_path = TheoreticalProbabilityBestFilePaths.as_csv()

        # turn_system_name, failure_rate, p はインデックス
        self._df.to_csv(csv_file_path,
                columns=['span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'theoretical_a_win_rate', 'theoretical_no_win_match_rate'])

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            関数
        """

        df = self._df

        for row_number,(      turn_system_name,       failure_rate,       p,       span,       t_step,       h_step,       shortest_coins,       upper_limit_coins,       theoretical_a_win_rate,       theoretical_no_win_match_rate) in\
            enumerate(zip(df['turn_system_name'], df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['theoretical_a_win_rate'], df['theoretical_no_win_match_rate'])):

            # turn_system_name, failure_rate, p はインデックス
            turn_system_name, failure_rate, p = df.index[row_number]

            # FIXME これはもう要らないのでは？
            # # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
            # span = round_letro(span)
            # t_step = round_letro(t_step)
            # h_step = round_letro(h_step)
            # shortest_coins = round_letro(shortest_coins)
            # upper_limit_coins = round_letro(upper_limit_coins)

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


##########
# MARK: TP
##########

class TheoreticalProbabilityRecord():


    def __init__(self, span, t_step, h_step, shortest_coins, upper_limit_coins, theoretical_a_win_rate, theoretical_no_win_match_rate):
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._theoretical_a_win_rate = theoretical_a_win_rate
        self._theoretical_no_win_match_rate = theoretical_no_win_match_rate


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


class TheoreticalProbabilityTable():
    """理論的確率データ"""


    _dtype = {
        # span, t_step, h_step はインデックス
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'theoretical_a_win_rate':'float64',
        'theoretical_no_win_match_rate':'float64'}


    def __init__(self, df, spec):
        self._df = df
        self._spec = spec


    @classmethod
    def new_empty_table(clazz, spec):
        # span, t_step, h_step はインデックス
        tp_df = pd.DataFrame.from_dict({
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'theoretical_a_win_rate': [],
                'theoretical_no_win_match_rate': []})
        clazz.setup_data_frame(tp_df)
        return TheoreticalProbabilityTable(df=tp_df, spec=spec)


    @classmethod
    def read_csv(clazz, spec, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        tp_table : TheoreticalProbabilityTable
            テーブル、またはナン
        is_new : bool
            新規作成されたか？
        """

        csv_file_path = TheoreticalProbabilityFilePaths.as_csv(
                turn_system_id=spec.turn_system_id,
                failure_rate=spec.failure_rate,
                p=spec.p)

        is_file_exists = os.path.isfile(csv_file_path)

        # ファイルが既存だったら、そのファイルを読む
        if is_file_exists:
            while True: # retry
                try:
                    df = pd.read_csv(csv_file_path, encoding="utf8",
                            dtype=clazz._dtype)
                    clazz.setup_data_frame(df)
                    tp_table = TheoreticalProbabilityTable(df=df, spec=spec)
                    break
                
                # テーブルに列が無かったら、ファイル生成のタイミングと被ったか？ リトライしてみる
                except pd.errors.EmptyDataError as e:
                    wait_for_seconds = random.randint(30, 5*60)
                    print(f"[{datetime.datetime.now()}] read to failed. wait for {wait_for_seconds} seconds and retry. {e}")

        # ファイルが存在しなかった場合
        else:
            if new_if_it_no_exists:
                tp_table = TheoreticalProbabilityTable.new_empty_table(spec=spec)
            else:
                tp_table = None


        return tp_table, not is_file_exists


    @property
    def df(self):
        return self._df


    @classmethod
    def setup_data_frame(clazz, df):
        """データフレームの設定"""

        # データ型の設定
        df.astype(clazz._dtype)

        # インデックスの設定
        df.set_index(
                ['span', 't_step', 'h_step'],
                inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        shall_record_change : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """

        # インデックス
        # -----------
        # index : any
        #   インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
        #   <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        index = (welcome_record.span, welcome_record.t_step, welcome_record.h_step)

        # データ変更判定
        # -------------
        is_new_index = index not in self._df['shortest_coins']

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # span, t_step, h_step はインデックス
            shall_record_change =\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['theoretical_a_win_rate'][index] != welcome_record.theoretical_a_win_rate or\
                self._df['theoretical_no_win_match_rate'][index] != welcome_record.theoretical_no_win_match_rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # span, t_step, h_step はインデックス
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'theoretical_a_win_rate': welcome_record.theoretical_a_win_rate,
                'theoretical_no_win_match_rate': welcome_record.theoretical_no_win_match_rate}

        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        csv_file_path = TheoreticalProbabilityFilePaths.as_csv(
                p=self._spec.p,
                failure_rate=self._spec.failure_rate,
                turn_system_id=self._spec.turn_system_id)

        # span, t_step, h_step はインデックス
        self._df.to_csv(
                csv_file_path,
                columns=['shortest_coins', 'upper_limit_coins', 'theoretical_a_win_rate', 'theoretical_no_win_match_rate'])

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(      shortest_coins  ,     upper_limit_coins  ,     theoretical_a_win_rate  ,     theoretical_no_win_match_rate) in\
            enumerate(zip(df['shortest_coins'], df['upper_limit_coins'], df['theoretical_a_win_rate'], df['theoretical_no_win_match_rate'])):

            # span, t_step, h_step はインデックス
            span, t_step, h_step = df.index[row_number]

            # レコード作成
            record = TheoreticalProbabilityRecord(
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    theoretical_a_win_rate=theoretical_a_win_rate,
                    theoretical_no_win_match_rate=theoretical_no_win_match_rate)

            on_each(record)


############
# MARK: EPDT
############

class EmpiricalProbabilityDuringTrialsRecord():
    """試行中の経験論的確率レコード"""


    def __init__(self, p, best_p, best_p_error, best_span, best_t_step, best_h_step, latest_p, latest_p_error, latest_span, latest_t_step, latest_h_step, candidate_history_text):
        """初期化
        
        Parameters
        ----------
        best_p : float
            ［調整後の表が出る確率］列を更新
        best_p_error : float
            ［調整後の表が出る確率の５割との誤差］
        best_span : int
            ［目標の点数］列を更新 
        best_t_step : int
            ［裏番で勝ったときの勝ち点］列を更新
        best_h_step : int
            ［表番で勝ったときの勝ち点］列を更新
        latest_p : float
            ［調整後の表が出る確率］列を更新
        latest_p_error : float
            ［調整後の表が出る確率の５割との誤差］
        latest_span : int
            ［目標の点数］列を更新 
        latest_t_step : int
            ［裏番で勝ったときの勝ち点］列を更新
        latest_h_step : int
            ［表番で勝ったときの勝ち点］列を更新
        candidate_history_text : str
            ［シリーズ・ルール候補］
        """

        # FIXME このコードはもういらない？ pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_span = round_letro(best_span)
        best_t_step = round_letro(best_t_step)
        best_h_step = round_letro(best_h_step)
        latest_span = round_letro(latest_span)
        latest_t_step = round_letro(latest_t_step)
        latest_h_step = round_letro(latest_h_step)

        self._p=p
        self._best_p=best_p
        self._best_p_error=best_p_error
        self._best_span=best_span
        self._best_t_step=best_t_step
        self._best_h_step=best_h_step
        self._latest_p=latest_p
        self._latest_p_error=latest_p_error
        self._latest_span=latest_span
        self._latest_t_step=latest_t_step
        self._latest_h_step=latest_h_step
        self._candidate_history_text=candidate_history_text


    @property
    def p(self):
        return self._p


    @property
    def best_p(self):
        return self._best_p


    @property
    def best_p_error(self):
        return self._best_p_error


    @property
    def best_span(self):
        return self._best_span


    @property
    def best_t_step(self):
        return self._best_t_step


    @property
    def best_h_step(self):
        return self._best_h_step


    @property
    def latest_p(self):
        return self._latest_p


    @property
    def latest_p_error(self):
        return self._latest_p_error


    @property
    def latest_span(self):
        return self._latest_span


    @property
    def latest_t_step(self):
        return self._latest_t_step


    @property
    def latest_h_step(self):
        return self._latest_h_step


    @property
    def candidate_history_text(self):
        return self._candidate_history_text


class EmpiricalProbabilityDuringTrialsTable():
    """試行中の経験的確率論テーブル
    """


    _dtype = {
        # p はインデックス
        'best_p':'float64',
        'best_p_error':'float64',
        'best_span':'int64',
        'best_t_step':'int64',
        'best_h_step':'int64',
        'latest_p':'float64',
        'latest_p_error':'float64',
        'latest_span':'int64',
        'latest_t_step':'int64',
        'latest_h_step':'int64',
        'candidate_history_text':'object'}


    def __init__(self, df, trial_series, turn_system_id, failure_rate):
        self._df = df
        self._trial_series = trial_series
        self._turn_system_id = turn_system_id
        self._failure_rate = failure_rate


    @classmethod
    def new_empty_table(clazz, trial_series, turn_system_id, failure_rate):
        # p はインデックス
        ep_df = pd.DataFrame.from_dict({
            'p': [],
            'best_p': [],
            'best_p_error': [],
            'best_span': [],
            'best_t_step': [],
            'best_h_step': [],
            'latest_p': [],
            'latest_p_error': [],
            'latest_span': [],
            'latest_t_step': [],
            'latest_h_step': [],
            'candidate_history_text': []})
        clazz.setup_data_frame(df=ep_df)
        return EmpiricalProbabilityDuringTrialsTable(
                df=ep_df,
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)


    @classmethod
    def read_csv(clazz, trial_series, turn_system_id, failure_rate, new_if_it_no_exists):
        """

        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［手番が回ってくる制度］
        failure_rate : float
            ［将棋の引分け率］
        """

        csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv(
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)

        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                ep_table = EmpiricalProbabilityDuringTrialsTable.new_empty_table(
                        trial_series=trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate)
            else:
                ep_table = None
        else:
            df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=df)
            ep_table = EmpiricalProbabilityDuringTrialsTable(
                    df,
                    trial_series=trial_series,
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate)


        return ep_table, is_new


    @property
    def df(self):
        return self._df


    @property
    def trial_series(self):
        return self._trial_series


    @property
    def turn_system_id(self):
        return self._turn_system_id


    @property
    def failure_rate(self):
        return self._failure_rate


    @classmethod
    def setup_data_frame(clazz, df, shall_set_index=True):
        """データフレームの設定"""

        # データ型の設定
        df.astype(clazz._dtype)

        if shall_set_index:
            df.set_index(
                    ['p'],
                    inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します


    def exists_index(self, p):
        return p in self._df['best_p']


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        is_record_update : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """

        # インデックス
        # -----------
        # index : any
        #   インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
        #   <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        index = welcome_record.p

        # データ変更判定
        # -------------
        is_new_index = not self.exists_index(index)

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # p はインデックス
            shall_record_change =\
                self._df['best_p'][index] != welcome_record.best_p or\
                self._df['best_p_error'][index] != welcome_record.best_p_error or\
                self._df['best_span'][index] != welcome_record.best_span or\
                self._df['best_t_step'][index] != welcome_record.best_t_step or\
                self._df['best_h_step'][index] != welcome_record.best_h_step or\
                self._df['latest_p'][index] != welcome_record.latest_p or\
                self._df['latest_p_error'][index] != welcome_record.latest_p_error or\
                self._df['latest_span'][index] != welcome_record.latest_span or\
                self._df['latest_t_step'][index] != welcome_record.latest_t_step or\
                self._df['latest_h_step'][index] != welcome_record.latest_h_step or\
                self._df['candidate_history_text'][index] != welcome_record.candidate_history_text


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # 'p' はインデックス
                'best_p': welcome_record.best_p,
                'best_p_error': welcome_record.best_p_error,
                'best_span': welcome_record.best_span,
                'best_t_step': welcome_record.best_t_step,
                'best_h_step': welcome_record.best_h_step,
                'latest_p': welcome_record.latest_p,
                'latest_p_error': welcome_record.latest_p_error,
                'latest_span': welcome_record.latest_span,
                'latest_t_step': welcome_record.latest_t_step,
                'latest_h_step': welcome_record.latest_h_step,
                'candidate_history_text': welcome_record.candidate_history_text}

        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv(
                trial_series=self._trial_series,
                turn_system_id=self._turn_system_id,
                failure_rate=self._failure_rate)

        #print(f"[{datetime.datetime.now()}] write file to `{csv_file_path}` ...")

        # CSV保存
        self._df.to_csv(
                csv_file_path,
                # ［シリーズ・ルール候補］列は長くなるので末尾に置きたい
                # 'p' はインデックス
                columns=['best_p', 'best_p_error', 'best_span', 'best_t_step', 'best_h_step', 'latest_p', 'latest_p_error', 'latest_span', 'latest_t_step', 'latest_h_step', 'candidate_history_text'])

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            関数
        """

        df = self._df

        for row_number,(        best_p,       best_p_error,       best_span,       best_t_step,       best_h_step,       latest_p,       latest_p_error,       latest_span,       latest_t_step,       latest_h_step,       candidate_history_text) in\
            enumerate(zip(df['best_p'], df['best_p_error'], df['best_span'], df['best_t_step'], df['best_h_step'], df['latest_p'], df['latest_p_error'], df['latest_span'], df['latest_t_step'], df['latest_h_step'], df['candidate_history_text'])):

            # インデックスの縦方向のリストから、p を取得
            p = df.index[row_number]

            # レコード作成
            record = EmpiricalProbabilityDuringTrialsRecord(
                    p=p,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_span=best_span,
                    best_t_step=best_t_step,
                    best_h_step=best_h_step,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_span=latest_span,
                    latest_t_step=latest_t_step,
                    latest_h_step=latest_h_step,
                    candidate_history_text=candidate_history_text)

            on_each(record)


###########
# MARK: CPT
###########

class CalculateProbabilityTable():


    @staticmethod
    def get_let_calculate_probability_df():
        """TODO read_csv に名称変更したい"""
        cp_df = pd.read_csv(CSV_FILE_PATH_CAL_P, encoding="utf8",
                dtype={
                    'p':'float64',
                    'p_time':'int64',
                    'q_time':'int64',
                    'best_p':'float64',
                    'best_p_error':'float64',
                    'comment':'object'
                })

        return cp_df
