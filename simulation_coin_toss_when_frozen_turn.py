#
# シミュレーション
# python simulation_coin_toss_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数（max_number_of_bout_when_frozen_turn）投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, ALICE, CoinToss, PointsConfiguration
from views import stringify_log_when_simulation_coin_toss_when_frozen_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_frozen_turn.log'
CSV_FILE_PATH_TSS = './data/takahashi_satoshi_system.csv'
CSV_FILE_PATH_EVEN = './data/generate_even_when_frozen_turn.csv'


def perform_p(coin_toss, p, round_total, b_time, w_time, comment):

    # ［勝ち点ルール］の構成
    points_configuration = PointsConfiguration.let_points_from_repeat(b_time, w_time)

    # ［先後固定制］で、黒が勝った回数
    black_wons = 0
    shortest_bout_th_when_frozen_turn = 2_147_483_647
    longest_bout_th_when_frozen_turn = 0

    for round in range(0, round_total):
        # ［先後固定制］で、勝った方の手番を返す
        winner_color, bout_th = coin_toss.play_game_when_frozen_turn(p, b_time, w_time)
        if winner_color == BLACK:
            black_wons += 1

        if bout_th < shortest_bout_th_when_frozen_turn:
            shortest_bout_th_when_frozen_turn = bout_th
        
        if longest_bout_th_when_frozen_turn < bout_th:
            longest_bout_th_when_frozen_turn = bout_th


    # ［先後交互制］で、Ａさんが勝った回数
    alice_wons = 0
    shortest_bout_th_when_alternating_turn = 2_147_483_647
    longest_bout_th_when_alternating_turn = 0

    for round in range(0, round_total):
        # ［先後交互制］で、勝った方のプレイヤーを返す
        winner_player, bout_th = coin_toss.play_game_when_alternating_turn(p, points_configuration)
        if winner_player == ALICE:
            alice_wons += 1

        if bout_th < shortest_bout_th_when_alternating_turn:
            shortest_bout_th_when_alternating_turn = bout_th
        
        if longest_bout_th_when_alternating_turn < bout_th:
            longest_bout_th_when_alternating_turn = bout_th


    # 最短対局数、最長対局数のテスト
    expected_shortest_bout_th_when_frozen_turn=points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    actual_shortest_bout_th_when_frozen_turn=shortest_bout_th_when_frozen_turn
    expected_longest_bout_th_when_frozen_turn=points_configuration.let_number_of_longest_bout_when_frozen_turn()
    actual_longest_bout_th_when_frozen_turn=longest_bout_th_when_frozen_turn
    alice_wons=alice_wons
    expected_shortest_bout_th_when_alternating_turn=points_configuration.let_number_of_shortest_bout_when_alternating_turn()
    actual_shortest_bout_th_when_alternating_turn=shortest_bout_th_when_alternating_turn
    expected_longest_bout_th_when_alternating_turn=points_configuration.let_number_of_longest_bout_when_alternating_turn()
    actual_longest_bout_th_when_alternating_turn=longest_bout_th_when_alternating_turn

    text = stringify_log_when_simulation_coin_toss_when_frozen_turn(
            # 出力先ファイルへのパス
            output_file_path=coin_toss.output_file_path,
            # ［表が出る確率］（先手勝率）
            p=p,
            # 対局数
            round_total=round_total,
            # ［先後固定制］で、黒が勝った回数
            black_wons=black_wons,
            expected_shortest_bout_th_when_frozen_turn=expected_shortest_bout_th_when_frozen_turn,
            actual_shortest_bout_th_when_frozen_turn=actual_shortest_bout_th_when_frozen_turn,
            expected_longest_bout_th_when_frozen_turn=expected_longest_bout_th_when_frozen_turn,
            actual_longest_bout_th_when_frozen_turn=actual_longest_bout_th_when_frozen_turn,
            # ［先後交互制］で、Ａさんが勝った回数
            alice_wons=alice_wons,
            expected_shortest_bout_th_when_alternating_turn=expected_shortest_bout_th_when_alternating_turn,
            actual_shortest_bout_th_when_alternating_turn=actual_shortest_bout_th_when_alternating_turn,
            expected_longest_bout_th_when_alternating_turn=expected_longest_bout_th_when_alternating_turn,
            actual_longest_bout_th_when_alternating_turn=actual_longest_bout_th_when_alternating_turn,
            # ［勝ち点ルール］の構成
            points_configuration=points_configuration,
            # コメント
            comment=comment)


    print(text) # 表示

    # ログ出力
    with open(coin_toss.output_file_path, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if actual_shortest_bout_th_when_frozen_turn < expected_shortest_bout_th_when_frozen_turn:
        raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {actual_shortest_bout_th_when_frozen_turn} が理論値 {expected_shortest_bout_th_when_frozen_turn} を下回った")

    if expected_longest_bout_th_when_frozen_turn < actual_longest_bout_th_when_frozen_turn:
        raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {actual_longest_bout_th_when_frozen_turn} が理論値 {expected_longest_bout_th_when_frozen_turn} を上回った")

    if actual_shortest_bout_th_when_alternating_turn < expected_shortest_bout_th_when_alternating_turn:
        raise ValueError(f"{p=} ［先後交互制］の最短対局数の実際値 {actual_shortest_bout_th_when_alternating_turn} が理論値 {expected_shortest_bout_th_when_alternating_turn} を下回った")

    if expected_longest_bout_th_when_alternating_turn < actual_longest_bout_th_when_alternating_turn:
        raise ValueError(f"{p=} ［先後交互制］の最長対局数の実際値 {actual_longest_bout_th_when_alternating_turn} が理論値 {expected_longest_bout_th_when_alternating_turn} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_even = pd.read_csv(CSV_FILE_PATH_EVEN, encoding="utf8")
        df_tss = pd.read_csv(CSV_FILE_PATH_TSS, encoding="utf8")

        coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 10 # 少なすぎるケース


        # 精度が高いデータを基にしている
        for p, number_of_longest_bout_when_frozen_turn, w_time in zip(df_even['p'], df_even['number_of_longest_bout_when_frozen_turn'], df_even['w_time']):
            # ［黒だけでの回数］は計算で求めます
            b_time = number_of_longest_bout_when_frozen_turn-(w_time-1)

            perform_p(coin_toss, p, round_total, b_time, w_time, comment='精度を求めた元データ')


        # 実用的なデータを基にしている
        for p, b_time, w_time in zip(df_tss['p'], df_tss['b_time'], df_tss['w_time']):
            perform_p(coin_toss, p, round_total, b_time, w_time, comment='実用的な元データ')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
