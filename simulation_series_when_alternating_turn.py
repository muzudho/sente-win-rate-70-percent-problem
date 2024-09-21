#
# シミュレーション
# python simulation_series_when_alternating_turn.py
#
#   ［先後交互制］
#   引き分けは考慮していない。
#   ［表の出る確率］ p が偏ったコインを、指定回数投げる
#   Ａさん（Alice）が最初に先手を持ち、１局毎にＢさん（Bob）と先後を交代する。
#

import traceback
import random
import math
import datetime
import pandas as pd

from fractions import Fraction
from library import ALICE, PointsConfiguration, play_game_when_alternating_turn, SimulationResultWhenAlternatingTurn
from database import get_df_muzudho_recommends_points_when_alternating_turn
from views import stringify_log_when_simulation_series_when_alternating_turn


LOG_FILE_PATH = 'output/simulation_series_when_alternating_turn.log'


def simulate(p, number_of_series, points_configuration):
    """シミュレート"""

    series_result_at_list = []

    for round in range(0, number_of_series):

        # ［先後交互制］で、勝ったプレイヤーを返す
        series_result_at = play_game_when_alternating_turn(p, points_configuration)
        series_result_at_list.append(series_result_at)


    # シミュレーションの結果
    simulation_result_at = SimulationResultWhenAlternatingTurn(
            series_result_at_list=series_result_at_list)

    text = stringify_log_when_simulation_series_when_alternating_turn(
            p=p,
            points_configuration=points_configuration,
            simulation_result_at=simulation_result_at)

    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力

    # # 表示とログ出力を終えた後でテスト
    # if simulation_result.shortest_time_th < expected_shortest_time_th_when_alternating_turn:
    #     raise ValueError(f"{p=} ［先後交互制］の最短対局数の実際値 {simulation_result.shortest_time_th} が理論値 {expected_shortest_time_th_when_alternating_turn} を下回った")

    # if expected_longest_time_th_when_alternating_turn < simulation_result.longest_time_th:
    #     raise ValueError(f"{p=} ［先後交互制］の最長対局数の実際値 {simulation_result.longest_time_th} が理論値 {expected_longest_time_th_when_alternating_turn} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_at = get_df_muzudho_recommends_points_when_alternating_turn()

        # 対局数
        number_of_series = 2_000_000 # 十分多いケース
        #number_of_series = 200

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_at['p'], df_mr_at['b_step'], df_mr_at['w_step'], df_mr_at['span'], df_mr_at['presentable'], df_mr_at['comment'], df_mr_at['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    number_of_series=number_of_series,
                    points_configuration=specified_points_configuration)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
