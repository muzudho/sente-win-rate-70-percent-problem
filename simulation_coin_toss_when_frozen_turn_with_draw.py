#
# シミュレーション
# python simulation_coin_toss_when_frozen_turn_with_draw.py
#
#   ［先後固定制］
#   引き分けを考慮する。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, ALICE, PointsConfiguration, play_series_when_frozen_turn, play_game_when_alternating_turn
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_log_when_simulation_coin_toss_when_frozen_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_frozen_turn.log'

# 引き分けになる確率
DRAW_RATE = 0.1


def simulate(p, round_total, b_time, w_time, comment):

    # ［かくきんシステムのｐの構成］
    points_configuration = PointsConfiguration.let_points_from_repeat(
            b_time=b_time,
            w_time=w_time)

    # 黒が勝った回数
    black_wons = 0
    shortest_time_th = 2_147_483_647
    longest_time_th = 0

    for round in range(0, round_total):

        points_configuration = PointsConfiguration.let_points_from_repeat(
                b_time=b_time,
                w_time=w_time)

        # ［先後固定制］で、勝った方の手番を返す
        winner_color, time_th = play_series_when_frozen_turn(
                p=p,
                points_configuration=points_configuration)
        
        if winner_color == BLACK:
            black_wons += 1

        if time_th < shortest_time_th:
            shortest_time_th = time_th
        
        if longest_time_th < time_th:
            longest_time_th = time_th


    # 最短対局数、最長対局数のテスト
    expected_shortest_time_th=points_configuration.count_shortest_time_when_frozen_turn()
    actual_shortest_time_th=shortest_time_th
    expected_longest_time_th=points_configuration.count_longest_time_when_frozen_turn()
    actual_longest_time_th=longest_time_th_when_frozen_turn

    text = stringify_log_when_simulation_coin_toss_when_frozen_turn(
            # 出力先ファイルへのパス
            output_file_path=LOG_FILE_PATH,
            # ［表が出る確率］（先手勝率）
            p=p,
            # 対局数
            round_total=round_total,
            # ［先後固定制］で、黒が勝った回数
            black_wons=black_wons,
            expected_shortest_time_th=expected_shortest_time_th,
            actual_shortest_time_th=actual_shortest_time_th,
            expected_longest_time_th=expected_longest_time_th,
            actual_longest_time_th=actual_longest_time_th,
            # ［かくきんシステムのｐの構成］
            points_configuration=points_configuration,
            # コメント
            comment=comment)


    print(text) # 表示

    # ログ出力
    with open(output_file_path, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if actual_shortest_time_th < expected_shortest_time_th:
        raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {actual_shortest_time_th} が理論値 {expected_shortest_time_th} を下回った")

    if expected_longest_time_th < actual_longest_time_th:
        raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {actual_longest_time_th} が理論値 {expected_longest_time_th} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_ft = get_df_muzudho_recommends_points_when_frozen_turn()

        # 対局数
        round_count = 2_000_000 # 十分多いケース
        #round_count = 10 # 少なすぎるケース

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    round_total=round_count,
                    b_time=specified_points_configuration.b_time,
                    w_time=specified_points_configuration.w_time,
                    comment='むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
