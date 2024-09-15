#
# 共通コード
#

import random
import datetime

# 四捨五入 📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)
from decimal import Decimal, ROUND_HALF_UP


# 黒。先手
BLACK = 1

# 白。後手
WHITE = 2


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


def count_of_decimal_places(value):
    """小数部の桁数を取得
    
    Parameters
    ----------
    value : float
        浮動小数点数
    """
    if not isinstance(value, float):
        raise ValueError(f"{value} is not float. {type(value)}")
    
    # 文字列表現
    s = str(value)
    # 小数点の位置
    i = s.find('.')
    if i < 0:
        return 0
    # 小数部の文字列
    s = s[i+1:]
    return len(s)


def white_win_rate(black_win_rate):
    """後手勝率
    
    Parameters
    ----------
    black_win_rate : float
        先手勝率
    """
    return 1 - black_win_rate


def black_win_value(white_win_rate):
    """先手の勝ちの価値
    
    Parameters
    ----------
    white_win_rate : float
        後手勝率
    """
    return white_win_rate / (1 - white_win_rate)


def white_win_value(black_win_rate):
    """後手の勝ちの価値
    
    Parameters
    ----------
    black_win_rate : float
        先手勝率
    """
    return black_win_rate / (1 - black_win_rate)


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


class CoinToss():
    """コイントスの試行"""


    def __init__(self, summary_file_path):
        """初期化
        
        Parameters
        ----------
        summary_file_path : str
            結果の出力ファイルへのパス
        """
        self._summary_file_path = summary_file_path


    def coin_toss_in_some_rounds(self, black_win_rate, black_target_in_bout, white_target_in_bout, round_total):
        """コイントスを複数対局する
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        black_target_in_bout : int
            先手の何本先取制
        white_target_in_bout : int
            後手の何本先取制
        round_total : int
            対局数
        """

        # 初期値
        # ------

        # 黒が勝った回数
        black_wons = 0


        for round in range(0, round_total):

            # 新しい本目（Bout）
            b_count_in_bout = 0
            w_count_in_bout = 0

            # ｎ本勝負で勝ち負けが出るまでやる
            while True:

                # 黒が出た
                if coin(black_win_rate) == BLACK:
                    b_count_in_bout += 1
                
                # 白が出た
                else:
                    w_count_in_bout += 1

                # 黒の先取本数を取った（黒が勝った）
                if black_target_in_bout <= b_count_in_bout:
                    black_wons += 1
                    break

                # 白の先取本数を取った（白が勝った）
                elif white_target_in_bout <= w_count_in_bout:
                    break


        with open(self._summary_file_path, 'a', encoding='utf8') as f:
            # 文言作成
            # -------

            # 黒が勝った確率
            black_won_rate = black_wons / round_total

            # 均等からの誤差
            error = abs(black_won_rate - 0.5)

            text = f"[{datetime.datetime.now()}]  先手勝率：{black_win_rate:4.02f}  先手{black_target_in_bout:2}本先取/後手{white_target_in_bout:2}本先取制  先手勝ち数{black_wons:7}／{round_total:7}対局試行  先手が勝った確率{black_won_rate*100:8.4f} ％  誤差{error*100:8.4f} ％"
            print(text) # 表示
            f.write(f"{text}\n")    # ファイルへ出力
