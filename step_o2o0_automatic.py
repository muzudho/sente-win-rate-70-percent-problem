#
# 分析
# python step_o2o0_automatic.py
#
#   ［理論的確率データ］を作成します。
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE, EVEN, Converter, Specification, is_almost_zero
from library.database import TheoreticalProbabilityTable
from config import DEFAULT_MAX_DEPTH
from scripts.step_o2o1o0_upsert_new_record_in_tp import Automation as StepO2o1o0UpsertNewRecordInTp


# タイムアップ間隔（秒）。タイムシェアリング間隔
INTERVAL_SECONDS_FOR_SAVE_CSV = 5


class AllTheoreticalProbabilityFilesOperation():


    def __init__(self, depth):

        # CSV保存用タイマー
        self._start_time_for_save = None

        # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._number_of_dirty = 0

        self._depth = depth


    @property
    def depth(self):
        return self._depth


    def stringify_log_stamp(self, spec):
        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        return f"""\
[{datetime.datetime.now()}][depth={self._depth}  turn_system_name={turn_system_name:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] \
"""


    def for_each_spec(self, on_each_spec):
        """
        Parameters
        ----------
        on_each_spec : func
            関数
        """

        # ［先後の決め方］
        for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_name(turn_system_id)

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    p = p_percent / 100

                    # 仕様
                    spec = Specification(
                            turn_system_id=turn_system_id,
                            failure_rate=failure_rate,
                            p=p)
                    
                    on_each_spec(spec=spec)


    def on_each_spec(self, spec):
        # ファイルが存在しなければ、新規作成する。あれば読み込む
        tp_table, is_tp_file_created = TheoreticalProbabilityTable.read_csv(spec=spec, new_if_it_no_exists=True)

        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)

        if is_tp_file_created:
            print(f"{self.stringify_log_stamp(spec=spec)}NEW_FILE")

            # １件も処理してないが、ファイルを保存したいのでフラグを立てる
            self._number_of_dirty += 1

        else:
            # ファイルが既存で、テーブルの中で、誤差がほぼ０の行が含まれているなら、探索打ち切り
            #
            #   FIXME このコードの書き方で動くのかわからない。もし書けないなら、１件ずつ調べていけばいいか
            #
            min_abs_error = (tp_table.df['theoretical_a_win_rate'] - EVEN).abs().min()
            if is_almost_zero(min_abs_error):
                print(f"{self.stringify_log_stamp(spec=spec)}READY_EVEN....")
                return


        #################################################
        # Step o2o1o0 ［理論的確率データ］に新規行を挿入する
        #################################################

        #
        # FIXME 飛び番で挿入されてる？
        #
        print(f"{self.stringify_log_stamp(spec=spec)}step o2o1o0 insert new record in tp...")
        step_o2o1o0_upsert_new_record_in_tp = StepO2o1o0UpsertNewRecordInTp()

        # まず、［理論的確率データ］ファイルに span, t_step, h_step のインデックスを持った仮行をある程度の数、追加していく。このとき、スリー・レーツ列は入れず、空けておく
        temp_number_of_dirty = step_o2o1o0_upsert_new_record_in_tp.execute(
                spec=spec,
                tp_table=tp_table,
                is_tp_file_created=is_tp_file_created,

                #
                # NOTE 内容をどれぐらい作るかは、 upper_limit_span （span の上限）を指定することにする。
                # 数字が増えると処理が重くなる。 10 ぐらいまですぐ作れるが、 20 を超えると数秒かかるようになる
                #
                upper_limit_span=self._depth)


        # ［理論的確率データ］（TP）ファイル保存
        if 0 < temp_number_of_dirty:
            self._number_of_dirty += temp_number_of_dirty
            csv_file_path_to_wrote = tp_table.to_csv()
            print(f"{self.stringify_log_stamp(spec=spec)}SAVE_FILE  {self._number_of_dirty=}  write file to `{csv_file_path_to_wrote}` ...")
            self._number_of_dirty = 0


        # TODO ［理論的確率データ］のうち、［理論的確率ベスト・データ］に載っているものについて、試行して、その結果を［理論的確率の試行結果データ］に保存したい


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # TODO 自動調整のいい方法が思い浮かばない
        # とりあえず、 depth が どんどん増えていくものとする。
        for depth in range(1, DEFAULT_MAX_DEPTH):

            all_theoretical_probability_files_operation = AllTheoreticalProbabilityFilesOperation(depth=depth)

            all_theoretical_probability_files_operation.for_each_spec(
                    on_each_spec=all_theoretical_probability_files_operation.on_each_spec)


        # 現実的に、完了しない想定
        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
