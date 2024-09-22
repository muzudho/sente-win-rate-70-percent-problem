#
# 分析
# python analysis_series_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, WHITE, ALICE, PointsConfiguration, PseudoSeriesResult, judge_series_when_frozen_turn, SimulationResult, make_all_results_of_cointoss_in_series_when_frozen_turn
from database import get_df_muzudho_single_points_when_frozen_turn
from views import stringify_series_log


LOG_FILE_PATH = 'output/analysis_series_when_frozen_turn.log'

# 引き分けになる確率
DRAW_RATE = 0.0


def analysis_series(series_result, p, points_configuration, title):
    """シリーズ１つを分析します"""

    text = stringify_series_log(
            # ［表が出る確率］（指定値）
            p=p,
            draw_rate=DRAW_RATE,
            # ［かくきんシステムのｐの構成］
            points_configuration=points_configuration,
            # シリーズの結果
            series_result=series_result,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # # TODO 表示とログ出力を終えた後でテスト
    # if simulation_result.shortest_time_th < points_configuration.count_shortest_time_when_frozen_turn():
    #     raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {simulation_result.shortest_time_th} が理論値 {points_configuration.count_shortest_time_when_frozen_turn()} を下回った")

    # if points_configuration.count_longest_time_when_frozen_turn() < simulation_result.longest_time_th:
    #     raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {simulation_result.longest_time_th} が理論値 {points_configuration.count_longest_time_when_frozen_turn()} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_ft = get_df_muzudho_single_points_when_frozen_turn()

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)


            # FIXME 動作テスト
            stats_result_data = make_all_results_of_cointoss_in_series_when_frozen_turn(
                    can_draw=False,
                    points_configuration=specified_points_configuration)
            for successful_color_list in stats_result_data:
                #print(f"動作テスト {successful_color_list=}")

                pseudo_series_result = PseudoSeriesResult(
                        p=None,                 # FIXME 未設定
                        draw_rate=DRAW_RATE,
                        longest_times=specified_points_configuration.count_longest_time_when_frozen_turn(),
                        successful_color_list=successful_color_list)

                #
                # FIXME 到達できない棋譜は除去しておきたい
                #

                old_number_of_times = len(successful_color_list)

                # ［先後固定制］で、シリーズを勝った方の手番を返す
                series_result = judge_series_when_frozen_turn(
                        pseudo_series_result=pseudo_series_result,
                        points_configuration=specified_points_configuration)

                if series_result.number_of_all_times < old_number_of_times:
                    # 棋譜の長さが短くなったということは、到達できない記録が混ざっていたということです。
                    print(f"到達できない棋譜を除去 {series_result.number_of_all_times=}  {old_number_of_times=}")
                    pass

                elif old_number_of_times < specified_points_configuration.count_shortest_time_when_frozen_turn():
                    # 棋譜の長さが足りていないということは、最後までプレイしていない
                    print(f"最後までプレイしていない棋譜を除去 {old_number_of_times=}  {specified_points_configuration.count_shortest_time_when_frozen_turn()=}")
                    pass

                #
                # FIXME 引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去したい
                #

                else:
                    analysis_series(
                            series_result=series_result,
                            p=p,
                            points_configuration=specified_points_configuration,
                            title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
