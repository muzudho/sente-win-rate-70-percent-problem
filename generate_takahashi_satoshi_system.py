#
# 探索
# python generate_takahashi_satoshi_system.py
#
#   ［高橋智史システム］ジェネレーター。
#   実用的な、先後固定制での［黒勝ちだけでの対局数］、［白勝ちだけでの対局数］を求める。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import round_letro, calculate_probability, PointsConfiguration
from views import stringify_when_generate_takahashi_satoshi_system


LOG_FILE_PATH = 'output/generate_takahashi_satoshi_system.log'
CSV_FILE_PATH_P = "./data/p.csv"
CSV_FILE_PATH_TSS = './data/takahashi_satoshi_system.csv'


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")
        df_tss = pd.read_csv(CSV_FILE_PATH_TSS, encoding="utf8")

        # 先手勝率
        for p in df['p']:

            # ベストな調整後の先手勝率と、その誤差
            best_new_p_error = OUT_OF_ERROR
            best_new_p = None
            best_b_time = 0
            best_w_time = 0

            # 計算過程
            process_list = []

            is_cutoff = False

            # ［黒勝ちだけでの対局数］
            for b_time in range(1, 101):
                
                # ［白勝ちだけでの対局数］
                for w_time in range (1, b_time + 1):
                #for w_time in range (1, 2): # ［黒勝ちだけでの対局数］を 1 に固定する場合

                    # # ［黒勝ちだけでの対局数］　＞＝　［白勝ちだけでの対局数］。かつ、［白勝ちだけでの対局数］が１の場合は特別
                    # if b_time <= w_time and 1 < w_time:
                    #     continue

                    points_configuration = PointsConfiguration.let_points_from_repeat(b_time, w_time)

                    # ［調整後の表が出る確率（％）］
                    new_p = calculate_probability(      # 表側のプレイヤー（Ａさん）の、勝つ確率
                            p=p,                        # 表が出る割合
                            H=b_time,                 # 表側のプレイヤーの、これだけ表が出れば勝ち、という数
                            T=w_time)                 # 裏側のプレイヤーの、これだけ裏が出れば勝ち、という数

                    #
                    # NOTE ［先後交互制］での H と T はどう考える？ ----> ［表が出る確率］というのは変わらない。ＡさんとＢさんたちが先後を入れ替えて回ってるだけで。
                    #

                    # 誤差
                    new_p_error = abs(new_p - 0.5)

                    # ［最長対局数］
                    number_of_longest_bout = points_configuration.let_number_of_longest_bout_when_frozen_turn()


                    # より誤差が小さい組み合わせが見つかった
                    if new_p_error < best_new_p_error:

                        # しかし
                        #
                        if best_new_p_error != OUT_OF_ERROR:

                            # 先手勝率が［５０％～５４％）なら
                            #
                            #   NOTE ５１％～５５％付近を調整するには、４～１２本勝負ぐらいしないと変わらない。このあたりは調整を諦めることにする
                            #
                            if 0.5 <= p and p < 0.57:
                                # ４本勝負で調整できなければ諦める
                                if 4 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［５０％～５７％）（{p}）なら、４本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［５７％～６１％）なら
                            elif 0.57 <= p and p < 0.61:
                                # ５本勝負で調整できなければ諦める
                                if 5 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［５７％～６１％）（{p}）なら、５本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
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
                                if 10 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［６６％～６７％）（{p}）なら、１０本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
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
                                if 5 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［６７％～６８％）（{p}）なら、５本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # # # NOTE ７６％～７７％は山ができてる地点
                            # # #   ７６％  [0.2600 黒  1 白 1][0.0776 黒  2 白 1][0.0610 黒  3 白 1][0.0578 黒  5 白 2][0.0298 黒  6 白 2][0.0134 黒  9 白 3][0.0022 黒 12 白 4][0.0017 黒 31 白10][0.0014 黒 50 白16][0.0012 黒 69 白22][0.0011 黒 88 白28]
                            # # #   ７７％  [0.2700 黒  1 白 1][0.0929 黒  2 白 1][0.0435 黒  3 白 1][0.0040 黒  6 白 2][0.0014 黒 16 白 5][0.0003 黒 26 白 8]
                            # # 先手勝率が［７６％～７８％）なら
                            # elif 0.76 <= p and p < 0.78:
                            #     # ７本勝負で調整できなければ諦める
                            #     if 7 < number_of_longest_bout:
                            #         message = f"[▲！先手勝率が［７６％～７８％）（{p}）なら、７本勝負を超えるケース（{number_of_longest_bout} 黒{b_time} 白{w_time}）は、調整を諦めます]"
                            #         print(message)
                            #         process_list.append(f"{message}\n")
                            #         continue

                            # 先手勝率が［６１％～８２％）なら
                            elif 0.61 <= p and p < 0.82:
                                # ７本勝負で調整できなければ諦める
                                if 7 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［６１％～８２％）（{p}）なら、７本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
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
                                if 9 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［８２％～８３％）（{p}）なら、９本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue

                            # 先手勝率が［８３％～９０％）なら
                            elif 0.83 <= p and p < 0.90:
                                # １０本勝負で調整できなければ諦める
                                if 10 < number_of_longest_bout:
                                    message = f"[▲！先手勝率が［８３％～９０％）（{p}）なら、１０本勝負を超えるケース（{number_of_longest_bout}）は、調整を諦めます]"
                                    print(message)
                                    process_list.append(f"{message}\n")
                                    continue


                            # それ以上なら、調整する
                            else:
                                pass


                        best_new_p_error = new_p_error
                        best_new_p = new_p
                        best_b_time = b_time
                        best_w_time = w_time

                        # 計算過程
                        process = f"[{best_new_p_error:6.4f} 黒{best_b_time:>3} 白{best_w_time:>2}]"
                        process_list.append(process)
                        print(process, end='', flush=True) # すぐ表示

                        if best_new_p_error < LIMIT_ERROR:
                            is_cutoff = True
                            print("x", end='', flush=True)
                            break

                if is_cutoff:
                    break

            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言の作成
                text = stringify_when_generate_takahashi_satoshi_system(p, best_new_p, best_new_p_error, best_b_time, best_w_time)

                print(text) # 表示

                # # 計算過程を追加する場合
                # text += f"  {''.join(process_list)}"

                f.write(f"{text}\n")    # ログファイルへ出力


            # データフレーム更新
            # -----------------

            # ［黒勝ちだけでの対局数（先後固定制）］列を更新
            df_tss['b_time'].astype('int')   # NOTE 初期値が float なので、 int 型へ変更
            df_tss.loc[df['p']==p, ['b_time']] = best_b_time

            # ［白勝ちだけでの対局数（先後固定制）］列を更新
            df_tss['w_time'].astype('int')   # NOTE 初期値が float なので、 int 型へ変更
            df_tss.loc[df['p']==p, ['w_time']] = best_w_time


        # CSV保存
        df_tss.to_csv(CSV_FILE_PATH_TSS,
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
