import traceback
import datetime
import time

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable


# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 30


class AutomationOne():


    def __init__(self, tpb_table):
        """初期化
        
        Parameters
        ----------
        df_best : DataFrame
            データフレーム
        """

        self._tpb_table = tpb_table

        self._spec = None
        self._best_record = None

        self._tp_table = None
        self._is_tp_update = False


    def _on_match_file(self, record_tp):
        """TP表の span, t_step, h_step をインデックスとする各行について"""

        try:
            shall_upsert_record = False

            # 絞り込み。 0～複数件の DataFrame型が返ってくる
            # とりえあず主キーは［先後の決め方］［コインを投げて表も裏も出ない確率］［コインを投げて表が出る確率］の３列
            tpb_result_set_by_index_df = self._tpb_table.get_result_set_by_index(
                    turn_system_name=Converter.turn_system_id_to_name(self._spec.turn_system_id),
                    failure_rate=self._spec.failure_rate,
                    p=self._spec.p)

            
            # 空テーブルを想定。
            #
            #   ただし、TP テーブルは先にインデックス列を埋めた仮表を作るから、テーブルが空ということはないはず
            #
            if 0 == len(tpb_result_set_by_index_df):
                shall_upsert_record = True

            # ［理論的確率データ］表にある span, t_step, h_step に一致する［理論的確率ベスト］表のレコードがあれば、それを取得
            else:
                index = tpb_result_set_by_index_df.index[0]  # インデックスを取得

                # ［理論的確率ベスト］表から、［理論的なＡさんの勝率］と、［理論的なコインを投げて表も裏も出ない確率］を抽出
                old_theoretical_a_win_rate = tpb_result_set_by_index_df.at[index, 'theoretical_a_win_rate']
                old_theoretical_no_win_match_rate = tpb_result_set_by_index_df.at[index, 'theoretical_no_win_match_rate']

                # 誤差が縮まれば更新
                welcome_theoretical_a_win_error = record_tp.theoretical_a_win_rate - EVEN
                if abs(welcome_theoretical_a_win_error) < abs(old_theoretical_a_win_rate - EVEN):
                    shall_upsert_record = True

                # 誤差が同じでも、引分け率が新しく判明したか、引き分け率が下がれば更新
                elif welcome_theoretical_a_win_error == abs(old_theoretical_a_win_rate - EVEN) and (old_theoretical_no_win_match_rate is None or record_tp.theoretical_no_win_match_rate < old_theoretical_no_win_match_rate):
                    shall_upsert_record = True


            if shall_upsert_record:
                # 型変換
                welcome_record = TheoreticalProbabilityBestRecord(
                        turn_system_name=record_tp.turn_system_name,
                        failure_rate=record_tp.failure_rate,
                        p=record_tp.p,
                        span=record_tp.span,
                        t_step=record_tp.t_step,
                        h_step=record_tp.h_step,
                        shortest_coins=record_tp.shortest_coins,
                        upper_limit_coins=record_tp.upper_limit_coins,
                        theoretical_a_win_rate=record_tp.theoretical_a_win_rate,
                        theoretical_no_win_match_rate=record_tp.theoretical_no_win_match_rate)

                # レコードの新規作成または更新
                is_dirty_temp = self._tpb_table.upsert_record(
                        df_result_set_by_index=tpb_result_set_by_index_df,
                        welcome_record=welcome_record)

                if is_dirty_temp:
                    self._is_tp_update = True


        except KeyError as ex:
            print(f"列名がないという例外が発生中")
            for index, column_name in enumerate(self._tpb_table.df.columns.values, 1):
                print(f"({index}) {column_name=}")
            raise # 再スロー


    def get_reocrd_of_best_tp_or_none(self):
        """［理論的確率データ］表から、イーブンに一番近い行を抽出します"""

        # ［Ａさんの勝率］と 0.5 との誤差の絶対値が最小のレコードのセット
        df_result_set = self._tp_table.df.loc[abs(self._tp_table.df['theoretical_a_win_rate'] - 0.5) == min(abs(self._tp_table.df['theoretical_a_win_rate'] - 0.5))]

        # それでも１件に絞り込めない場合、［コインを投げて表も裏も出ない確率］が最小のレコードのセット
        if 1 < len(df_result_set):
            df_result_set = self._tp_table.df.loc[self._tp_table.df['theoretical_no_win_match_rate'] == min(self._tp_table.df['theoretical_no_win_match_rate'])]

            # それでも１件に絞り込めない場合、［上限対局数］が最小のレコードのセット
            if 1 < len(df_result_set):
                df_result_set = self._tp_table.df.loc[self._tp_table.df['upper_limit_coins'] == min(self._tp_table.df['upper_limit_coins'])]


        # 該当レコードがあれば、適当に先頭の１件だけ返す。無ければナンを返す
        if 0 < len(df_result_set):
            return self._tp_table.df.iloc[0]

        return None


    def execute_a_spec(self, spec):
        """
        
        Returns
        -------
        is_dirty : bool
            ファイル変更の有無
        """

        if self._tpb_table is None:
            raise ValueError("self._tpb_table を先に設定しておかなければいけません")

        self._spec = spec
        self._is_tp_update = False

        turn_system_name = Converter.turn_system_id_to_name(self._spec.turn_system_id)

        # 読み込む［理論的確率データ］ファイルがなければ無視
        self._tp_table, is_new = TheoreticalProbabilityTable.read_csv(spec=self._spec, new_if_it_no_exists=False)

        if self._tp_table is None:
            print(f"[{datetime.datetime.now()}][turn_system={Converter.turn_system_id_to_name(self._spec.turn_system_id)}  failure_rate={self._spec.failure_rate * 100:.1f}%  p={self._spec.p * 100:.1f}%] スキップ。［理論的確率データ］ファイルがない。")
            return False

        if is_new:
            self._is_tp_update = True


        # ［理論的確率データ］ファイルの中から、ベストな１行を取得します
        #
        #   NOTE TPテーブルは行が膨大にあるので、for_each するのは良くない。集計を使って１回でベスト・レコードを取得すべき
        #
        record_in_best_tp_or_none = self.get_reocrd_of_best_tp_or_none()
        if record_in_best_tp_or_none is not None:
            self._on_match_file(record_tp=record_in_best_tp_or_none)


        return self._is_tp_update


class AutomationAll():


    def execute_all(self):

        # 書込み先の［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        tpb_table, is_new = TheoreticalProbabilityBestTable.read_csv(new_if_it_no_exists=True)

        if tpb_table is None:
            raise ValueError("ここで tpb_table がナンなのはおかしい")

        # ［理論的確率ベストデータ］新規作成または更新
        automation_one = AutomationOne(tpb_table=tpb_table)

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み
                specified_failure_rate = failure_rate_percent / 100

                # リセット
                number_of_dirty_rows = 0                # 変更された行数
                number_of_bright_rows = 0               # 変更されなかった行数
                start_time_for_save = time.time()       # CSV保存用タイマー

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    specified_p = p_percent / 100
                    #print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}  p={specified_p * 100:.1f}] ...")

                    # 仕様
                    spec = Specification(
                            p=specified_p,
                            failure_rate=specified_failure_rate,
                            turn_system_id=specified_turn_system_id)

                    is_dirty_temp = automation_one.execute_a_spec(spec=spec)

                    if is_dirty_temp:
                        number_of_dirty_rows += 1
                    
                    else:
                        number_of_bright_rows += 1
                    

                    if 0 < number_of_dirty_rows:
                        # 指定間隔（秒）でファイル保存
                        end_time_for_save = time.time()
                        if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                            csv_file_path_to_wrote = tpb_table.to_csv()
                            print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] {number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged. write theoretical probability best to `{csv_file_path_to_wrote}` file ...")

                            # リセット
                            start_time_for_save = time.time()
                            number_of_dirty_rows = 0
                            number_of_bright_rows = 0


                # 忘れずに flush
                if 0 < number_of_dirty_rows:
                    csv_file_path_to_wrote = tpb_table.to_csv()
                    # specified_p はまだ入ってるはず
                    print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] {number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged. write theoretical probability best to `{csv_file_path_to_wrote}` file ...")
