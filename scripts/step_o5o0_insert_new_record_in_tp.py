import traceback
import datetime
import pandas as pd

from library import EVEN, Converter, is_almost_zero, OUT_OF_P, Converter, SeriesRule, round_letro
from library.file_paths import TheoreticalProbabilityFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityRecord
from scripts import SaveOrIgnore, ForEachSeriesRule


class Automation():
    """［理論的確率データ］（TP）表に新規行を挿入する。

    FIXME 更新するつもりはないが、既存行が一斉に同じレコードになるような不具合が起こる
    アップサートにしても解決しない
    NOTE 主キーや、ロック機構がないので、インデックスが重複するようなレコードを追加できてしまう？
    """


    def __init__(self, depth):
        """初期化"""
        self._depth = depth

        # CSV保存用タイマー
        self._start_time_for_save = None

        # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._number_of_dirty = 0


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
                return self._number_of_dirty

        #
        # NOTE 内容をどれぐらい作るかは、 upper_limit_span （span の上限）を指定することにする。
        # 数字が増えると処理が重くなる。 10 ぐらいまですぐ作れるが、 20 を超えると数秒かかるようになる
        #
        upper_limit_span = self._depth

        #
        # FIXME 飛び番で挿入されてる？
        #
        #print(f"{self.stringify_log_stamp(spec=spec)}step o2o1o0 insert new record in tp...")
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
            # TODO 最後に処理された span は？
            span = round_letro(tp_table._df['span'].max())

            # TODO 最後に処理された span のうち、最後に処理された t_step は？
            t_step = round_letro(tp_table._df.loc[tp_table._df['span']==span, 't_step'].max())

            # TODO 最後に処理された span, t_step のうち、最後に処理された h_step は？
            h_step = round_letro(tp_table._df.loc[(tp_table._df['span']==span) & (tp_table._df['t_step']==t_step), 'h_step'].max())

            # カウントアップ
            span, t_step, h_step = ForEachSeriesRule.increase(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            print(f"{datetime.datetime.now()}RESTART_ {span=:2}  {t_step=:2}  {h_step=:2}")


        #
        # TODO ロック機構がないと、データの整合性が取れないのでは？
        #
        while span < upper_limit_span + 1:

            # インデックス
            result_set_df_by_index = tp_table.get_result_set_by_index(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)
            
            if 1 < len(result_set_df_by_index):
                raise ValueError(f"テーブルが壊れています。インデックスが重複するデータが {len(result_set_df_by_index)} 件ありました")

            if len(result_set_df_by_index) == 1:
                raise ValueError(f"プログラムが壊れています。指定した新しいインデックスが既に存在します")


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
            # FIXME 追加ではなく、先頭から上書き保存になってる？
            tp_table.insert_record(
                    welcome_record=TheoreticalProbabilityRecord(
                            span=span,
                            t_step=t_step,
                            h_step=h_step,
                            shortest_coins=series_rule.shortest_coins,
                            upper_limit_coins=series_rule.upper_limit_coins,

                            # NOTE スリー・レーツを求める処理は重たいので、後回しにする
                            theoretical_a_win_rate=OUT_OF_P,
                            theoretical_no_win_match_rate=OUT_OF_P))
            
            self._number_of_dirty += 1


            # カウントアップ
            span, t_step, h_step = ForEachSeriesRule.increase(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            # FIXME DEBUG
            print("デバッグ中166")
            SaveOrIgnore.execute(
                    log_file_path=TheoreticalProbabilityFilePaths.as_log(
                            turn_system_id=spec.turn_system_id,
                            failure_rate=spec.failure_rate,
                            p=spec.p),
                    on_save_and_get_file_name=tp_table.to_csv)


        # ［理論的確率データ］（TP）ファイル保存
        if 0 < self._number_of_dirty:

            SaveOrIgnore.execute(
                    log_file_path=TheoreticalProbabilityFilePaths.as_log(
                            turn_system_id=spec.turn_system_id,
                            failure_rate=spec.failure_rate,
                            p=spec.p),
                    on_save_and_get_file_name=tp_table.to_csv)
            print(f"{self.stringify_log_stamp(spec=spec)}SAVED dirty={self._number_of_dirty}")
            self._number_of_dirty = 0


        return self._number_of_dirty


    def stringify_log_stamp(self, spec):
        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        return f"""\
[{datetime.datetime.now()}][depth={self._depth}  turn_system_name={turn_system_name:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] \
"""
