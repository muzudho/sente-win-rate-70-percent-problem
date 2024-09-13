# python main.py
import traceback
import random
import math

# 四捨五入 📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)
from decimal import Decimal, getcontext, ROUND_HALF_UP

# 黒。先手
BLACK = 1

# 白。後手
WHITE = 2


def coin(black_rate):
    """表が黒、裏が白のコイン

    Parameters
    ----------
    black_rate : float
        黒が出る確率。例： 黒が７割出るなら 0.7
    """
    if random.random() < black_rate:
        return BLACK
    return WHITE


def n_bout(n, black_rate, white_require):
    """ｎ本勝負
    
    n はコインを振る回数。全部黒が出たら黒の勝ち、white_require 回白が出れば白の勝ち。

    例えば n=1 なら、コインを最大１回振る。１勝先取で勝ち。
    n=2 なら、コインを最大２回振る。２勝先取で勝ち。白は１勝のアドバンテージが付いている。
    n=3 なら、コインを最大３回振る。３勝先取で勝ち。白は２勝のアドバンテージが付いている。
    以下同様。

    Parameters
    ----------
    n : int
        ｎ本勝負
    black_rate : float
        黒番の勝率。例： 黒番の勝率が７割なら 0.7
    white_require : int
        白が勝つのに必要な番数
    
    Returns
    -------
    winner_color : int
        勝った方の色
    """
    white_count_down = white_require

    for i in range(0, n):
        if coin(black_rate) == WHITE:
            white_count_down -= 1
            if white_count_down < 1:
                return WHITE

    return BLACK


def n_round(black_win_rate, bout_count, white_require, round_count):
    """ｎ回対局

    ｎ回対局して黒が勝った回数を返す。
    
    Parameters
    ----------
    black_win_rate : float
        黒番の勝率。例： 黒番が７割勝つなら 0.7
    bout_count : int
        ｎ本勝負。例： ３本勝負なら 3
    white_require : int
        白が勝つのに必要な番数
    round_count : int
        ｎ回対局
    
    Returns
    -------
    black_win_count : int
        黒の勝った数
    """
    black_win_count = 0

    for i in range(0, round_count):
        if n_bout(bout_count, black_win_rate, white_require) == BLACK:
            black_win_count += 1

    return black_win_count


def round_letro(number):
    """四捨五入

    📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)

    Parameters
    ----------
    number : float
        四捨五入したい数
    
    Returns
    -------
    answer : int
        整数
    """
    return int(Decimal(str(number)).quantize(Decimal('0'), ROUND_HALF_UP))


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        # 0.50 ～ 0.99 まで試算
        rule_list = [
            # black_win_rate, best_bout_count, best_white_require
            # -----------------------------------------
            # 人の目で見て十分だと思ったら、best_bout_count と best_white_require を 0 以外にすること
            [0.50,  0,  0],
            [0.51,  0,  0],
            [0.52,  0,  0],
            [0.53,  0,  0],
            [0.54,  0,  0],
            [0.55,  0,  0],
            [0.56,  0,  0],
            [0.57,  0,  0],
            [0.58,  0,  0],
            [0.59,  0,  0],
            [0.60,  0,  0],
            [0.61,  0,  0],
            [0.62,  0,  0],
            [0.63,  0,  0],
            [0.64,  0,  0],
            [0.65,  0,  0],
            [0.66,  0,  0],
            [0.67,  0,  0],
            [0.68,  0,  0],
            [0.69,  0,  0],
            [0.70,  0,  0],
            [0.71,  0,  0],
            [0.72,  0,  0],
            [0.73,  0,  0],
            [0.74,  0,  0],
            [0.75,  0,  0],
            [0.76,  0,  0],
            [0.77,  0,  0],
            [0.78,  0,  0],
            [0.79,  0,  0],
            [0.80,  0,  0],
            [0.81,  0,  0],
            [0.82,  0,  0],
            [0.83,  0,  0],
            [0.84,  0,  0],
            [0.85,  0,  0],
            [0.86,  0,  0],
            [0.87,  0,  0],
            [0.88,  0,  0],
            [0.89,  0,  0],
            [0.90,  0,  0],
            [0.91,  0,  0],
            [0.92,  0,  0],
            [0.93,  0,  0],
            [0.94,  0,  0],
            [0.95,  0,  0],
            [0.96,  0,  0],
            [0.97,  0,  0],
            [0.98,  0,  0],
            [0.99,  0,  0],
        ]

        for rule in rule_list:
            black_win_rate=rule[0]
            best_bout_count=rule[1]
            best_white_require=rule[2]
            is_automatic = best_bout_count == 0 or best_white_require == 0

            # （仮説）何本勝負にするかは、以下の式で求まる
            # bout_count = round_letro(1/(1-black_win_rate)-1)
            # print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下四捨五入")
            # bout_count = math.floor(1/(1-black_win_rate)-1)
            # print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下切り捨て")
            #bout_count = math.ceil(1/(1-black_win_rate)-1)
            #print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下切り上げ")

            # 途中の計算式
            calculation_list = []

            # best_bout_count と best_white_require が未設定なら、アルゴリズムで求めることにする
            if is_automatic:
                best_black_win_count = 0
                best_bout_count = 0
                best_white_require = 0
                round_count = 20_000

                # 誤差は 0.01 に接近するほどベスト。勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
                # 0.01 未満からさらに 0 に近づいていくので、そうなる前に打ち切る
                LIMIT = 0.01
                OUT_OF_ERROR = 0.51
                best_black_win_error = OUT_OF_ERROR

                is_cutoff = False

                for bout_count in range(1, 10):

                    # １本勝負のときだけ、白はｎ本－１ではない
                    if bout_count == 1:
                        end_white_require = 2
                    else:
                        end_white_require = bout_count

                    for white_require in range(1, end_white_require):

                        black_win_count = n_round(
                            black_win_rate=black_win_rate,
                            bout_count=bout_count,
                            white_require=white_require,
                            round_count=round_count)
                        
                        #print(f"{black_win_count=}  {round_count=}  {black_win_count / round_count=}")
                        black_win_error = abs(black_win_count / round_count - 0.5)

                        if best_black_win_error != OUT_OF_ERROR and black_win_error < LIMIT:
                            is_cutoff = True

                            # 進捗バー
                            print('x', end='')

                            break

                        if black_win_error < best_black_win_error:
                            best_black_win_count = black_win_count
                            best_black_win_error = black_win_error
                            best_bout_count = bout_count
                            best_white_require = white_require
                        
                            # 進捗バー（更新時）
                            text = f'[{black_win_error:6.4f}]'
                            calculation_list.append(text)
                            print(text, end='')

                    if is_cutoff:
                        break

                    # 進捗バー
                    print('.', end='')
                print() # 改行

            # best_bout_count と best_white_require が設定されていれば、より細かく確率を求める
            else:
                round_count = 2_000_000

                best_black_win_count = n_round(
                    black_win_rate=black_win_rate,
                    bout_count=best_bout_count,
                    white_require=best_white_require,
                    round_count=round_count)

                best_black_win_error = abs(best_black_win_count / round_count - 0.5)


            with open('result_summary.log', 'a', encoding='utf8') as f:
                # 計算未完了
                if best_black_win_error == OUT_OF_ERROR:
                    text = f"先手勝率：{black_win_rate:4.02f}  （計算未完了）  {is_automatic=}  {''.join(calculation_list)}\n"
                
                # 計算可能
                else:
                    text = f"先手勝率：{black_win_rate:4.02f}  {best_bout_count:2}本勝負×{round_count}回  白{best_white_require:2}先取制  調整先手勝率：{best_black_win_count * 100 / round_count:>7.04f} ％  {is_automatic=}  {''.join(calculation_list)}\n"

                f.write(text)
                print(text, end='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
