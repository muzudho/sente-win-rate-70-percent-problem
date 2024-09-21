#
# シミュレーション
# python simulation_series_with_draw_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けを考慮する。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import EMPTY, BLACK, WHITE, round_letro, PointsConfiguration, play_series_with_draw_when_frozen_turn, play_tie_break
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_log_when_simulation_series_with_draw_when_frozen_turn


LOG_FILE_PATH = 'output/simulation_series_when_frozen_turn.log'

# 引き分けになる確率
#DRAW_RATE = 0.1
DRAW_RATE = 0.9


def simulate(p, round_total, points_configuration, comment):

    # 黒が勝った回数
    black_wons = 0

    # ［勝ち点差判定が行われた回数］
    number_of_judge_in_points = 0

    # ［勝ち点差で黒が勝った回数］
    black_wons_in_points = 0

    # ［タイブレークで黒が勝った回数］
    black_wons_in_tie_break = 0

    sum_number_of_ties_throughout_series = 0

    # 試行全体を通して引き分けた数
    number_of_ties_throughout_trial = 0

    shortest_time_th = 2_147_483_647
    longest_time_th = 0

    for round in range(0, round_total):

        # ［先後固定制］で、勝った方の手番を返す。引き分けを１局と数える
        winner_color, time_th, new_number_of_ties_throughout_series, reason = play_series_with_draw_when_frozen_turn(
                p=p,
                draw_rate=DRAW_RATE,
                points_configuration=points_configuration)
        
        sum_number_of_ties_throughout_series += new_number_of_ties_throughout_series

        # 勝ち点による決着
        if reason == 'points':
            number_of_judge_in_points += 1

            if winner_color == BLACK:
                black_wons_in_points += 1

        # 黒勝ち
        if winner_color == BLACK:
            black_wons += 1

        # 白勝ち        
        elif winner_color == WHITE:
            pass

        # 引分け（勝ち点が同点）
        else:
            number_of_ties_throughout_trial += 1

            # 引き分けならタイブレークを行う場合
            #
            #   FIXME 当然、引き分け率が上がるほど白有利になる
            #
            winner_color = play_tie_break(
                p=p,
                draw_rate=DRAW_RATE)
            
            # タイブレークによる決着
            if winner_color == BLACK:
                black_wons += 1
                black_wons_in_tie_break += 1


        if time_th < shortest_time_th:
            shortest_time_th = time_th
        
        if longest_time_th < time_th:
            longest_time_th = time_th


    # ［最短対局数］の期待値と実際値、［最長対局数］の期待値と実際値
    expected_shortest_time_th=points_configuration.count_shortest_time_when_frozen_turn()
    actual_shortest_time_th=shortest_time_th
    expected_longest_time_th=points_configuration.count_longest_time_when_frozen_turn()
    actual_longest_time_th=longest_time_th

    text = stringify_log_when_simulation_series_with_draw_when_frozen_turn(
            # 出力先ファイルへのパス
            output_file_path=LOG_FILE_PATH,
            # ［表が出る確率］（指定値）
            p=p,
            # ［引き分ける確率］
            draw_rate=DRAW_RATE,
            # 対局数
            round_total=round_total,
            # ［勝ち点差判定が行われた回数］
            number_of_judge_in_points=number_of_judge_in_points,
            # 黒が勝った回数
            black_wons=black_wons,
            # ［勝ち点差で黒が勝った回数］
            black_wons_in_points=black_wons_in_points,
            # ［タイブレークで黒が勝った回数］
            black_wons_in_tie_break=black_wons_in_tie_break,
            # ［引き分けた回数］
            number_of_ties=number_of_ties_throughout_trial,
            sum_number_of_ties_throughout_series=sum_number_of_ties_throughout_series,

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
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    #
    #   FIXME ［引き分けを１局として数えるケース］では、対局数の計算がまだ実装できていません
    #
    print("［引き分けを１局として数えるケース］では、対局数の計算がまだ実装できていません")
    # if actual_shortest_time_th < expected_shortest_time_th:
    #     raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {actual_shortest_time_th} が理論値 {expected_shortest_time_th} を下回った")

    # if expected_longest_time_th < actual_longest_time_th:
    #     raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {actual_longest_time_th} が理論値 {expected_longest_time_th} を上回った")


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

            #
            #   NOTE ［目標の点数］を整数倍すると、最小公倍数が何回も出てきて、引き分けになる回数も整数倍になる
            #

            # ［かくきんシステムのｐの構成］           
            print("確率調整中")  # FIXME
            points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    round_total=round_count,
                    points_configuration=points_configuration,
                    comment='むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
