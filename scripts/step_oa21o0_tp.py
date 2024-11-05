import traceback
import datetime
import pandas as pd

from library import EVEN, Converter, Precision, Converter, SeriesRule, round_letro
from library.file_paths import TheoreticalProbabilityFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityRecord
from library.views import DebugWrite
from scripts import SaveOrIgnore, ForEachSeriesRule


class GeneratorOfTP():
    """［理論的確率データ］（TP）表に新規行を挿入する。

    FIXME 更新するつもりはないが、既存行が一斉に同じレコードになるような不具合が起こる
    アップサートにしても解決しない
    NOTE 主キーや、ロック機構がないので、インデックスが重複するようなレコードを追加できてしまう？
    """


    def __init__(self, depth):
        """初期化"""
        self._depth = depth

        self._start_time_for_save = None    # CSV保存用タイマー

        self._number_of_dirty = 0   # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._row_number_th = 0             # 行番号。先頭行を１とする
        self._row_number_when_even = None   # あれば、誤差が0になった行の番号


    @property
    def depth(self):
        return self._depth


    def execute_by_spec(self, spec):
        """実行

        Parameters
        ----------
        spec : Specification
            ［仕様］
        
        Returns
        -------
        number_of_dirty : int
            変更のあった行数
        """

        self._row_number_th += 1

        # ファイルが存在しなければ、新規作成する。あれば読み込む
        tp_table, tp_file_read_result = TheoreticalProbabilityTable.from_csv(spec=spec, new_if_it_no_exists=True)


        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)

        if tp_file_read_result.is_file_not_found:
            turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
            print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}NEW_FILE(C)")

            # １件も処理してないが、ファイルを保存したいのでフラグを立てる
            self._number_of_dirty += 1

        # else:
        #     # TODO ファイルが既存で、テーブルの中で、誤差がほぼ０の行が含まれているなら、探索打ち切り
        #     min_abs_error = (tp_table.df['expected_a_victory_rate_by_duet'] - EVEN).abs().min()
        #     if Precision.is_it_zero_enough(min_abs_error):
        #         turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        #         print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}READY_EVEN....")
        #         return self._number_of_dirty

        #
        # NOTE 内容をどれぐらい作るかは、 upper_limit_span （span の上限）を指定することにする。
        # 数字が増えると処理が重くなる。 10 ぐらいまですぐ作れるが、 20 を超えると数秒かかるようになる
        #
        upper_limit_span = self._depth

        #
        # FIXME 飛び番で挿入されてる？
        #
        #turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        #print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}step o2o1o0 insert new record in tp...")
        # まず、［理論的確率データ］ファイルに span, t_step, h_step のインデックスを持った仮行をある程度の数、追加していく。このとき、スリー・レーツ列は入れず、空けておく

        # ループカウンター
        # 空テーブル時
        if len(tp_table._df) < 1:
            span = 1        # ［目標の点数］
            t_step = 1      # ［後手で勝ったときの勝ち点］
            h_step = 1      # ［先手で勝ったときの勝ち点］

        else:
            # 途中まで処理が終わってるんだったら、途中から再開したいが。ループの途中から始められるか？

            #
            # NOTE 4.999...9997 みたいな数が入ってたら int() で 4 に切り下げられるの嫌なので、 round_letro() を使う
            #

            # FIXME ここもっと簡潔に書けそう？
#             print(f"""\
# tp_table._df:
# {tp_table._df}

# tp_table._df.index:
# {tp_table._df.index}

# tp_table._df.index.values[-1]:
# {tp_table._df.index.values[-1]}
# """)

            # NOTE 昇順にソートされている前提で、最後の行のインデックスを取得
            last_index = tp_table._df.index.values[-1]

            # TODO 最後に処理された span は？
            span = last_index[0]    #round_letro(tp_table._df['span'].max())

            # TODO 最後に処理された span のうち、最後に処理された t_step は？
            t_step = last_index[1]  #round_letro(tp_table._df.loc[tp_table._df['span']==span, 't_step'].max())

            # TODO 最後に処理された span, t_step のうち、最後に処理された h_step は？
            h_step = last_index[2]  #round_letro(tp_table._df.loc[(tp_table._df['span']==span) & (tp_table._df['t_step']==t_step), 'h_step'].max())

            # カウントアップ
            span, t_step, h_step = ForEachSeriesRule.increase(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
            #print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)} RESTART {span=:2}  {t_step=:2}  {h_step=:2}")


        #
        # TODO ロック機構がないと、データの整合性が取れないのでは？
        #
        while span < upper_limit_span + 1:

            # ［シリーズ・ルール］
            #
            #   ［最短対局数］と［上限対局数］を求めるのに使う
            #
            series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            # レコードの挿入
            tp_table.upsert_record(
                    welcome_record=TheoreticalProbabilityRecord(
                            span=span,
                            t_step=t_step,
                            h_step=h_step,
                            shortest_coins=series_rule.shortest_coins,
                            upper_limit_coins=series_rule.upper_limit_coins))
            
            self._number_of_dirty += 1


            # カウントアップ
            span, t_step, h_step = ForEachSeriesRule.increase(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            # # FIXME DEBUG 本来、ここでは保存しない
            # print("デバッグ中166")
            # SaveOrIgnore.execute(
            #         log_file_path=TheoreticalProbabilityFilePaths.as_log(spec=spec),
            #         on_save_and_get_file_name=tp_table.to_csv)


        # ［理論的確率データ］（TP）ファイル保存
        if 0 < self._number_of_dirty:

            successful, target_file_path = SaveOrIgnore.execute(
                    log_file_path=TheoreticalProbabilityFilePaths.as_log(spec=spec),
                    on_save_and_get_file_name=tp_table.to_csv)
            
            if successful:
                turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
                print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}SAVED dirty={self._number_of_dirty} file={target_file_path}")
                self._number_of_dirty = 0


        return self._number_of_dirty
