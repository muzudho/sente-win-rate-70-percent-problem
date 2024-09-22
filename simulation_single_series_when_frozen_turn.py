#
# シミュレーション
# python simulation_single_series_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, WHITE, ALICE, PointsConfiguration, make_cointoss_list, play_series_when_frozen_turn, SimulationResult
from database import get_df_muzudho_single_points_when_frozen_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_single_series_when_frozen_turn.log'

# 引き分けになる確率
DRAW_RATE = 0.0


def simulate(p, points_configuration, title):
    """シミュレート"""

    series_result_list = []

    # ［最長対局数］は計算で求められます
    longest_times = points_configuration.count_longest_time_when_frozen_turn()

    # １シリーズするだけ
    # -----------------

    cointoss_list = make_cointoss_list(
            p=p,
            draw_rate=DRAW_RATE,
            longest_times=longest_times)

    # ［先後固定制］で、シリーズを勝った方の手番を返す
    series_result = play_series_when_frozen_turn(
            cointoss_list=cointoss_list,
            p=p,
            draw_rate=DRAW_RATE,
            points_configuration=points_configuration)

    series_result_list.append(series_result)

    print(f"{len(series_result.winner_color_game_record)=}")

    b_step = points_configuration.b_step
    w_step = points_configuration.w_step
    span = points_configuration.span
    b_rest = span
    w_rest = span
    line_1_list = ['   S']
    line_2_list = [f'{b_rest:>4}']
    line_3_list = [f'{w_rest:>4}']

    for winner_color in series_result.winner_color_game_record:
        # 黒石        
        if winner_color == BLACK:
            line_1_list.append('   x')
            b_rest -= b_step
        
        # 白石
        elif winner_color == WHITE:
            line_1_list.append('   o')
            w_rest -= w_step
        
        # 勝者なし
        else:
            line_1_list.append('   .')

        line_2_list.append(f'{b_rest:>4}')
        line_3_list.append(f'{w_rest:>4}')

    print() # 改行
    print(' '.join(line_1_list))
    print(' '.join(line_2_list))
    print(' '.join(line_3_list))


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
        df_mr_ft = get_df_muzudho_single_points_when_frozen_turn()

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    points_configuration=specified_points_configuration,
                    title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
