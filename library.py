#
# 共通コード
#
#   ファイル出力、ログ等を除く
#

import random
import math
from fractions import Fraction

# 四捨五入 📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)
from decimal import Decimal, ROUND_HALF_UP


# 黒。表。先手
BLACK = 1

# 白。裏。後手
WHITE = 2

# Ａさん。配列のインデックスに使う    NOTE 黒白と混同しないように注意
ALICE = 1

# Ｂさん。配列のインデックスに使う
BOB = 2


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
    b_repeat_when_frozen_turn = round_letro(p * scale)

    # 白先取本数基礎
    w_repeat_when_frozen_turn = scale - b_repeat_when_frozen_turn

    # 約分する
    fraction = Fraction(b_repeat_when_frozen_turn, w_repeat_when_frozen_turn)
    return fraction.numerator, fraction.denominator


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


def n_bout_when_frozen_turn(black_rate, max_number_of_bout, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn):
    """先後固定制で、最長で max_number_of_bout 回の対局を行い、勝った方の手番を返します

    NOTE 白番はずっと白番、黒番はずっと黒番とします。手番を交代しません

    max_number_of_bout はコインを振る回数。全部黒が出たら黒の勝ち、 w_repeat_when_frozen_turn 回白が出れば白の勝ち。

    例えば n=1 なら、コインを最大１回振る。１勝先取で勝ち。
    n=2 なら、コインを最大２回振る。２勝先取で勝ち。白は１勝のアドバンテージが付いている。
    n=3 なら、コインを最大３回振る。３勝先取で勝ち。白は２勝のアドバンテージが付いている。
    以下同様。

    Parameters
    ----------
    black_rate : float
        黒番の勝率。例： 黒番の勝率が７割なら 0.7
    max_number_of_bout : int
        最長の対局数
    b_repeat_when_frozen_turn : int
        黒が勝つのに必要な一本の数
    w_repeat_when_frozen_turn : int
        白が勝つのに必要な一本の数
    
    Returns
    -------
    winner_color : int
        勝った方の色
    """
    black_count_down = b_repeat_when_frozen_turn
    white_count_down = w_repeat_when_frozen_turn

    for i in range(0, max_number_of_bout):
        if coin(black_rate) == WHITE:
            white_count_down -= 1
            if white_count_down < 1:
                return WHITE    # 白が勝ちぬけ
        else:
            black_count_down -= 1
            if black_count_down < 1:
                return BLACK    # 黒が勝ちぬけ

    raise ValueError(f"決着が付かずにループを抜けたからエラー  {black_rate=}  {max_number_of_bout=}  {b_repeat_when_frozen_turn=}  {w_repeat_when_frozen_turn=}")


def n_round_when_frozen_turn(black_win_rate, max_number_of_bout_when_frozen_turn, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn, round_count):
    """［最長対局数（先後固定制）］の中で対局

    ｎ回対局して黒が勝った回数を返す。
    
    Parameters
    ----------
    black_win_rate : float
        黒番の勝率。例： 黒番が７割勝つなら 0.7
    max_number_of_bout_when_frozen_turn : int
        ［最長対局数（先後固定制）］。例： ３本勝負なら 3
    b_repeat_when_frozen_turn : int
        黒が勝つのに必要な一本の数
    w_repeat_when_frozen_turn : int
        白が勝つのに必要な一本の数
    round_count : int
        ｎ回対局
    
    Returns
    -------
    black_win_count : int
        黒の勝った数
    """
    black_win_count = 0

    for i in range(0, round_count):
        if n_bout_when_frozen_turn(black_win_rate, max_number_of_bout_when_frozen_turn, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn) == BLACK:
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


    def coin_toss_in_round(self, black_win_rate, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn):
        """１対局行う（どちらの勝ちが出るまでコイントスを行う）
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        b_repeat_when_frozen_turn : int
            先手の何本先取制
        w_repeat_when_frozen_turn : int
            後手の何本先取制
        
        Returns
        -------
        winner_color : int
            黒か白
        """

        # 新しい本目（Bout）
        b_got = 0
        w_got = 0

        # ｎ本勝負で勝ち負けが出るまでやる
        while True:

            # 黒が出た
            if coin(black_win_rate) == BLACK:
                b_got += 1

                # 黒の先取本数を取った（黒が勝った）
                if b_repeat_when_frozen_turn <= b_got:
                    return BLACK

            # 白が出た
            else:
                w_got += 1

                # 白の先取本数を取った（白が勝った）
                if w_repeat_when_frozen_turn <= w_got:
                    return WHITE

            # 続行


    def coin_toss_in_round_when_alternating_turn(self, black_win_rate, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn):
        """１対局行う（どちらの勝ちが出るまでコイントスを行う）

        手番を交互にするパターン
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        b_repeat_when_frozen_turn : int
            先手の何本先取制
        w_repeat_when_frozen_turn : int
            後手の何本先取制
        
        Returns
        -------
        winner_player : int
            ＡさんかＢさん
        """

        # 新しい本目（Bout）。未使用、Ａさん、Ｂさんの順
        b_got = [0, 0, 0]
        w_got = [0, 0, 0]

        # ｎ本勝負で勝ち負けが出るまでやる
        for bout_th in range(1, 2_147_483_647):

            # 黒が出た
            if coin(black_win_rate) == BLACK:

                # 奇数本で黒番のプレイヤーはＡさん
                if bout_th % 2 == 1:
                    successful_player = ALICE

                # 偶数本で黒番のプレイヤーはＢさん
                else:
                    successful_player = BOB

                b_got[successful_player] += 1

                # 黒の先取本数を取った（黒で、勝利条件を満たした）
                if b_repeat_when_frozen_turn <= b_got[successful_player]:
                    return successful_player

            # 白が出た
            else:

                # 奇数本で白番のプレイヤーはＢさん
                if bout_th % 2 == 1:
                    successful_player = BOB

                # 偶数本で白番のプレイヤーはＡさん
                else:
                    successful_player = ALICE

                w_got[successful_player] += 1

                # 白の先取本数を取った（白で、勝利条件を満たした）
                if w_repeat_when_frozen_turn <= w_got[successful_player]:
                    return successful_player

            # 続行


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


class PointRuleDescription():
    """勝ち点ルールの説明"""


    def __init__(self, b_step, w_step, span_when_frozen_turn):
        """初期化
        
        Parameters
        ----------
        b_step : int
            先手勝ちの点（先手＝Black）
        w_step : int
            後手勝ちの点（後手＝White）
        span_when_frozen_turn : int
            先後固定制での目標の点
        """
        self._b_step = b_step
        self._w_step = w_step
        self._span_when_frozen_turn = span_when_frozen_turn


    @property
    def b_step(self):
        """先手勝ちの点"""
        return self._b_step


    @property
    def w_step(self):
        """後手勝ちの点"""
        return self._w_step


    @property
    def span_when_frozen_turn(self):
        """先後固定制での目標の点"""
        return self._span_when_frozen_turn


    @property
    def b_repeat_when_frozen_turn(self):
        """先後固定制で、先手勝ちの点だけで目標の点に到達するのに必要な数［反復数］"""
        return self._span_when_frozen_turn / self._b_step


    @property
    def w_repeat_when_frozen_turn(self):
        """先後固定制で、後手勝ちの点だけで目標の点に到達するのに必要な数［反復数］"""
        return self._span_when_frozen_turn / self._w_step


    @staticmethod
    def let_points_from_require(b_repeat_when_frozen_turn, w_repeat_when_frozen_turn):
        """先手の勝ち点、後手の勝ち点、目標の勝ち点を求める"""
        # DO 通分したい。最小公倍数を求める
        lcm = math.lcm(b_repeat_when_frozen_turn, w_repeat_when_frozen_turn)
        # 先手勝ちの点
        b_step = lcm / b_repeat_when_frozen_turn
        # 後手勝ちの点
        w_step = lcm / w_repeat_when_frozen_turn
        # 先後固定制での目標の点
        span_when_frozen_turn = w_repeat_when_frozen_turn * w_step
        span_when_frozen_turn_w = b_repeat_when_frozen_turn * b_step
        if span_when_frozen_turn != span_when_frozen_turn_w:
            raise ValueError(f"{span_when_frozen_turn=}  {span_when_frozen_turn_w=}")

        return PointRuleDescription(b_step, w_step, span_when_frozen_turn)
