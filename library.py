#
# 共通コード
#
#   ファイル出力、ログ等を除く
#

import random
from fractions import Fraction

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


def scale_for_float_to_int(value):
    """小数部を持つ数を、小数部を持たないようにするのに必要な１０の倍数"""
    # 小数部の桁数
    dp_len = count_of_decimal_places(value)
    #print(f"小数部の桁数{dp_len}  ", end="")

    return 10**dp_len


# def white_win_rate(black_win_rate):
#     """後手勝率
#
#     NOTE 0.11 が 0.10999999999999999 になっていたり、想定した結果を返さないことがあるから使わないほうがいい
#
#     Parameters
#     ----------
#     black_win_rate : float
#         先手勝率
#     """
#     return 1 - black_win_rate


def black_win_rate_to_b_w_targets(p):
    """表が出る確率 p を与えると、表取得本数、裏取得本数を返す
    
    Parameters
    ----------
    p : float
        表が出る確率
    
    Returns
    -------
    p_point : int
        表取得本数
    q_point : int
        裏取得本数
    """

    # 説明２  コインの表裏の確率の整数化
    # --------------------------------
    scale = scale_for_float_to_int(p)

    # 黒先取本数基礎
    #
    #   NOTE int() を使って小数点以下切り捨てしようとすると、57 が 56 になったりするので、四捨五入にする
    #
    b_point = round_letro(p * scale)

    # 白先取本数基礎
    w_point = scale - b_point

    # 約分する
    fraction = Fraction(b_point, w_point)
    return fraction.numerator, fraction.denominator


# def black_win_value(white_win_rate):
#     """先手の勝ちの価値
#
#     Parameters
#     ----------
#     white_win_rate : float
#         後手勝率
#     """
#     return white_win_rate / (1 - white_win_rate)


# def white_win_value(black_win_rate):
#     """後手の勝ちの価値
#
#     Parameters
#     ----------
#     black_win_rate : float
#         先手勝率
#     """
#     return black_win_rate / (1 - black_win_rate)


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


    def __init__(self, output_file_path):
        """初期化
        
        Parameters
        ----------
        output_file_path : str
            出力先ファイルへのパス
        """
        self._output_file_path = output_file_path


    @property
    def output_file_path(self):
        """出力先ファイルへのパス"""
        return self._output_file_path


    def coin_toss_in_round(self, black_win_rate, b_point, w_point):
        """１対局行う
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        b_point : int
            先手の何本先取制
        w_point : int
            後手の何本先取制
        """

        # 新しい本目（Bout）
        b_count_in_bout = 0
        w_count_in_bout = 0

        # ｎ本勝負で勝ち負けが出るまでやる
        while True:

            # 黒が出た
            if coin(black_win_rate) == BLACK:
                b_count_in_bout += 1

                # 黒の先取本数を取った（黒が勝った）
                if b_point <= b_count_in_bout:
                    return BLACK

            # 白が出た
            else:
                w_count_in_bout += 1

                # 白の先取本数を取った（白が勝った）
                if w_point <= w_count_in_bout:
                    return WHITE

            # 続行


    def coin_toss_in_some_rounds(self, black_win_rate, b_point, w_point, round_total):
        """コイントスを複数対局する
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        b_point : int
            先手の何本先取制
        w_point : int
            後手の何本先取制
        round_total : int
            対局数
        
        Returns
        -------
        black_wons : int
            黒が勝った回数
        """

        # 初期値
        # ------

        # 黒が勝った回数
        black_wons = 0


        for round in range(0, round_total):

            if self.coin_toss_in_round(black_win_rate, b_point, w_point) == BLACK:
                black_wons += 1

        return black_wons


def calculate_probability(p, H, T):
    """TODO このコードは検証中
    Ａさんが勝つ確率を返します

    Ａさんが勝つ条件：　表が H 回出る前に裏が T 回出ないこと
    試行回数の考え方：　ゲームは最小で H 回、最大で N = H + T - 1 回のコイン投げで終了します
    確率の計算：　総試行回数 N 回で、表が H 回以上出る確率を計算します

    # パラメータの設定例
    p = 0.7  # 表が出る確率
    H = 7    # Aさんが必要な表の回数
    T = 3    # Bさんが必要な裏の回数

    # 計算の実行例
    probability = calculate_probability(p, H, T)
    print(f"Aさんが勝つ確率: {probability * 100:.2f}%")

    Parameters
    ----------
    p : float
        表が出る確率
    H : int
        表側のプレイヤー（Ａさん）が必要な、表の先取回数
    T : int
        裏側のプレイヤー（Ｂさん）が必要な、裏の先取回数
    
    Returns
    black_win_rate : float
        Ａさんが勝つ確率
    """

    from math import comb

    # 裏が出る確率
    q = 1 - p

    # 試行回数
    N = H + T - 1

    # Ａさんが勝つ確率を初期化
    probability = 0.0

    # 表が H 回から N 回出る確率を計算
    for n in range(H, N + 1):
        # 📖 ［累計二項分布］を調べること
        combinations = comb(N, n)   # 組み合わせの数
        prob = combinations * (p ** n) * (q ** (N - n))
        probability += prob

    return probability
