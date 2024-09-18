#
# 生成
# python generate_b_w_target_strict.py
#
#   先手先取本数、後手先取本数を求める（厳密）
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import calculate_probability, PointRuleDescription


LOG_FILE_PATH = 'output/generate_b_w_target_strict.log'

# 後手が勝つのに必要な先取本数の上限
MAX_W_POINT = 6 # 99999

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
            best_b_require = 0
            best_w_require = 0

            # 計算過程
            process_list = []

            # p=0.5 は計算の対象外とします
            for b_require in range(1, 101):

                # 後手が勝つのに必要な先取本数の上限
                max_w_require = b_require
                if MAX_W_POINT < max_w_require:
                    max_w_require = MAX_W_POINT                

                for w_require in range (1, max_w_require+1):

                    balanced_black_win_rate = calculate_probability(
                        p=p,
                        H=b_require,
                        T=w_require)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    if error < best_error:
                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_require = b_require
                        best_w_require = w_require

                        # 計算過程
                        process = f"[{best_error:6.4f} 黒{best_b_require:>3} 白{best_w_require:>2}]"
                        process_list.append(process)
                        print(process, end='', flush=True) # すぐ表示


            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:

                # ［最長対局数（先後固定制）］
                #
                #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                #
                max_number_of_bout_in_frozen_turn = (best_b_require-1) + (best_w_require-1) + 1

                # 先手の勝ち点、後手の勝ち点、目標の勝ち点を求める
                point_rule_description = PointRuleDescription.let_points_from_require(best_b_require, best_w_require)

                text = ""
                #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
                text += f"先手勝率 {p*100:2.0f} ％ --調整後--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）  対局数ｍ～{max_number_of_bout_in_frozen_turn:>3}  先手勝ち{point_rule_description.b_step:2.0f}点、後手勝ち{point_rule_description.w_step:2.0f}点の{point_rule_description.target_point:3.0f}点先取制"

                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
