#
# シミュレーション
# python simulation_coin_toss.py
#
#   表の出る確率（black_win_rate）が偏ったコインを、指定回数（max_bout_count）投げる
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, CoinToss
from views import write_coin_toss_log


SUMMARY_FILE_PATH = 'output/simulation_coin_toss.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        round_total = 2_000_000

        df = pd.read_csv(
                "./data/takahashi_satoshi_system.csv",
                encoding="utf8")

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_point, w_point in zip(df['p'], df['b_point'], df['w_point']):
            coin_toss = CoinToss(output_file_path=SUMMARY_FILE_PATH)

            # 対局数
            round_total=round_total

            # 黒が勝った回数
            black_wons = 0

            for round in range(0, round_total):
                if coin_toss.coin_toss_in_round(p, b_point, w_point) == BLACK:
                    black_wons += 1


            # ログ出力
            write_coin_toss_log(
                    # 出力先ファイルへのパス
                    output_file_path=coin_toss.output_file_path,
                    # 先手勝率
                    black_win_rate=p,
                    # 先手の何本先取制
                    b_point=b_point,
                    # 後手の何本先取制
                    w_point=w_point,
                    # 対局数
                    round_total=round_total,
                    # 黒が勝った回数
                    black_wons=black_wons)

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
