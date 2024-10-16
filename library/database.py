#
# NOTE pandas のデータフレームの列の型の初期値が float なので、いちいち設定する手間を省くため、読み込み時にそれぞれ型を明示しておく
#
import os
import time
import random
import datetime
import numpy as np
import pandas as pd

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_OUT_OF_ERROR, EVEN, round_letro, Converter, ThreeRates, RenamingBackup
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths, TheoreticalProbabilityRatesFilePaths, TheoreticalProbabilityFilePaths, TheoreticalProbabilityBestFilePaths, KakukinDataSheetFilePaths, GameTreeFilePaths
from scripts import IntervalForRetry


CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


class FileReadResult():
    """ファイル読込結果"""


    def __init__(self, file_path, is_file_not_found):
        """初期化"""
        self._file_path = file_path
        self._is_file_not_found = is_file_not_found


    @property
    def file_path(self):
        return self._file_path


    @property
    def is_file_not_found(self):
        return self._is_file_not_found


###########
# MARK: KDS
###########

class KakukinDataSheetRecord():
    """［かくきんデータ・シート］レコード"""


    def __init__(self, p, turn_system_name, failure_rate, span, t_step, h_step, shortest_coins, upper_limit_coins, expected_a_win_rate, expected_no_win_match_rate, trial_series, series_shortest_coins, series_longest_coins, wins_a, wins_b, succucessful_series, s_ful_wins_a, s_ful_wins_b, s_pts_wins_a, s_pts_wins_b, failed_series, f_ful_wins_a, f_ful_wins_b, f_pts_wins_a, f_pts_wins_b, no_wins_ab):
        """初期化

        p はインデックス。
        turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じ

        """
        self._p = p

        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate

        self._span = span
        self._tail_step = t_step
        self._head_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._expected_a_win_rate = expected_a_win_rate
        self._expected_no_win_match_rate= expected_no_win_match_rate
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
    def p(self):
        """［コインを投げて表が出る確率］
        インデックスです"""
        return self._p


    @property
    def turn_system_name(self):
        """［先後の決め方］
        ファイル名で示されているものと同じ"""
        return self._turn_system_name


    @property
    def failure_rate(self):
        """［コインを投げて表も裏も出ない確率］
        ファイル名で示されているものと同じ"""
        return self._failure_rate


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
    def expected_a_win_rate(self):
        return self._expected_a_win_rate


    @property
    def expected_no_win_match_rate(self):
        return self._expected_no_win_match_rate


    @property
    def trial_series(self):
        """［シリーズ試行回数］
        ファイル名で示されているものと同じ"""
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
        # p はインデックス
        # turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じ
        'turn_system_name':'object',    # string型は無い？
        'failure_rate':'float64',

        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'expected_a_win_rate':'float64',
        'expected_no_win_match_rate':'float64',
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
        kds_df = pd.DataFrame(
                columns=[
                    # 'p' は後でインデックスに変換
                    'p',

                    'turn_system_name',
                    'failure_rate',
                    'span',
                    't_step',
                    'h_step',
                    'shortest_coins',
                    'upper_limit_coins',
                    'expected_a_win_rate',
                    'expected_no_win_match_rate',
                    'trial_series',
                    'series_shortest_coins',
                    'series_longest_coins',
                    'wins_a',
                    'wins_b',
                    'succucessful_series',
                    's_ful_wins_a',
                    's_ful_wins_b',
                    's_pts_wins_a',
                    's_pts_wins_b',
                    'failed_series',
                    'f_ful_wins_a',
                    'f_ful_wins_b',
                    'f_pts_wins_a',
                    'f_pts_wins_b',
                    'no_wins_ab'])
        clazz.setup_data_frame(df=kds_df, shall_set_index=True)

        # turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じ

        return KakukinDataSheetTable(
                df=kds_df,
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)


    @classmethod
    def from_csv(clazz, trial_series, turn_system_id, failure_rate, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［手番が回ってくる制度］
        failure_rate : float
            ［将棋の引分け率］
        
        Returns
        -------
        kds_table : KakukinDataSheetTable
            テーブル
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = KakukinDataSheetFilePaths.as_sheet_csv(
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)

        # ファイルが存在しなかった場合
        is_file_not_found = not os.path.isfile(csv_file_path)
        if is_file_not_found:
            if new_if_it_no_exists:
                kds_table = KakukinDataSheetTable.new_empty_table(
                        trial_series=trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate)
            else:
                kds_table = None
        else:
            renaming_backup = RenamingBackup(file_path=csv_file_path)
            renaming_backup.rollback_if_file_crushed()
            kds_df = pd.read_csv(
                    csv_file_path,
                    encoding="utf8",
                    index_col='p',
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=kds_df, shall_set_index=False, csv_file_path=csv_file_path)
            kds_table = KakukinDataSheetTable(
                    df=kds_df,
                    trial_series=trial_series,
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate)


        return kds_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


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
    def setup_data_frame(clazz, df, shall_set_index, csv_file_path=None):
        """データフレームの設定"""

        if shall_set_index:
            try:
                # p はインデックス
                # turn_system_name, failure_rate と trial_series はファイル名と同じはず
                df.set_index(
                        'p',
                        inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します

            # FIXME データフレームがエンプティのときエラーになる？ 列もないとき ---> ファイルが破損している
            # FIXME KeyError: "None of ['p'] are in the columns"
            except KeyError as e:
                print(f"""\
{e}
{csv_file_path=}
df:
{df}
""")
                raise

        # データ型の設定
        # FIXME KeyError: "Only a column name can be used for the key in a dtype mappings argument. 'p' not found in columns."
        df.astype(clazz._dtype)


    def assert_welcome_record(self, welcome_record):
        specified_turn_system_name = Converter.turn_system_id_to_name(self._turn_system_id)
        if welcome_record.turn_system_name != specified_turn_system_name:
            raise ValueError(f"ファイル名と turn_system_name 列で内容が異なるのはおかしいです {welcome_record.turn_system_name=}  {specified_turn_system_name=}")

        if welcome_record.failure_rate != self._failure_rate:
            raise ValueError(f"ファイル名と failure_rate 列で内容が異なるのはおかしいです {welcome_record.failure_rate=}  {self._failure_rate=}")

        if welcome_record.trial_series != self._trial_series:
            raise ValueError(f"ファイル名と trial_series 列で内容が異なるのはおかしいです {welcome_record.trial_series=}  {self._trial_series=}")


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
        is_new_index = index not in self._df.index

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # p はインデックスだから省略
            # turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じはずだから省略
            shall_record_change =\
                self._df['span'][index] != welcome_record.span or\
                self._df['t_step'][index] != welcome_record.t_step or\
                self._df['h_step'][index] != welcome_record.h_step or\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['expected_a_win_rate'][index] != welcome_record.expected_a_win_rate or\
                self._df['expected_no_win_match_rate'][index] != welcome_record.expected_no_win_match_rate or\
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
                # turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じ
                'turn_system_name': welcome_record.turn_system_name,
                'failure_rate': welcome_record.failure_rate,
                'span': welcome_record.span,
                't_step': welcome_record.t_step,
                'h_step': welcome_record.h_step,
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'expected_a_win_rate': welcome_record.expected_a_win_rate,
                'expected_no_win_match_rate': welcome_record.expected_no_win_match_rate,
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

        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(
                csv_file_path,
                # p はインデックス
                columns=['turn_system_name', 'failure_rate', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'expected_a_win_rate', 'expected_no_win_match_rate', 'trial_series', 'series_shortest_coins', 'series_longest_coins', 'wins_a', 'wins_b', 'succucessful_series', 's_ful_wins_a', 's_ful_wins_b', 's_pts_wins_a', 's_pts_wins_b', 'failed_series', 'f_ful_wins_a', 'f_ful_wins_b', 'f_pts_wins_a', 'f_pts_wins_b', 'no_wins_ab'])
        renaming_backup.remove_backup()

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(      turn_system_name  ,     failure_rate  ,     span  ,     t_step  ,     h_step  ,     shortest_coins  ,     upper_limit_coins  ,     expected_a_win_rate  ,     expected_no_win_match_rate  ,     trial_series  ,     series_shortest_coins  ,     series_longest_coins  ,     wins_a  ,     wins_b  ,     succucessful_series  ,     s_ful_wins_a  ,     s_ful_wins_b  ,     s_pts_wins_a  ,     s_pts_wins_b  ,     failed_series  ,     f_ful_wins_a  ,     f_ful_wins_b  ,     f_pts_wins_a  ,     f_pts_wins_b  ,     no_wins_ab) in\
            enumerate(zip(df['turn_system_name'], df['failure_rate'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['expected_a_win_rate'], df['expected_no_win_match_rate'], df['trial_series'], df['series_shortest_coins'], df['series_longest_coins'], df['wins_a'], df['wins_b'], df['succucessful_series'], df['s_ful_wins_a'], df['s_ful_wins_b'], df['s_pts_wins_a'], df['s_pts_wins_b'], df['failed_series'], df['f_ful_wins_a'], df['f_ful_wins_b'], df['f_pts_wins_a'], df['f_pts_wins_b'], df['no_wins_ab'])):

            # p はインデックス
            p = df.index[row_number]
            # turn_system_name, failure_rate と trial_series はファイル名で示されているものと同じ

            # レコード作成
            record = KakukinDataSheetRecord(
                    p=p,

                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,

                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    expected_a_win_rate=expected_a_win_rate,
                    expected_no_win_match_rate=expected_no_win_match_rate,
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

            on_each(row_number, record)


###########
# MARK: TPB
###########

class TheoreticalProbabilityBestRecord():
    """理論的確率ベスト・レコード"""


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, expected_a_win_rate, expected_no_win_match_rate):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._expected_a_win_rate = expected_a_win_rate
        self._expected_no_win_match_rate = expected_no_win_match_rate


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
    def expected_a_win_rate(self):
        return self._expected_a_win_rate


    @property
    def expected_no_win_match_rate(self):
        return self._expected_no_win_match_rate


class TheoreticalProbabilityBestTable():
    """理論的確率ベスト・テーブル"""


    _dtype = {
        # turn_system_name, failure_rate, p はインデックス
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'expected_a_win_rate':'float64',
        'expected_no_win_match_rate':'float64'}


    def __init__(self, df):
        self._df = df


    @classmethod
    def setup_data_frame(clazz, shall_set_index, df):
        """データフレームの設定"""

        if shall_set_index:
            df.set_index(
                    ['turn_system_name', 'failure_rate', 'p'],
                    inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します

        # データ型の設定
        df.astype(clazz._dtype)


    @classmethod
    def new_empty_table(clazz):
        tpb_df = pd.DataFrame(
                columns=[
                    # 'turn_system_name', 'failure_rate', 'p' は後でインデックスに変換
                    'turn_system_name',
                    'failure_rate',
                    'p',

                    'span',
                    't_step',
                    'h_step',
                    'shortest_coins',
                    'upper_limit_coins',
                    'expected_a_win_rate',
                    'expected_no_win_match_rate'])
        clazz.setup_data_frame(df=tpd_df, shall_set_index=True)

        return TheoreticalProbabilityBestTable(df=tpb_df)


    @classmethod
    def from_csv(clazz, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？

        Returns
        -------
        tpb_table : TheoreticalProbabilityBestTable
            テーブル
        table_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = TheoreticalProbabilityBestFilePaths.as_csv()

        is_file_not_found = not os.path.isfile(csv_file_path)
        # ファイルが存在しなかった場合
        if is_file_not_found:
            if new_if_it_no_exists:
                tpb_table = TheoreticalProbabilityBestTable.new_empty_table()
            else:
                tpb_table = None

        # ファイルが存在した場合
        else:
            renaming_backup = RenamingBackup(file_path=csv_file_path)
            renaming_backup.rollback_if_file_crushed()
            tpb_df = pd.read_csv(
                    csv_file_path,
                    encoding="utf8",
                    index_col=['turn_system_name', 'failure_rate', 'p'],
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=tpb_df, shall_set_index=False)
            tpb_table = TheoreticalProbabilityBestTable(df=tpb_df)


        return tpb_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


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
                expected_a_win_rate=None,
                expected_no_win_match_rate=None)


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
        is_new_index = index not in self._df.index


        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # turn_system_name, failure_rate, p はインデックス
            shall_record_change =\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['expected_a_win_rate'][index] != welcome_record.expected_a_win_rate or\
                self._df['expected_no_win_match_rate'][index] != welcome_record.expected_no_win_match_rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # turn_system_name, failure_rate, p はインデックス
                'span': welcome_record.span,
                't_step': welcome_record.t_step,
                'h_step': welcome_record.h_step,
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'expected_a_win_rate': welcome_record.expected_a_win_rate,
                'expected_no_win_match_rate': welcome_record.expected_no_win_match_rate}

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

        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(csv_file_path,
                # turn_system_name, failure_rate, p はインデックス
                columns=['span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'expected_a_win_rate', 'expected_no_win_match_rate'])
        renaming_backup.remove_backup()

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            関数
        """

        df = self._df

        for row_number,(      span,       t_step,       h_step,       shortest_coins,       upper_limit_coins,       expected_a_win_rate,       expected_no_win_match_rate) in\
            enumerate(zip(df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['expected_a_win_rate'], df['expected_no_win_match_rate'])):

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
                    expected_a_win_rate=expected_a_win_rate,
                    expected_no_win_match_rate=expected_no_win_match_rate)

            on_each(row_number, record)


#############
# MARK: TPTPR
#############


class TpTprRecord():


    def __init__(self, span, t_step, h_step, shortest_coins, upper_limit_coins, expected_a_win_rate, expected_no_win_match_rate):
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._expected_a_win_rate = expected_a_win_rate
        self._expected_no_win_match_rate = expected_no_win_match_rate


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
    def expected_a_win_rate(self):
        return self._expected_a_win_rate


    @property
    def expected_no_win_match_rate(self):
        return self._expected_no_win_match_rate


###########
# MARK: TPR
###########

class TheoreticalProbabilityRatesRecord():


    def __init__(self, span, t_step, h_step, expected_a_win_rate, expected_no_win_match_rate):
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._expected_a_win_rate = expected_a_win_rate
        self._expected_no_win_match_rate = expected_no_win_match_rate


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
    def expected_a_win_rate(self):
        return self._expected_a_win_rate


    @property
    def expected_no_win_match_rate(self):
        return self._expected_no_win_match_rate


class TheoreticalProbabilityRatesTable():
    """理論的確率の率データ"""


    _dtype = {
        # span, t_step, h_step はインデックス
        'expected_a_win_rate':'float64',
        'expected_no_win_match_rate':'float64'}


    def __init__(self, df, spec):
        self._df = df
        self._spec = spec


    @classmethod
    def new_empty_table(clazz, spec):
        tpr_df = pd.DataFrame(
                columns=[
                    # 'span', 't_step', 'h_step' は後でインデックスに変換
                    'span',
                    't_step',
                    'h_step',

                    'expected_a_win_rate',
                    'expected_no_win_match_rate'])
        clazz.setup_data_frame(df=tpr_df, shall_set_index=True)

        # tpr_df.empty は真

        return TheoreticalProbabilityRatesTable(df=tpr_df, spec=spec)


    @classmethod
    def from_csv(clazz, spec, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        tpr_table : TheoreticalProbabilityRatesTable
            テーブル、またはナン
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = TheoreticalProbabilityRatesFilePaths.as_csv(
                turn_system_id=spec.turn_system_id,
                failure_rate=spec.failure_rate,
                p=spec.p)

        is_file_not_found = not os.path.isfile(csv_file_path)

        # ファイルが既存だったら、そのファイルを読む
        if not is_file_not_found:
            while True: # retry

                # CSVファイルの読取り、データタイプの設定
                try:
                    renaming_backup = RenamingBackup(file_path=csv_file_path)
                    renaming_backup.rollback_if_file_crushed()
                    tpr_df = pd.read_csv(
                            csv_file_path,
                            encoding="utf8",
                            index_col=['span', 't_step', 'h_step'])

                    # NOTE TPR ファイルは、初期状態では０件なので、０件だからといってファイル破損とは認定できない

                # ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？ リトライしてみる
                except PermissionError as e:
                    IntervalForRetry.sleep(shall_print=True)
                    continue    # retry

                # テーブルに列が無かった？ ファイルは破損してない。ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？ リトライしてみる
                except pd.errors.EmptyDataError as e:
                    # pandas.errors.EmptyDataError: No columns to parse from file
                    print(f"""\
[{datetime.datetime.now}] ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？
{e}
{csv_file_path=}""")
                    IntervalForRetry.sleep(shall_print=True)
                    raise ValueError("ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？") from e
                
                # CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
                except ValueError as e:
                    # ValueError: Integer column has NA values in column 3
                    print(f"""\
[{datetime.datetime.now}] CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
{e}
{csv_file_path=}""")
                    raise ValueError("CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき") from e


                # テーブルに追加の設定
                #try:
                clazz.setup_data_frame(df=tpr_df, shall_set_index=False, csv_file_path=csv_file_path)

#                 # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
#                 # "None of ['span', 't_step', 'h_step'] are in the columns"
#                 # とりあえず、ファイル破損と判定する
#                 except KeyError as e:
#                     print(f"""\
# [{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(A)
# {type(e)=}
# {e}
# {csv_file_path=}""")

#                     return None, None, True     # crush


                # オブジェクト生成
                tpr_table = TheoreticalProbabilityRatesTable(df=tpr_df, spec=spec)
                break   # complete


        # ファイルが存在しなかった場合
        else:
            if new_if_it_no_exists:
                tpr_table = TheoreticalProbabilityRatesTable.new_empty_table(spec=spec)
            else:
                tpr_table = None


        return tpr_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


    @property
    def df(self):
        return self._df


    @classmethod
    def setup_data_frame(clazz, df, shall_set_index, csv_file_path=None):
        """データフレームの設定"""

        # df.empty が真になるケースもある

        if shall_set_index:
            try:
                # インデックスの設定
                #
                #   NOTE インデックスに指定した列は、（デフォルトでは）テーブルから削除（ドロップ）します
                #
                df.set_index(
                        ['span', 't_step', 'h_step'],
                        inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します
            # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
            # "None of ['span', 't_step', 'h_step'] are in the columns"
            # とりあえず、ファイル破損と判定する
            except KeyError as e:
                print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(B)
{type(e)=}
{e}
{csv_file_path=}
df:
{df}""")
                raise


        try:
            # データ型の設定
            #
            #   NOTE clazz._dtype には、インデックスを除いた列の設定が含まれているものとします
            #
            df.astype(clazz._dtype)

        # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
        # "None of ['span', 't_step', 'h_step'] are in the columns"
        # とりあえず、ファイル破損と判定する
        except KeyError as e:
            print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(C)
{type(e)=}
{e}
{csv_file_path=}""")
            raise


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
        is_new_index = index not in self._df.index

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # span, t_step, h_step はインデックス
            shall_record_change =\
                self._df['expected_a_win_rate'][index] != welcome_record.expected_a_win_rate or\
                self._df['expected_no_win_match_rate'][index] != welcome_record.expected_no_win_match_rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # span, t_step, h_step はインデックス
                'expected_a_win_rate': welcome_record.expected_a_win_rate,
                'expected_no_win_match_rate': welcome_record.expected_no_win_match_rate}

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

        csv_file_path = TheoreticalProbabilityRatesFilePaths.as_csv(
                p=self._spec.p,
                failure_rate=self._spec.failure_rate,
                turn_system_id=self._spec.turn_system_id)

        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(
                csv_file_path,
                # span, t_step, h_step はインデックス
                columns=['expected_a_win_rate', 'expected_no_win_match_rate'])
        renaming_backup.remove_backup()

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(      expected_a_win_rate  ,     expected_no_win_match_rate) in\
            enumerate(zip(df['expected_a_win_rate'], df['expected_no_win_match_rate'])):

            # span, t_step, h_step はインデックス
            span, t_step, h_step = df.index[row_number]

            # レコード作成
            tpr_record = TheoreticalProbabilityRatesRecord(
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    expected_a_win_rate=expected_a_win_rate,
                    expected_no_win_match_rate=expected_no_win_match_rate)

            on_each(row_number, tpr_record)


##########
# MARK: TP
##########

class TheoreticalProbabilityRecord():


    def __init__(self, span, t_step, h_step, shortest_coins, upper_limit_coins):
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


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


class TheoreticalProbabilityTable():
    """理論的確率データ"""


    _dtype = {
        # span, t_step, h_step はインデックス
        'shortest_coins':'int64',
        'upper_limit_coins':'int64'}


    def __init__(self, df, spec):
        self._df = df
        self._spec = spec


    @classmethod
    def new_empty_table(clazz, spec):
        tp_df = pd.DataFrame(
                columns=[
                    # 'span', 't_step', 'h_step' は後でインデックスに変換
                    'span',
                    't_step',
                    'h_step',

                    'shortest_coins',
                    'upper_limit_coins'])
        clazz.setup_data_frame(df=tp_df, shall_set_index=True)

        # tp_df.empty は真

        return TheoreticalProbabilityTable(df=tp_df, spec=spec)


    @classmethod
    def from_csv(clazz, spec, new_if_it_no_exists=False):
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
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = TheoreticalProbabilityFilePaths.as_csv(
                turn_system_id=spec.turn_system_id,
                failure_rate=spec.failure_rate,
                p=spec.p)

        is_file_not_found = not os.path.isfile(csv_file_path)

        # ファイルが既存だったら、そのファイルを読む
        if not is_file_not_found:
            while True: # retry

                # CSVファイルの読取り、データタイプの設定
                try:
                    renaming_backup = RenamingBackup(file_path=csv_file_path)
                    renaming_backup.rollback_if_file_crushed()
                    df = pd.read_csv(
                            csv_file_path,
                            encoding="utf8",
                            index_col=['span', 't_step', 'h_step'])

                    # 診断
                    # FIXME テキストファイルの中身が表示されないバイトで埋まっていることがある。
                    if df.empty:
                        print(f"バイナリ・ファイルを読み取ったかもしれない。ファイル破損として扱う {csv_file_path=}")
                        raise ValueError(f"バイナリ・ファイルを読み取ったかもしれない。ファイル破損として扱う {csv_file_path=}")


                # ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？ リトライしてみる
                except PermissionError as e:
                    IntervalForRetry.sleep(shall_print=True)
                    continue    # retry

                # テーブルに列が無かった？ ファイルは破損してない。ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？
                except pd.errors.EmptyDataError as e:
                    # pandas.errors.EmptyDataError: No columns to parse from file
                    print(f"""\
[{datetime.datetime.now}] ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？
{e}
{csv_file_path=}""")
                    raise ValueError("ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？") from e
                
                # CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
                except ValueError as e:
                    # ValueError: Integer column has NA values in column 3
                    print(f"""\
[{datetime.datetime.now}] CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
{e}
{csv_file_path=}""")
                    raise ValueError("CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき") from e
                
                except TypeError as e:
                    print(f"""\
[{datetime.datetime.now}] 想定外の型エラー。ファイルが破損してるかも？
{e}
{csv_file_path=}
""")
                    raise ValueError("想定外の型エラー。ファイルが破損してるかも？") from e


                # テーブルに追加の設定
                #try:
                clazz.setup_data_frame(df=df, shall_set_index=False, csv_file_path=csv_file_path)

#                 # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
#                 # "None of ['span', 't_step', 'h_step'] are in the columns"
#                 # とりあえず、ファイル破損と判定する
#                 except KeyError as e:
#                     print(f"""\
# [{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(A)
# {type(e)=}
# {e}
# {csv_file_path=}""")

#                     return None, None, True     # crush


                # オブジェクト生成
                tp_table = TheoreticalProbabilityTable(df=df, spec=spec)
                break   # complete


        # ファイルが存在しなかった場合
        else:
            if new_if_it_no_exists:
                tp_table = TheoreticalProbabilityTable.new_empty_table(spec=spec)
            else:
                tp_table = None


        return tp_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


    @property
    def df(self):
        return self._df


    @classmethod
    def setup_data_frame(clazz, df, shall_set_index, csv_file_path=None):
        """データフレームの設定"""

        # df.empty が真になるケースもある

        if shall_set_index:
            try:
                # インデックスの設定
                #
                #   NOTE インデックスに指定した列は、（デフォルトでは）テーブルから削除（ドロップ）します
                #
                df.set_index(
                        ['span', 't_step', 'h_step'],
                        inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します
            # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
            # "None of ['span', 't_step', 'h_step'] are in the columns"
            # とりあえず、ファイル破損と判定する
            except KeyError as e:
                print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(B)
{type(e)=}
{e}
{csv_file_path=}
df:
{df}""")
                raise


        try:
            # データ型の設定
            #
            #   NOTE clazz._dtype には、インデックスを除いた列の設定が含まれているものとします
            #
            df.astype(clazz._dtype)

        # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
        # "None of ['span', 't_step', 'h_step'] are in the columns"
        # とりあえず、ファイル破損と判定する
        except KeyError as e:
            print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(C)
{type(e)=}
{e}
{csv_file_path=}""")
            raise


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : TheoreticalProbabilityRecord
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
        is_new_index = index not in self._df.index

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # span, t_step, h_step はインデックス
            shall_record_change =\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # span, t_step, h_step はインデックス
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins}

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

        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(
                csv_file_path,
                # span, t_step, h_step はインデックス
                columns=['shortest_coins', 'upper_limit_coins'])
        renaming_backup.remove_backup()

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(      shortest_coins  ,     upper_limit_coins) in\
            enumerate(zip(df['shortest_coins'], df['upper_limit_coins'])):

            # span, t_step, h_step はインデックス
            span, t_step, h_step = df.index[row_number]

            # レコード作成
            record = TheoreticalProbabilityRecord(
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins)

            on_each(row_number, record)


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

        ep_df = pd.DataFrame(
                columns=[
                    # 'p' は後でインデックスに変換
                    'p',

                    'best_p',
                    'best_p_error',
                    'best_span',
                    'best_t_step',
                    'best_h_step',
                    'latest_p',
                    'latest_p_error',
                    'latest_span',
                    'latest_t_step',
                    'latest_h_step',
                    'candidate_history_text'])
        clazz.setup_data_frame(df=ep_df, shall_set_index=True)

        return EmpiricalProbabilityDuringTrialsTable(
                df=ep_df,
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)


    @classmethod
    def from_csv(clazz, trial_series, turn_system_id, failure_rate, new_if_it_no_exists):
        """ファイル読込

        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［手番が回ってくる制度］
        failure_rate : float
            ［将棋の引分け率］

        Returns
        -------
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = EmpiricalProbabilityDuringTrialsFilePaths.as_csv(
                trial_series=trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate)

        # ファイルが存在しなかった場合
        is_file_not_found = not os.path.isfile(csv_file_path)

        if is_file_not_found:
            if new_if_it_no_exists:
                ep_table = EmpiricalProbabilityDuringTrialsTable.new_empty_table(
                        trial_series=trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate)
            else:
                ep_table = None
        else:
            renaming_backup = RenamingBackup(file_path=csv_file_path)
            renaming_backup.rollback_if_file_crushed()
            df = pd.read_csv(
                    csv_file_path,
                    encoding="utf8",
                    index_col='p',
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=df, shall_set_index=False)
            ep_table = EmpiricalProbabilityDuringTrialsTable(
                    df,
                    trial_series=trial_series,
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate)


        return ep_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


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
    def setup_data_frame(clazz, df, shall_set_index):
        """データフレームの設定"""

        if shall_set_index:
            df.set_index(
                    'p',
                    inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します

        # データ型の設定
        df.astype(clazz._dtype)


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
        is_new_index = index not in self._df.index

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
        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(
                csv_file_path,
                # ［シリーズ・ルール候補］列は長くなるので末尾に置きたい
                # 'p' はインデックス
                columns=['best_p', 'best_p_error', 'best_span', 'best_t_step', 'best_h_step', 'latest_p', 'latest_p_error', 'latest_span', 'latest_t_step', 'latest_h_step', 'candidate_history_text'])
        renaming_backup.remove_backup()

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

            on_each(row_number, record)


###########
# MARK: CPT
###########

class CalculateProbabilityTable():


    @staticmethod
    def from_csv():
        """ファイル読込

        Returns
        -------
        df : DataFrame
            データフレーム
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = CSV_FILE_PATH_CAL_P

        # ファイルが存在しなかった場合
        is_file_not_found = not os.path.isfile(csv_file_path)

        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.rollback_if_file_crushed()
        cp_df = pd.read_csv(csv_file_path, encoding="utf8",
                dtype={
                    'p':'float64',
                    'h_time':'int64',
                    't_time':'int64',
                    'best_p':'float64',
                    'best_p_error':'float64',
                    'comment':'object'
                })

        return cp_df, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


##########
# MARK: GT
##########
class GameTreeNode():

    def __init__(self, face, winner, pts, rate):
        """初期化
        
        Parameters
        ----------
        face : str
            'h', 't', 'f' のいずれか。それぞれ head（コインの表）, tail（コインの裏）, failed（失敗）
        winner : str
            'A', 'B', 'N' のいずれか。それぞれ Ａさん, Ｂさん, 勝者なし（No win match）
        pts : int
            winner の累計の勝ち点
        rate : float
            そのノードの実現確率
        """
        self._face = face
        self._winner = winner
        self._pts = pts
        self._rate = rate


    @property
    def face(self):
        return self._face


    @property
    def winner(self):
        return self._winner


    @property
    def pts(self):
        return self._pts


    @property
    def rate(self):
        return self._rate


class GameTreeRecord():


    def __init__(self, no, result,
        node1,
        node2,
        node3,
        node4,
        node5,
        node6):
        """TODO n6 以降も欲しいが、あとで考える
        
        Parameters
        ----------
        no : int
            1から始まる連番
        result : str
            結果
        node1 : GameTreeNode
            ノード１
        """
        self._no = no
        self._result = result

        self._node1 = node1
        self._node2 = node2
        self._node3 = node3
        self._node4 = node4
        self._node5 = node5
        self._node6 = node6


    @property
    def no(self):
        return self._no


    @property
    def result(self):
        return self._result


    @property
    def node1(self):
        return self._node1


    @property
    def node2(self):
        return self._node2


    @property
    def node3(self):
        return self._node3



    @property
    def node4(self):
        return self._node4



    @property
    def node5(self):
        return self._node5



    @property
    def node6(self):
        return self._node6


class GameTreeTable():
    """樹形図データのテーブル"""


    _dtype = {
        # no はインデックス
        'result':'object',

        'face1':'object',
        'winner1':'object',
        'pts1':'Int64',         # NOTE NaN が含まれる場合は、int64 ではなく Int64 を使う。先頭が大文字
        'rate1':'float64',

        'face2':'object',
        'winner2':'object',
        'pts2':'Int64',
        'rate2':'float64',

        'face3':'object',
        'winner3':'object',
        'pts3':'Int64',
        'rate3':'float64',

        'face4':'object',
        'winner4':'object',
        'pts4':'Int64',
        'rate4':'float64',

        'face5':'object',
        'winner5':'object',
        'pts5':'Int64',
        'rate5':'float64',
        
        'face6':'object',
        'winner6':'object',
        'pts6':'Int64',
        'rate6':'float64'}


    def __init__(self, df, spec, span, t_step, h_step):
        self._df = df
        self._spec = spec
        self._span = span
        self._t_step = t_step
        self._h_step = h_step


    @classmethod
    def new_empty_table(clazz, spec, span, t_step, h_step):
        gt_df = pd.DataFrame(
                columns=[
                    # 'no' は後でインデックスに変換
                    'no',

                    'result',

                    'face1',
                    'winner1',
                    'pts1',
                    'rate1',

                    'face2',
                    'winner2',
                    'pts2',
                    'rate2',

                    'face3',
                    'winner3',
                    'pts3',
                    'rate3',

                    'face4',
                    'winner4',
                    'pts4',
                    'rate4',

                    'face5',
                    'winner5',
                    'pts5',
                    'rate5',

                    'face6',
                    'winner6',
                    'pts6',
                    'rate6'])
        clazz.setup_data_frame(df=gt_df, shall_set_index=True)
        return GameTreeTable(df=gt_df, spec=spec, span=span, t_step=t_step, h_step=h_step)


    @classmethod
    def from_csv(clazz, spec, span, t_step, h_step, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        gt_table : GameTreeTable
            テーブル、またはナン
        file_read_result : FileReadResult
            ファイル読込結果
        """

        csv_file_path = GameTreeFilePaths.as_csv(spec=spec, span=span, t_step=t_step, h_step=h_step)

        is_file_not_found = not os.path.isfile(csv_file_path)

        # ファイルが既存だったら、そのファイルを読む
        if not is_file_not_found:
            while True: # retry

                # CSVファイルの読取り、データタイプの設定
                try:
                    renaming_backup = RenamingBackup(file_path=csv_file_path)
                    renaming_backup.rollback_if_file_crushed()
                    df = pd.read_csv(
                            csv_file_path,
                            encoding="utf8",
                            index_col=['no'])

                    # 診断
                    # FIXME テキストファイルの中身が表示されないバイトで埋まっていることがある。
                    if df.empty:
                        print(f"バイナリ・ファイルを読み取ったかもしれない。ファイル破損として扱う {csv_file_path=}")
                        raise ValueError(f"バイナリ・ファイルを読み取ったかもしれない。ファイル破損として扱う {csv_file_path=}")


                # ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？ リトライしてみる
                except PermissionError as e:
                    IntervalForRetry.sleep(shall_print=True)
                    continue    # retry

                # テーブルに列が無かった？ ファイルは破損してない。ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？
                except pd.errors.EmptyDataError as e:
                    # pandas.errors.EmptyDataError: No columns to parse from file
                    print(f"""\
[{datetime.datetime.now}] ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？
{e}
{csv_file_path=}""")
                    raise ValueError("ファイルの読取タイミングが、他のプログラムからのファイルのアクセス中と被ったか？") from e
                
                # CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
                except ValueError as e:
                    # ValueError: Integer column has NA values in column 3
                    print(f"""\
[{datetime.datetime.now}] CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき
{e}
{csv_file_path=}""")
                    raise ValueError("CSVファイルに異常データが入ってる、レコードに一部の値だけが入っているような、値が欠損しているとき") from e
                
                except TypeError as e:
                    print(f"""\
[{datetime.datetime.now}] 想定外の型エラー。ファイルが破損してるかも？
{e}
{csv_file_path=}
""")
                    raise ValueError("想定外の型エラー。ファイルが破損してるかも？") from e


                # テーブルに追加の設定
                #try:
                clazz.setup_data_frame(df=df, shall_set_index=False, csv_file_path=csv_file_path)

                # オブジェクト生成
                gt_table = GameTreeTable(df=df, spec=spec, span=span, t_step=t_step, h_step=h_step)
                break   # complete


        # ファイルが存在しなかった場合
        else:
            if new_if_it_no_exists:
                gt_table = GameTreeTable.new_empty_table(spec=spec, span=span, t_step=t_step, h_step=h_step)
            else:
                gt_table = None


        return gt_table, FileReadResult(file_path=csv_file_path, is_file_not_found=is_file_not_found)


    @property
    def df(self):
        return self._df


    @classmethod
    def setup_data_frame(clazz, df, shall_set_index, csv_file_path=None):
        """データフレームの設定"""

        # df.empty が真になるケースもある

        if shall_set_index:
            try:
                # インデックスの設定
                df.set_index('no',
                        inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します

            # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
            # "None of ['span', 't_step', 'h_step'] are in the columns"
            # とりあえず、ファイル破損と判定する
            except KeyError as e:
                print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(B)
{type(e)=}
{e}
{csv_file_path=}
df:
{df}""")
                raise


        try:
            # データ型の設定
            df.astype(clazz._dtype)

        # FIXME 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う
        # "None of ['span', 't_step', 'h_step'] are in the columns"
        # とりあえず、ファイル破損と判定する
        except KeyError as e:
            print(f"""\
[{datetime.datetime.now}] 開いても読めない、容量はある、VSCodeで開けない .csv ファイルができていることがある。破損したファイルだと思う(C)
{type(e)=}
{e}
{csv_file_path=}""")
            raise


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : GameTreeRecord
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
        index = welcome_record.no

        # データ変更判定
        # -------------
        is_new_index = index not in self._df.index

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            # no はインデックス
            shall_record_change =\
                self._df['result'][index] != welcome_record.result or\
                \
                self._df['face1'][index] != welcome_record.node1.face or\
                self._df['winner1'][index] != welcome_record.node1.winner or\
                self._df['pts1'][index] != welcome_record.node1.pts or\
                self._df['rate1'][index] != welcome_record.node1.rate or\
                \
                self._df['face2'][index] != welcome_record.node2.face or\
                self._df['winner2'][index] != welcome_record.node2.winner or\
                self._df['pts2'][index] != welcome_record.node2.pts or\
                self._df['rate2'][index] != welcome_record.node2.rate or\
                \
                self._df['face3'][index] != welcome_record.node3.face or\
                self._df['winner3'][index] != welcome_record.node3.winner or\
                self._df['pts3'][index] != welcome_record.node3.pts or\
                self._df['rate3'][index] != welcome_record.node3.rate or\
                \
                self._df['face4'][index] != welcome_record.node4.face or\
                self._df['winner4'][index] != welcome_record.node4.winner or\
                self._df['pts4'][index] != welcome_record.node4.pts or\
                self._df['rate4'][index] != welcome_record.node4.rate or\
                \
                self._df['face5'][index] != welcome_record.node5.face or\
                self._df['winner5'][index] != welcome_record.node5.winner or\
                self._df['pts5'][index] != welcome_record.node5.pts or\
                self._df['rate5'][index] != welcome_record.node5.rate or\
                \
                self._df['face6'][index] != welcome_record.node6.face or\
                self._df['winner6'][index] != welcome_record.node6.winner or\
                self._df['pts6'][index] != welcome_record.node6.pts or\
                self._df['rate6'][index] != welcome_record.node6.rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                # no はインデックス
                'result': welcome_record.result,

                'face1': welcome_record.node1.face,
                'winner1': welcome_record.node1.winner,
                'pts1': welcome_record.node1.pts,
                'rate1': welcome_record.node1.rate,

                'face2': welcome_record.node2.face,
                'winner2': welcome_record.node2.winner,
                'pts2': welcome_record.node2.pts,
                'rate2': welcome_record.node2.rate,

                'face3': welcome_record.node3.face,
                'winner3': welcome_record.node3.winner,
                'pts3': welcome_record.node3.pts,
                'rate3': welcome_record.node3.rate,

                'face4': welcome_record.node4.face,
                'winner4': welcome_record.node4.winner,
                'pts4': welcome_record.node4.pts,
                'rate4': welcome_record.node4.rate,

                'face5': welcome_record.node5.face,
                'winner5': welcome_record.node5.winner,
                'pts5': welcome_record.node5.pts,
                'rate5': welcome_record.node5.rate,

                'face6': welcome_record.node6.face,
                'winner6': welcome_record.node6.winner,
                'pts6': welcome_record.node6.pts,
                'rate6': welcome_record.node6.rate}

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

        csv_file_path = GameTreeFilePaths.as_csv(
                spec=self._spec,
                span=self._span,
                t_step=self._t_step,
                h_step=self._h_step)

        # TODO ファイル保存の前のリネーム・バックアップ
        renaming_backup = RenamingBackup(file_path=csv_file_path)
        renaming_backup.make_backup()
        self._df.to_csv(
                csv_file_path,
                # no はインデックス
                columns=[
                    'result',
                    'face1', 'winner1', 'pts1', 'rate1',
                    'face2', 'winner2', 'pts2', 'rate2',
                    'face3', 'winner3', 'pts3', 'rate3',
                    'face4', 'winner4', 'pts4', 'rate4',
                    'face5', 'winner5', 'pts5', 'rate5',
                    'face6', 'winner6', 'pts6', 'rate6'])
        renaming_backup.remove_backup()

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for row_number,(
                result,
                face1, winner1, pts1, rate1,
                face2, winner2, pts2, rate2,
                face3, winner3, pts3, rate3,
                face4, winner4, pts4, rate4,
                face5, winner5, pts5, rate5,
                face6, winner6, pts6, rate6) in\
                enumerate(zip(
                    df['result'],
                    df['face1'], df['winner1'], df['pts1'], df['rate1'],
                    df['face2'], df['winner2'], df['pts2'], df['rate2'],
                    df['face3'], df['winner3'], df['pts3'], df['rate3'],
                    df['face4'], df['winner4'], df['pts4'], df['rate4'],
                    df['face5'], df['winner5'], df['pts5'], df['rate5'],
                    df['face6'], df['winner6'], df['pts6'], df['rate6'])):

            # no はインデックス
            no = df.index[row_number]

            # レコード作成
            record = GameTreeRecord(
                    no=no,
                    result=result,
                    node1=GameTreeNode(face=face1, winner=winner1, pts=pts1, rate=rate1),
                    node2=GameTreeNode(face=face2, winner=winner2, pts=pts2, rate=rate2),
                    node3=GameTreeNode(face=face3, winner=winner3, pts=pts3, rate=rate3),
                    node4=GameTreeNode(face=face4, winner=winner4, pts=pts4, rate=rate4),
                    node5=GameTreeNode(face=face5, winner=winner5, pts=pts5, rate=rate5),
                    node6=GameTreeNode(face=face6, winner=winner6, pts=pts6, rate=rate6))

            on_each(row_number, record)
