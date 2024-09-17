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

            # # 比が同じになるｎ本勝負と白のｍ勝先取のペアはスキップしたい
            # ration_set = set()

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
                    
                    # # NOTE strict の方で ration 使ってないので合わせる
                    # # NOTE ［先手が勝つのに必要な先取本数が４，後手が勝つのに必要な先取本数が２］というのは、［先手が勝つのに必要な先取本数が２，後手が勝つのに必要な先取本数が１］と同じように見えるが、均等に近づく精度が上がる
                    # #
                    # #   同じ比はスキップ。１００００倍（１００×１００程度を想定）して小数点以下四捨五入
                    # #
                    # ration = round_letro(w_point / b_point * 10000)

                    # if ration in ration_set:
                    #     continue

                    # ration_set.add(ration)


                    balanced_black_win_rate = calculate_probability(
                        p=black_win_rate,
                        H=b_point,
                        T=w_point)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    # 最大ｎ本勝負
                    #
                    #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                    #
                    max_bout_count = b_point + w_point - 1


                    # より誤差が小さい組み合わせが見つかった
                    if error < best_error:

                        # しかし
                        #
                        if best_error != OUT_OF_ERROR:

                            # 先手勝率が［５０％～５４％）なら
                            #
                            #   NOTE ５１％～５５％付近を調整するには、４～１２本勝負ぐらいしないと変わらない。このあたりは調整を諦めることにする
                            #
                            if 0.5 <= black_win_rate and black_win_rate < 0.57:
                                # ４本勝負で調整できなければ諦める
                                if 4 < max_bout_count:
                                    message = f"[▲！先手勝率が［５０％～５７％）（{black_win_rate}）なら、４本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［５７％～６１％）なら
                            elif 0.57 <= black_win_rate and black_win_rate < 0.61:
                                # ５本勝負で調整できなければ諦める
                                if 5 < max_bout_count:
                                    message = f"[▲！先手勝率が［５７％～６１％）（{black_win_rate}）なら、５本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # # NOTE ６２％の前後は山ができてる地点。６本勝負にしたい

                            # 先手勝率が［６６％～６７％）なら
                            #
                            #   NOTE ６６％は山ができてる地点。５本勝負の次は、８本、１０本勝負に飛んでいる。１３本勝負ぐらいしないと互角にならないが、多いし……
                            #   ６６％  [0.1600 黒  1 白 1][0.0644 黒  2 白 1][0.0522 黒  4 白 2][0.0481 黒  6 白 3][0.0411 黒  7 白 4][0.0314 黒  9 白 5][0.0241 黒 11 白 6][0.0182 黒 13 白 7][0.0134 黒 15 白 8][0.0092 黒 17 白 9][0.0055 黒 19 白10][0.0022 黒 21 白11][0.0008 黒 23 白12][0.0006 黒 56 白29][0.0005 黒 89 白46]
                            #
                            elif 0.66 <= black_win_rate and black_win_rate < 0.67:
                                # １０本勝負で調整できなければ諦める
                                if 10 < max_bout_count:
                                    message = f"[▲！先手勝率が［６６％～６７％）（{black_win_rate}）なら、１０本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［６７％～６８％）なら
                            #
                            #   NOTE ６７％は山ができてる地点。５本勝負の次は、８本勝負に飛んでいる
                            #   ６７％  [0.1700 黒  1 白 1][0.0511 黒  2 白 1][0.0325 黒  4 白 2][0.0236 黒  6 白 3][0.0179 黒  8 白 4][0.0138 黒 10 白 5][0.0105 黒 12 白 6][0.0079 黒 14 白 7][0.0056 黒 16 白 8][0.0037 黒 18 白 9][0.0019 黒 20 白10][0.0003 黒 22 白11][0.0002 黒 89 白44]
                            #
                            elif 0.67 <= black_win_rate and black_win_rate < 0.68:
                                # ５本勝負で調整できなければ諦める
                                if 5 < max_bout_count:
                                    message = f"[▲！先手勝率が［６７％～６８％）（{black_win_rate}）なら、５本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # # # NOTE ７６％～７７％は山ができてる地点
                            # # #   ７６％  [0.2600 黒  1 白 1][0.0776 黒  2 白 1][0.0610 黒  3 白 1][0.0578 黒  5 白 2][0.0298 黒  6 白 2][0.0134 黒  9 白 3][0.0022 黒 12 白 4][0.0017 黒 31 白10][0.0014 黒 50 白16][0.0012 黒 69 白22][0.0011 黒 88 白28]
                            # # #   ７７％  [0.2700 黒  1 白 1][0.0929 黒  2 白 1][0.0435 黒  3 白 1][0.0040 黒  6 白 2][0.0014 黒 16 白 5][0.0003 黒 26 白 8]
                            # # 先手勝率が［７６％～７８％）なら
                            # elif 0.76 <= black_win_rate and black_win_rate < 0.78:
                            #     # ７本勝負で調整できなければ諦める
                            #     if 7 < max_bout_count:
                            #         message = f"[▲！先手勝率が［７６％～７８％）（{black_win_rate}）なら、７本勝負を超えるケース（{max_bout_count} 黒{b_point} 白{w_point}）は、調整を諦めます]"
                            #         print(message)
                            #         process_list.append(f"{message}\n")
                            #         continue

                            # 先手勝率が［６１％～８２％）なら
                            elif 0.61 <= black_win_rate and black_win_rate < 0.82:
                                # ７本勝負で調整できなければ諦める
                                if 7 < max_bout_count:
                                    message = f"[▲！先手勝率が［６１％～８２％）（{black_win_rate}）なら、７本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
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
                            elif 0.82 <= black_win_rate and black_win_rate < 0.83:
                                # ９本勝負で調整できなければ諦める
                                if 9 < max_bout_count:
                                    message = f"[▲！先手勝率が［８２％～８３％）（{black_win_rate}）なら、９本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［８３％～９０％）なら
                            elif 0.83 <= black_win_rate and black_win_rate < 0.90:
                                # １０本勝負で調整できなければ諦める
                                if 10 < max_bout_count:
                                    message = f"[▲！先手勝率が［８３％～９０％）（{black_win_rate}）なら、１０本勝負を超えるケース（{max_bout_count}）は、調整を諦めます]"
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

                # 最大ｎ本勝負
                #
                #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
                #
                max_bout_count = best_b_point + best_w_point - 1

                # 後手がアドバンテージを持っているという表記に変更
                w_advantage = best_b_point - best_w_point

                text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％ --調整--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）  {max_bout_count:>2}本勝負（ただし、{best_b_point:>2}本先取制。後手は最初から {w_advantage:>2} 本持つアドバンテージ）"
                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
