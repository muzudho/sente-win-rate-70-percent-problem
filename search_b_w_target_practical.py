#
# 探索
# python search_b_w_target_practical.py
#
#   実用的な、先手先取本数、後手先取本数を求める
#

import traceback
import datetime
import random
import math

from library import round_letro, calculate_probability


SUMMARY_FILE_PATH = 'output/search_b_w_target_practical.log'


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


# 0.50 <= p and p <= 0.99
INPUT_DATA = [
    [0.50],
    [0.51],
    [0.52],
    [0.53],
    [0.54],
    [0.55],
    [0.56],
    [0.57],
    [0.58],
    [0.59],
    [0.60],
    [0.61],
    [0.62],
    [0.63],
    [0.64],
    [0.65],
    [0.66],
    [0.67],
    [0.68],
    [0.69],
    [0.70],
    [0.71],
    [0.72],
    [0.73],
    [0.74],
    [0.75],
    [0.76],
    [0.77],
    [0.78],
    [0.79],
    [0.80],
    [0.81],
    [0.82],
    [0.83],
    [0.84],
    [0.85],
    [0.86],
    [0.87],
    [0.88],
    [0.89],
    [0.90],
    [0.91],
    [0.92],
    [0.93],
    [0.94],
    [0.95],
    [0.96],
    [0.97],
    [0.98],
    [0.99],
]


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            # 先手勝率
            black_win_rate=input_datum[0]

            # ベストな調整後の先手勝率と、その誤差
            best_error = OUT_OF_ERROR
            best_balanced_black_win_rate = None
            best_b_point = 0
            best_w_point = 0

            # 比が同じになるｎ本勝負と白のｍ勝先取のペアはスキップしたい
            ration_set = set()

            # 計算過程
            process_list = []

            is_cutoff = False

            # p=0.5 は計算の対象外とします
            for b_point in range(1, 101):
                
                for w_point in range (1, b_point + 1):
                #for w_point in range (1, 2): # 後手に必要な先取本数を 1 に固定する場合

                    # # 先手が勝つのに必要な先取本数　＞＝　後手が勝つのに必要な先取本数。かつ、後手が勝つのに必要な先取本数が１の場合は特別
                    # if b_point <= w_point and 1 < w_point:
                    #     continue
                    
                    # NOTE ［先手が勝つのに必要な先取本数が４，後手が勝つのに必要な先取本数が２］というのは、［先手が勝つのに必要な先取本数が２，後手が勝つのに必要な先取本数が１］と同じように見えるが、均等に近づく精度が上がる
                    #
                    #   同じ比はスキップ。１００００倍（１００×１００程度を想定）して小数点以下四捨五入
                    #
                    ration = round_letro(w_point / b_point * 10000)

                    if ration in ration_set:
                        continue

                    ration_set.add(ration)


                    balanced_black_win_rate = calculate_probability(
                        p=black_win_rate,
                        H=b_point,
                        T=w_point)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    # ｎ本勝負
                    bout_count = b_point + w_point - 1


                    # より誤差が小さい組み合わせが見つかった
                    if error < best_error:

                        # しかし
                        #
                        if best_error != OUT_OF_ERROR:

                            # 先手勝率が［５０％～５４％）なら
                            if 0.5 <= black_win_rate and black_win_rate < 0.54:
                                # １本勝負で調整できなければ諦める
                                if 1 < bout_count:
                                    message = f"[▲！先手勝率が［５０％～５４％）（{black_win_rate}）なら、１本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue


                            # 先手勝率が［５４％～５７％）なら
                            elif 0.54 <= black_win_rate and black_win_rate < 0.57:
                                # ３本勝負で調整できなければ諦める
                                if 3 < bout_count:
                                    message = f"[▲！先手勝率が［５４％～５７％）（{black_win_rate}）なら、３本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue


                            # 先手勝率が［５７％～６５％）なら
                            elif 0.57 <= black_win_rate and black_win_rate < 0.65:
                                # ５本勝負で調整できなければ諦める
                                if 5 < bout_count:
                                    message = f"[▲！先手勝率が［５７％～６５％）（{black_win_rate}）なら、５本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # NOTE ６２％の前後は山ができてる地点

                            # 先手勝率が［６５％～８２％）なら
                            elif 0.65 <= black_win_rate and black_win_rate < 0.82:
                                # ７本勝負で調整できなければ諦める
                                if 7 < bout_count:
                                    message = f"[▲！先手勝率が［６５％～８２％）（{black_win_rate}）なら、７本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # NOTE ８０％で跳ねる

                            # NOTE ８２％は、４本勝負の次、１３本勝負に跳ねてしまう。手調整する
                            #
                            #   [0.3200 黒  1 白 1][0.1724 黒  2 白 1][0.0514 黒  3 白 1][0.0479 黒  4 白 1][0.0234 黒 13 白 3]x
                            #
                            elif 0.82 <= black_win_rate and black_win_rate < 0.83:
                                # １２本勝負で調整できなければ諦める
                                if 12 < bout_count:
                                    message = f"[▲！先手勝率が［８２％～８３％）（{black_win_rate}）なら、１２本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［８３％～９０％）なら
                            elif 0.83 <= black_win_rate and black_win_rate < 0.90:
                                # １０本勝負で調整できなければ諦める
                                if 10 < bout_count:
                                    message = f"[▲！先手勝率が［８３％～９０％）（{black_win_rate}）なら、１０本勝負を超えるケース（{bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue


                            # それ以上なら、調整する
                            else:
                                pass


                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_point = b_point
                        best_w_point = w_point

                        # 計算過程
                        process = f"[{best_error:6.4f} 黒{best_b_point:>3} 白{best_w_point:>2}]"
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


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                # 後手がアドバンテージを持っているという表記に変更
                w_advantage = best_b_point - best_w_point

                text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％ --調整--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）  {best_b_point:>2}本勝負（後手は最初から {w_advantage:>2} 本持つアドバンテージ）"
                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
