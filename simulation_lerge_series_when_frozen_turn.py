#
# シミュレーション
# python simulation_lerge_series_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, ALICE, PointsConfiguration, PseudoSeriesResult, judge_series_when_frozen_turn, LargeSeriesTrialSummary
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_lerge_series_when_frozen_turn.log'

# 引き分けになる確率
#DRAW_RATE = 0.0
DRAW_RATE = 0.1


def simulate_stats(p, number_of_series, pts_conf, title):
    """大量のシリーズをシミュレートします"""

    series_result_list = []

    # ［最長対局数］は計算で求められます
    longest_times = pts_conf.number_longest_time_when_frozen_turn

    for round in range(0, number_of_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        pseudo_series_result = PseudoSeriesResult.playout_pseudo(
                p=p,
                draw_rate=DRAW_RATE,
                longest_times=longest_times)

        # ［先後固定制］で、シリーズを勝った方の手番を返す
        series_result = judge_series_when_frozen_turn(
                pseudo_series_result=pseudo_series_result,
                pts_conf=pts_conf)
        
        series_result_list.append(series_result)


    # シミュレーションの結果
    large_series_trial_summary = LargeSeriesTrialSummary(
            series_result_list=series_result_list)

    text = stringify_simulation_log(
            # ［表が出る確率］（指定値）
            p=p,
            draw_rate=DRAW_RATE,
            # ［かくきんシステムのｐの構成］
            pts_conf=pts_conf,
            # シミュレーションの結果
            large_series_trial_summary=large_series_trial_summary,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if large_series_trial_summary.shortest_time_th < pts_conf.number_shortest_time_when_frozen_turn:
        raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {large_series_trial_summary.shortest_time_th} が理論値 {pts_conf.number_shortest_time_when_frozen_turn} を下回った")

    if pts_conf.number_longest_time_when_frozen_turn < large_series_trial_summary.longest_time_th:
        raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {large_series_trial_summary.longest_time_th} が理論値 {pts_conf.number_longest_time_when_frozen_turn} を上回った")


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

            simulate_stats(
                    p=p,
                    number_of_series=number_of_series,
                    pts_conf=specified_points_configuration,
                    title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
