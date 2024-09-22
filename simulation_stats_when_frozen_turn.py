#
# シミュレーション
# python simulation_stats_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, ALICE, PointsConfiguration, CointossResultInSeries, play_series_when_frozen_turn, SimulationResult
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_stats_when_frozen_turn.log'

# 引き分けになる確率
DRAW_RATE = 0.0


def simulate(p, number_of_series, points_configuration, title):
    """シミュレート"""

    series_result_list = []

    # ［最長対局数］は計算で求められます
    longest_times = points_configuration.count_longest_time_when_frozen_turn()

    for round in range(0, number_of_series):

        cointoss_result_in_series = CointossResultInSeries.make_cointoss_result_in_series(
                p=p,
                draw_rate=DRAW_RATE,
                longest_times=longest_times)

        # ［先後固定制］で、シリーズを勝った方の手番を返す
        series_result = play_series_when_frozen_turn(
                cointoss_result_in_series=cointoss_result_in_series,
                points_configuration=points_configuration)
        
        series_result_list.append(series_result)


    # シミュレーションの結果
    simulation_result = SimulationResult(
            series_result_list=series_result_list)

    text = stringify_simulation_log(
            # ［表が出る確率］（指定値）
            p=p,
            draw_rate=DRAW_RATE,
            # ［かくきんシステムのｐの構成］
            points_configuration=points_configuration,
            # シミュレーションの結果
            simulation_result=simulation_result,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if simulation_result.shortest_time_th < points_configuration.count_shortest_time_when_frozen_turn():
        raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {simulation_result.shortest_time_th} が理論値 {points_configuration.count_shortest_time_when_frozen_turn()} を下回った")

    if points_configuration.count_longest_time_when_frozen_turn() < simulation_result.longest_time_th:
        raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {simulation_result.longest_time_th} が理論値 {points_configuration.count_longest_time_when_frozen_turn()} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_ft = get_df_muzudho_recommends_points_when_frozen_turn()

        # 対局数
        number_of_series = 2_000_000 # 十分多いケース
        #number_of_series = 10 # 少なすぎるケース

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    number_of_series=number_of_series,
                    points_configuration=specified_points_configuration,
                    title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
