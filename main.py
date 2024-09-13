# python main.py
import traceback
import random

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


def n_bout(n, black_rate):
    """ｎ本勝負
    
    n はコインを振る回数。全部黒が出たら黒の勝ち、１回でも白が出れば白の勝ち。

    例えば n=1 なら、コインを最大１回振る。１勝先取で勝ち。
    n=2 なら、コインを最大２回振る。２勝先取で勝ち。白は１勝のアドバンテージが付いている。
    n=3 なら、コインを最大３回振る。３勝先取で勝ち。白は２勝のアドバンテージが付いている。
    以下同様。

    Parameters
    ----------
    n : int
        ｎ本勝負
    
    Returns
    -------
    winner_color : int
        勝った方の色
    """
    for i in range(0, n):
        if coin(black_rate) == WHITE:
            return WHITE

    return BLACK


def n_round(black_win_rate, bout_count, round_count):
    """ｎ回対局

    ｎ回対局して黒が勝った回数を返す。
    
    Parameters
    ----------
    black_win_rate : float
        黒番の勝率。例： 黒番が７割勝つなら 0.7
    bout_count : int
        ｎ本勝負。例： ３本勝負なら 3
    round_count : int
        ｎ回対局
    
    Returns
    -------
    black_win_count : int
        黒の勝った数
    """
    black_win_count = 0

    for i in range(0, round_count):
        if n_bout(bout_count, black_win_rate) == BLACK:
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
        round_count = 2_000_000

        # 0.50 ～ 0.99 まで試算
        for i in range(50, 100):
            black_win_rate = i / 100

            # （仮説）何本勝負にするかは、以下の式で求まる
            bout_count = round_letro(1/(1-black_win_rate)-1)
            print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※四捨五入")

            black_win_count = n_round(
                black_win_rate=black_win_rate,
                bout_count=bout_count,
                round_count=round_count)

            with open('result_summary.log', 'a', encoding='utf8') as f:
                text = f"先手勝率：{black_win_rate:4.02f}  {bout_count:2}本勝負×{round_count}回  調整先手勝率：{black_win_count * 100 / round_count:7.04f} ％\n"

                f.write(text)
                print(text, end='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
