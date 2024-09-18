#
# 探索
# python generate_takahashi_satoshi_system.py
#
#   ［高橋智史システム］ジェネレーター。
#   実用的な、先手先取本数、後手先取本数を求める。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import round_letro, calculate_probability, PointRuleDescription


LOG_FILE_PATH = 'output/generate_takahashi_satoshi_system.log'


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


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
            best_error = OUT_OF_ERROR
            best_balanced_black_win_rate = None
            best_b_require = 0
            best_w_require = 0

            # # 比が同じになるｎ本勝負と白のｍ勝先取のペアはスキップしたい
            # ration_set = set()

            # 計算過程
            process_list = []

            is_cutoff = False

            # p=0.5 は計算の対象外とします
            for b_require in range(1, 101):
                
                for w_require in range (1, b_require + 1):
                #for w_require in range (1, 2): # 後手に必要な先取本数を 1 に固定する場合

                    # # 先手が勝つのに必要な先取本数　＞＝　後手が勝つのに必要な先取本数。かつ、後手が勝つのに必要な先取本数が１の場合は特別
                    # if b_require <= w_require and 1 < w_require:
                    #     continue

                    balanced_black_win_rate = calculate_probability(
                        p=p,
                        H=b_require,
                        T=w_require)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    # ［最長対局数（先後固定制）］
                    #
                    #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                    #
                    max_number_of_bout_in_frozen_turn = (b_require-1) + (w_require-1) + 1


                    # より誤差が小さい組み合わせが見つかった
                    if error < best_error:

                        # しかし
                        #
                        if best_error != OUT_OF_ERROR:

                            # 先手勝率が［５０％～５４％）なら
                            #
                            #   NOTE ５１％～５５％付近を調整するには、４～１２本勝負ぐらいしないと変わらない。このあたりは調整を諦めることにする
                            #
                            if 0.5 <= p and p < 0.57:
                                # ４本勝負で調整できなければ諦める
                                if 4 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［５０％～５７％）（{p}）なら、４本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［５７％～６１％）なら
                            elif 0.57 <= p and p < 0.61:
                                # ５本勝負で調整できなければ諦める
                                if 5 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［５７％～６１％）（{p}）なら、５本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # # NOTE ６２％の前後は山ができてる地点。６本勝負にしたい

                            # 先手勝率が［６６％～６７％）なら
                            #
                            #   NOTE ６６％は山ができてる地点。５本勝負の次は、８本、１０本勝負に飛んでいる。１３本勝負ぐらいしないと互角にならないが、多いし……
                            #   ６６％  [0.1600 黒  1 白 1][0.0644 黒  2 白 1][0.0522 黒  4 白 2][0.0481 黒  6 白 3][0.0411 黒  7 白 4][0.0314 黒  9 白 5][0.0241 黒 11 白 6][0.0182 黒 13 白 7][0.0134 黒 15 白 8][0.0092 黒 17 白 9][0.0055 黒 19 白10][0.0022 黒 21 白11][0.0008 黒 23 白12][0.0006 黒 56 白29][0.0005 黒 89 白46]
                            #
                            elif 0.66 <= p and p < 0.67:
                                # １０本勝負で調整できなければ諦める
                                if 10 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［６６％～６７％）（{p}）なら、１０本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［６７％～６８％）なら
                            #
                            #   NOTE ６７％は山ができてる地点。５本勝負の次は、８本勝負に飛んでいる
                            #   ６７％  [0.1700 黒  1 白 1][0.0511 黒  2 白 1][0.0325 黒  4 白 2][0.0236 黒  6 白 3][0.0179 黒  8 白 4][0.0138 黒 10 白 5][0.0105 黒 12 白 6][0.0079 黒 14 白 7][0.0056 黒 16 白 8][0.0037 黒 18 白 9][0.0019 黒 20 白10][0.0003 黒 22 白11][0.0002 黒 89 白44]
                            #
                            elif 0.67 <= p and p < 0.68:
                                # ５本勝負で調整できなければ諦める
                                if 5 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［６７％～６８％）（{p}）なら、５本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # # # NOTE ７６％～７７％は山ができてる地点
                            # # #   ７６％  [0.2600 黒  1 白 1][0.0776 黒  2 白 1][0.0610 黒  3 白 1][0.0578 黒  5 白 2][0.0298 黒  6 白 2][0.0134 黒  9 白 3][0.0022 黒 12 白 4][0.0017 黒 31 白10][0.0014 黒 50 白16][0.0012 黒 69 白22][0.0011 黒 88 白28]
                            # # #   ７７％  [0.2700 黒  1 白 1][0.0929 黒  2 白 1][0.0435 黒  3 白 1][0.0040 黒  6 白 2][0.0014 黒 16 白 5][0.0003 黒 26 白 8]
                            # # 先手勝率が［７６％～７８％）なら
                            # elif 0.76 <= p and p < 0.78:
                            #     # ７本勝負で調整できなければ諦める
                            #     if 7 < max_number_of_bout_in_frozen_turn:
                            #         message = f"[▲！先手勝率が［７６％～７８％）（{p}）なら、７本勝負を超えるケース（{max_number_of_bout_in_frozen_turn} 黒{b_require} 白{w_require}）は、調整を諦めます]"
                            #         print(message)
                            #         process_list.append(f"{message}\n")
                            #         continue

                            # 先手勝率が［６１％～８２％）なら
                            elif 0.61 <= p and p < 0.82:
                                # ７本勝負で調整できなければ諦める
                                if 7 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［６１％～８２％）（{p}）なら、７本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # NOTE ８０％で跳ねる

                            #
                            #   NOTE ８１％は、３本勝負の次、１４本勝負に跳ねてしまう。手調整する
                            #   [0.3100 黒  1 白 1][0.1561 黒  2 白 1][0.0314 黒  3 白 1][0.0138 黒 12 白 3][0.0005 黒 16 白 4]
                            #

                            # 先手勝率が［８２％～８３％）なら
                            #
                            #   NOTE ８２％は、４本勝負の次、９本勝負に跳ねてしまう。手調整する
                            #   [0.3200 黒  1 白 1][0.1724 黒  2 白 1][0.0514 黒  3 白 1][0.0479 黒  4 白 1][0.0234 黒 13 白 3]x
                            #
                            elif 0.82 <= p and p < 0.83:
                                # ９本勝負で調整できなければ諦める
                                if 9 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［８２％～８３％）（{p}）なら、９本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［８３％～９０％）なら
                            elif 0.83 <= p and p < 0.90:
                                # １０本勝負で調整できなければ諦める
                                if 10 < max_number_of_bout_in_frozen_turn:
                                    message = f"[▲！先手勝率が［８３％～９０％）（{p}）なら、１０本勝負を超えるケース（{max_number_of_bout_in_frozen_turn}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue


                            # それ以上なら、調整する
                            else:
                                pass


                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_require = b_require
                        best_w_require = w_require

                        # 計算過程
                        process = f"[{best_error:6.4f} 黒{best_b_require:>3} 白{best_w_require:>2}]"
                        process_list.append(process)
                        print(process, end='', flush=True) # すぐ表示

                        if best_error < LIMIT_ERROR:
                            is_cutoff = True
                            print("x", end='', flush=True)
                            break

                if is_cutoff:
                    break

            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                # ［最長対局数（先後固定制）］
                #
                #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                #   NOTE 先手が１本、後手が１本取ればいいとき、最大で１本の勝負が行われる（先 or 後）から、１本勝負と呼ぶ
                #   NOTE 先手が２本、後手が１本取ればいいとき、最大で２本の勝負が行われる（先先 or 先後）から、２本勝負と呼ぶ
                #
                max_number_of_bout_in_frozen_turn = best_b_require + best_w_require - 1

                # 先手の勝ち点、後手の勝ち点、目標の勝ち点を求める
                point_rule_description = PointRuleDescription.let_points_from_require(best_b_require, best_w_require)

                text = ""
                #text += f"[{datetime.datetime.now()}]  " # タイムスタンプ

                text += f"先手勝率 {p*100:2.0f} ％ --調整後--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）    最長対局数 {max_number_of_bout_in_frozen_turn:>2}    先手勝ち{point_rule_description.b_step:2.0f}点、後手勝ち{point_rule_description.w_step:2.0f}点の{point_rule_description.target_point:3.0f}点先取制"


                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
