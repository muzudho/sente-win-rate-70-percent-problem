#
# 生成
# python generate_b_w_repeat_strict.py
#
#   先後固定制で、先手勝ち点だけで勝つのに必要な数［反復数］、後手勝ち点だけで勝つのに必要な数［反復数］を求める（厳密）
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import calculate_probability, PointsConfiguration
from views import stringify_when_generate_b_w_repeat_strict


LOG_FILE_PATH = 'output/generate_b_w_repeat_strict.log'

# 先後固定制で、後手勝ち点だけで勝つのに必要な数［反復数］の上限
MAX_W_REPEAT_WHEN_FROZEN_TURN = 6 # 99999

OUT_OF_ERROR = 0.51


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = pd.read_csv("./data/p.csv", encoding="utf8")

        # 先手勝率
        for p in df['p']:

            # ベストな調整後の先手勝率と、その誤差
            best_balanced_black_win_rate = None
            best_error = OUT_OF_ERROR
            best_b_repeat_when_frozen_turn = 0
            best_w_repeat_when_frozen_turn = 0

            # 計算過程
            process_list = []

            # p=0.5 は計算の対象外とします
            for b_repeat_when_frozen_turn in range(1, 101):

                # 先後固定制で、後手勝ち点だけで勝つのに必要な数［反復数］の上限
                max_w_repeat_when_frozen_turn = b_repeat_when_frozen_turn
                if MAX_W_REPEAT_WHEN_FROZEN_TURN < max_w_repeat_when_frozen_turn:
                    max_w_repeat_when_frozen_turn = MAX_W_REPEAT_WHEN_FROZEN_TURN                

                for w_repeat_when_frozen_turn in range (1, max_w_repeat_when_frozen_turn+1):

                    balanced_black_win_rate = calculate_probability(
                        p=p,
                        H=b_repeat_when_frozen_turn,
                        T=w_repeat_when_frozen_turn)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    if error < best_error:
                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_repeat_when_frozen_turn = b_repeat_when_frozen_turn
                        best_w_repeat_when_frozen_turn = w_repeat_when_frozen_turn

                        # 計算過程
                        process = f"[{best_error:6.4f} 黒{best_b_repeat_when_frozen_turn:>3} 白{best_w_repeat_when_frozen_turn:>2}]"
                        process_list.append(process)
                        print(process, end='', flush=True) # すぐ表示


            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:

                # ［勝ち点ルール］の構成
                points_configuration = PointsConfiguration.let_points_from_repeat(best_b_repeat_when_frozen_turn, best_w_repeat_when_frozen_turn)

                text = stringify_when_generate_b_w_repeat_strict(p, best_balanced_black_win_rate, best_error, points_configuration, process_list)
                print(text) # 表示

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
