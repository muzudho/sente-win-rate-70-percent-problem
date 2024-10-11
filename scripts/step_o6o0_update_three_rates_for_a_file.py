import traceback
import time
import datetime
import pandas as pd

from library import TERMINATED, YIELD, CALCULATION_FAILED, OUT_OF_P, Converter, SeriesRule
from library.database import TheoreticalProbabilityRatesRecord
from library.score_board import search_all_score_boards
from library.views import DebugWrite


class Automation():
    """［理論的確率データ］（TP）表のスリー・レーツ列を更新する"""


    def __init__(self, seconds_of_time_up):

        # CSV保存用タイマー
        self._start_time_for_save = None
        self._seconds_of_time_up = seconds_of_time_up

        # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._number_of_dirty = 0


    def update_three_rates_for_a_file_and_save(self, spec, tp_table, tpr_table, upper_limit_upper_limit_coins):
        """次に、スリー・レーツを更新する

        ファイルの保存機能も含む
        
        Returns
        -------
        calculation_status : int
            計算状況
        """

        def on_score_board_created(score_board):
            pass

        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)

        # リセット
        self._number_of_dirty = 0
        self._start_time_for_save = time.time()       # CSV保存用タイマー

        # TODO TP表と TPR表を完全外部結合する
#         print(f"""\
# tp_table.df:
# {tp_table.df}

# tpr_table.df:
# {tpr_table.df}
# """)
        # TODO インデックスが消えてしまうので、 .reset_index() を使って、インデックスを列として生成します。
        # そしてマージしたあと、その列をインデックスに戻します
        tptpr_df = pd.merge(tp_table.df.reset_index(), tpr_table.df.reset_index(), how='outer', on=['span', 't_step', 'h_step']).set_index(['span', 't_step', 'h_step'])
#         print(f"""\
# tptpr_df:
# {tptpr_df}
# """)


        # 該当行にチェックを入れたリスト
        # ［理論的Ａさんの勝率］列が未設定で、かつ、［上限対局数］が、指定の上限対局数以下のとき
        list_of_enable_each_row = (pd.isnull(tptpr_df['theoretical_a_win_rate'])) & (tptpr_df['upper_limit_coins']<=upper_limit_upper_limit_coins)

        # 該当行が１つでもあれば
        if list_of_enable_each_row.any():

            # TP表が 5000行以上あるので、すごい時間がかかってしまう
            for index, row in tptpr_df[list_of_enable_each_row].iterrows():
#                 print(f"""\
# {index=}
# {row=}
# """)

                # 指定間隔（秒）でループを抜ける
                end_time_for_save = time.time()
                if self._seconds_of_time_up < end_time_for_save - self._start_time_for_save:
                    # 途中の行まで処理したところでタイムアップ。譲る（タイムシェアリング）
                    #print(f"途中の行まで処理したところでタイムアップ。譲る（タイムシェアリング）")
                    return YIELD

                span, t_step, h_step = index

                # ［シリーズ・ルール］
                specified_series_rule = SeriesRule.make_series_rule_base(
                        spec=spec,
                        span=span,
                        t_step=t_step,
                        h_step=h_step)

                # 確率を求める
                #
                #   NOTE 指数関数的に激重になっていく処理
                #
                three_rates, all_patterns_p = search_all_score_boards(
                        series_rule=specified_series_rule,
                        on_score_board_created=on_score_board_created)

                # データフレーム更新
                tpr_table.upsert_record(
                        welcome_record=TheoreticalProbabilityRatesRecord(
                                span=span,
                                t_step=t_step,
                                h_step=h_step,
                                theoretical_a_win_rate=three_rates.a_win_rate,
                                theoretical_no_win_match_rate=three_rates.no_win_match_rate))
                #
                #   FIXME ここは .at[] では不正なスカラーアクセスになる。なんで？
                #
                # tp_table.df.loc[index, 'theoretical_a_win_rate'] = three_rates.a_win_rate
                # tp_table.df.loc[index, 'theoretical_no_win_match_rate'] = three_rates.no_win_match_rate

                self._number_of_dirty += 1


        # 変更があれば保存
        if 0 < self._number_of_dirty:
            # CSVファイルへ書き出し
            tpr_csv_file_path_to_wrote = tpr_table.to_csv()

            print(f"{DebugWrite.stringify(spec=spec)}SAVE dirty={self._number_of_dirty}  {upper_limit_upper_limit_coins=}  write file to `{tpr_csv_file_path_to_wrote}` ...")

            # このファイルは処理完了した
            return TERMINATED


        # 処理失敗
        print(f"{DebugWrite.stringify(spec=spec)}UNCHANGE dirty={self._number_of_dirty}")
        return CALCULATION_FAILED
