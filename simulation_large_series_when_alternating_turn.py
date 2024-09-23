#
# シミュレーション
# python simulation_large_series_when_alternating_turn.py
#
#   ［先後交互制］
#   ［表の出る確率］ p が偏ったコインを、指定回数投げる
#   Ａさん（Alice）が最初に先手を持ち、１局毎にＢさん（Bob）と先後を交代する。
#

import traceback
import random
import math
import datetime
import pandas as pd

from fractions import Fraction
from library import ALICE, PointsConfiguration, play_game_when_alternating_turn, LargeSeriesTrialSummary, PseudoSeriesResult
from database import get_df_muzudho_recommends_points_when_alternating_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_large_series_when_alternating_turn.log'

# ［将棋の引分け率］
FAILURE_RATE = 0.0
#FAILURE_RATE = 0.1


def simulate_stats(p, number_of_series, pts_conf):
    """大量のシリーズをシミュレートします"""

    series_result_list = []

    for round in range(0, number_of_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        pseudo_series_result = PseudoSeriesResult.playout_pseudo(
                p=p,
                failure_rate=FAILURE_RATE,
                longest_times=pts_conf.count_longest_time_when_alternating_turn())

        # ［先後交互制］で、勝ったプレイヤーを返す
        series_result = play_game_when_alternating_turn(
                pseudo_series_result=pseudo_series_result,
                pts_conf=pts_conf)

        series_result_list.append(series_result)


    # シミュレーションの結果
    large_series_trial_summary = LargeSeriesTrialSummary(
            series_result_list=series_result_list)

    text = stringify_simulation_log(
            p=p,
            failure_rate=FAILURE_RATE,
            pts_conf=pts_conf,
            large_series_trial_summary=large_series_trial_summary,
            title="（先後交互制）")

    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力

    # # 表示とログ出力を終えた後でテスト
    # if large_series_trial_summary.shortest_time_th < expected_shortest_time_th_when_alternating_turn:
    #     raise ValueError(f"{p=} ［先後交互制］の最短対局数の実際値 {large_series_trial_summary.shortest_time_th} が理論値 {expected_shortest_time_th_when_alternating_turn} を下回った")

    # if expected_longest_time_th_when_alternating_turn < large_series_trial_summary.longest_time_th:
    #     raise ValueError(f"{p=} ［先後交互制］の最長対局数の実際値 {large_series_trial_summary.longest_time_th} が理論値 {expected_longest_time_th_when_alternating_turn} を上回った")


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
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate_stats(
                    p=p,
                    number_of_series=number_of_series,
                    pts_conf=specified_points_configuration)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
