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

from library import calculate_probability


SUMMARY_FILE_PATH = 'output/generate_b_w_target_strict.log'

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
            best_b_point = 0
            best_w_point = 0

            # 計算過程
            process_list = []

            # p=0.5 は計算の対象外とします
            for b_point in range(1, 101):

                # 後手が勝つのに必要な先取本数の上限
                max_w_point = b_point
                if MAX_W_POINT < max_w_point:
                    max_w_point = MAX_W_POINT                

                for w_point in range (1, max_w_point+1):

                    balanced_black_win_rate = calculate_probability(
                        p=p,
                        H=b_point,
                        T=w_point)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    if error < best_error:
                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_point = b_point
                        best_w_point = w_point

                        # 計算過程
                        process = f"[{best_error:6.4f} 黒{best_b_point:>3} 白{best_w_point:>2}]"
                        process_list.append(process)
                        print(process, end='', flush=True) # すぐ表示


            # 計算過程の表示の切れ目
            print() # 改行


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                # 最大ｎ本勝負
                #
                #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                #
                max_bout_count = best_b_point + best_w_point - 1

                # 後手がアドバンテージを持っているという表記に変更
                w_advantage = best_b_point - best_w_point

                # DO 通分したい。最小公倍数を求める
                lcm = math.lcm(best_b_point, best_w_point)
                # 先手一本の価値
                b_unit = lcm / best_b_point
                # 後手一本の価値
                w_unit = lcm / best_w_point
                # 先手勝ち、後手勝ちの共通ゴール
                b_win_value_goal = best_w_point * w_unit
                w_win_value_goal = best_b_point * b_unit
                if b_win_value_goal != w_win_value_goal:
                    raise ValueError(f"{b_win_value_goal=}  {w_win_value_goal=}")

                text = ""
                #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
                text += f"先手勝率 {p*100:2.0f} ％ --調整後--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）  {max_bout_count:>3}本勝負（ただし、{best_b_point:>3}本先取制。後手は最初から {w_advantage:>2} 本持つアドバンテージ）  つまり、先手一本の価値{b_unit:2.0f}  後手一本の価値{w_unit:2.0f}  ゴール{b_win_value_goal:3.0f}"
                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
