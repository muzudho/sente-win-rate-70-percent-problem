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


# def white_win_rate(p):
#     """［裏が出る確率］（後手勝率）
#
#     NOTE 0.11 が 0.10999999999999999 になっていたり、想定した結果を返さないことがあるから使わないほうがいい
#
#     Parameters
#     ----------
#     p : float
#         ［表が出る確率］
#     """
#     return 1 - p


def p_to_b_w_times(p):
    """［表が出る確率］ p を与えると、［黒勝ちだけでの対局数］、［白勝ちだけでの対局数］を返す
    
    Parameters
    ----------
    p : float
        表が出る確率
    
    Returns
    -------
    b_time : int
        ［黒勝ちだけでの対局数］
    w_time : int
        ［白勝ちだけでの対局数］
    """

    # 説明２  コインの表裏の確率の整数化
    # --------------------------------
    scale = scale_for_float_to_int(p)

    # ［黒勝ちだけでの対局数］基礎
    #
    #   NOTE int() を使って小数点以下切り捨てしようとすると、57 が 56 になったりするので、四捨五入にする
    #
    b_time = round_letro(p * scale)

    # ［白勝ちだけでの対局数］基礎
    w_time = scale - b_time

    # 約分する
    fraction = Fraction(b_time, w_time)
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


def n_bout_when_frozen_turn(black_rate, max_number_of_bout, b_time, w_time):
    """先後固定制で、最長で max_number_of_bout 回の対局を行い、勝った方の手番を返します

    NOTE 白番はずっと白番、黒番はずっと黒番とします。手番を交代しません

    max_number_of_bout はコインを振る回数。全部黒が出たら黒の勝ち、 w_time 回白が出れば白の勝ち。

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
    b_time : int
        黒が勝つのに必要な一本の数
    w_time : int
        白が勝つのに必要な一本の数
    
    Returns
    -------
    winner_color : int
        勝った方の色
    """
    black_count_down = b_time
    white_count_down = w_time

    for i in range(0, max_number_of_bout):
        if coin(black_rate) == WHITE:
            white_count_down -= 1
            if white_count_down < 1:
                return WHITE    # 白が勝ちぬけ
        else:
            black_count_down -= 1
            if black_count_down < 1:
                return BLACK    # 黒が勝ちぬけ

    raise ValueError(f"決着が付かずにループを抜けたからエラー  {black_rate=}  {max_number_of_bout=}  {b_time=}  {w_time=}")


def n_round_when_frozen_turn(p, number_of_longest_bout_when_frozen_turn, b_time, w_time, round_count):
    """［最長対局数（先後固定制）］の中で対局

    ｎ回対局して黒が勝った回数を返す。
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）  例： 黒番が７割勝つなら 0.7
    number_of_longest_bout_when_frozen_turn : int
        ［最長対局数（先後固定制）］。例： ３本勝負なら 3
    b_time : int
        黒が勝つのに必要な一本の数
    w_time : int
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
        if n_bout_when_frozen_turn(p, number_of_longest_bout_when_frozen_turn, b_time, w_time) == BLACK:
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


    def play_game_when_frozen_turn(self, p, b_time, w_time):
        """［先後固定制］で１対局行う（どちらの勝ちが出るまでコイントスを行う）
        
        Parameters
        ----------
        p : float
            ［表が出る確率］（先手勝率）
        b_time : int
            先手の何本先取制
        w_time : int
            後手の何本先取制
        
        Returns
        -------
        winner_color : int
            黒か白
        bout_th : int
            対局本数
        """

        # 一本を取った数
        b_got = 0
        w_got = 0

        # ｎ本勝負で勝ち負けが出るまでやる
        for bout_th in range(1, 2_147_483_647):

            # 黒が出た
            if coin(p) == BLACK:
                b_got += 1

                # ［黒勝ちだけでの対局数］を取った（黒が勝った）
                if b_time <= b_got:
                    return BLACK, bout_th

            # 白が出た
            else:
                w_got += 1

                # ［白勝ちだけでの対局数］を取った（白が勝った）
                if w_time <= w_got:
                    return WHITE, bout_th

            # 続行

        raise ValueError("設定している回数で、決着が付かなかった")


    def play_game_when_alternating_turn(self, p, points_configuration):
        """［先後交互制］で１対局行う（どちらの勝ちが出るまでコイントスを行う）
        
        Parameters
        ----------
        p : float
            ［表が出る確率］（先手勝率）
        points_configuration : PointsConfiguration
            ［勝ち点ルール］の構成
        
        Returns
        -------
        winner_player : int
            ＡさんかＢさん
        bout_th : int
            対局本数
        """

        # ［得点］の配列。要素は、未使用、Ａさん、Ｂさんの順
        point_list = [0, 0, 0]

        # ｎ本勝負で勝ち負けが出るまでやる
        for bout_th in range(1, 2_147_483_647):

            # 黒が出た
            if coin(p) == BLACK:
                step = points_configuration.b_step

                # 奇数本で黒番のプレイヤーはＡさん
                if bout_th % 2 == 1:
                    successful_player = ALICE

                # 偶数本で黒番のプレイヤーはＢさん
                else:
                    successful_player = BOB

            # 白が出た
            else:
                step = points_configuration.w_step

                # 奇数本で白番のプレイヤーはＢさん
                if bout_th % 2 == 1:
                    successful_player = BOB

                # 偶数本で白番のプレイヤーはＡさん
                else:
                    successful_player = ALICE


            point_list[successful_player] += step

            if points_configuration.span_when_frozen_turn <= point_list[successful_player]:
                return successful_player, bout_th

            # 続行

        raise ValueError("設定している回数で、決着が付かなかった")


def calculate_probability(p, H, T):
    """［表側を持っているプレイヤー］が勝つ確率を返します

    NOTE ＡさんとＢさんは、表、裏を入れ替えて持つことがあるので、［表側を持っているプレイヤー］が必ずＡさんとは限らない

    ［表側を持っているプレイヤー］が勝つ条件：　表が H 回出る前に裏が T 回出ないこと
    試行回数の考え方：　ゲームは最小で H 回、最大で N = H + T - 1 回のコイン投げで終了します
    確率の計算：　総試行回数 N 回で、表が H 回以上出る確率を計算します

    # パラメータの設定例
    p = 0.7  # 表が出る確率
    H = 7    # ［表側を持っているプレイヤー］が必要な表の回数
    T = 3    # ［裏側を持っているプレイヤー］が必要な裏の回数

    # 計算の実行例
    probability = calculate_probability(p, H, T)
    print(f"［表側を持っているプレイヤー］が勝つ確率: {probability * 100:.2f}%")

    Parameters
    ----------
    p : float
        表が出る確率
    H : int
        ［表側を持っているプレイヤー］が必要な、表の先取回数
    T : int
        ［裏側を持っているプレイヤー］が必要な、裏の先取回数
    
    Returns
    -------
    probability : float
        ［表側を持っているプレイヤー］が勝つ確率
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


class PointsConfiguration():
    """勝ち点の構成［勝ち点ルール］"""


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
        """先手勝ちの点［黒勝ちの価値］"""
        return self._b_step


    @property
    def w_step(self):
        """後手勝ちの点［白勝ちの価値］"""
        return self._w_step


    @property
    def span_when_frozen_turn(self):
        """先後固定制での目標の点"""
        return self._span_when_frozen_turn


    @property
    def b_time(self):
        """［先後固定制］での［黒勝ちだけでの対局数］"""

        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        return round_letro(self._span_when_frozen_turn / self._b_step)


    @property
    def w_time(self):
        """［先後固定制］での［白勝ちだけでの対局数］"""

        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        return round_letro(self._span_when_frozen_turn / self._w_step)


    @staticmethod
    def let_points_from_repeat(b_time, w_time):
        """［先後固定制］での［黒勝ちだけでの対局数］と［白勝ちだけでの対局数］が分かれば、［勝ち点ルール］を分析して返す
        
        Parameters
        ----------
        b_time : int
            ［黒勝ちだけでの対局数］
        w_time : int
            ［白勝ちだけでの対局数］
        """
        # DO 通分したい。最小公倍数を求める
        lcm = math.lcm(b_time, w_time)
        # 先手勝ちの点
        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        b_step = round_letro(lcm / b_time)
        # 後手勝ちの点
        w_step = round_letro(lcm / w_time)
        # 先後固定制での目標の点
        span_when_frozen_turn = round_letro(w_time * w_step)
        span_when_frozen_turn_w = round_letro(b_time * b_step)
        if span_when_frozen_turn != span_when_frozen_turn_w:
            raise ValueError(f"{span_when_frozen_turn=}  {span_when_frozen_turn_w=}")

        return PointsConfiguration(b_step, w_step, span_when_frozen_turn)


    def let_number_of_shortest_bout_when_frozen_turn(self):
        """［最短対局数（先後固定制）］
        
        白が全勝したときの回数と同じ

        理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
        先後固定制で最長は？
        ・  白  白  白  白  白  で、最短５局
        10  10  10  10 10  10
        10   8   6   4  2   0
        """
        return self.w_time


    def let_number_of_longest_bout_when_frozen_turn(self):
        """［最長対局数（先後固定制）］

        黒があと１つで勝てるところで止まり、白が全勝したときの回数と同じ

        NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
        NOTE 先手が１本、後手が１本取ればいいとき、最大で１本の勝負が行われる（先 or 後）から、１本勝負と呼ぶ
        NOTE 先手が２本、後手が１本取ればいいとき、最大で２本の勝負が行われる（先先 or 先後）から、２本勝負と呼ぶ

        理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
        先後固定制で最長は？
        ・  黒  黒  黒  黒  黒  黒  黒  黒  黒  白  白  白  白  白  で、最長１４局
        10   9   8   7   6   5  4   3   2   1  1   1   1   1   1
        10  10  10  10  10  10 10  10  10  10  8   6   4   2   0
        """
        return  (self.b_time-1) + (self.w_time-1) + 1


    def let_number_of_shortest_bout_when_alternating_turn(self):
        """［最短対局数（先後交互制）］
        
        Ｂさんだけが勝ったときの回数と同じ。

        まず、［目標の点］が［黒勝ちの価値］＋［白勝ちの価値］より上回っているなら、［目標の点］から［黒勝ちの価値］＋［白勝ちの価値］を順に引いていく（２回分を加算していく）。
        端数が出たら［白勝ちの価値］（１回分）を加算する。
        まだ端数が出たら［黒勝ちの価値］（１回分）を加算する。
        そのような、［目標の点］に達するまでの回数。

        筆算
        ----

            理論上 `対局数  5～13（先後固定制）   6～17（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標  9点（先後固定制）`
            先後交互制で最短は？
                ・  Ａ  ａ  Ａ  ａ  Ａ  ａ  で、最短６対局
                9   8  6   5   3   2   0

                ・  ｂ  Ｂ  ｂ  Ｂ  ｂ  Ｂ  で、最短６対局
                9   7  6   4   3   1   0


            理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
            先後交互制で最短は？
                ・  Ａ  ａ  Ａ  ａ  Ａ  ａ  Ａ  で、最短７対局
                10   9  7   6   4   3   1   0

                ・  ｂ  Ｂ  ｂ  Ｂ  ｂ  Ｂ  ｂ  で、最短７対局
                10   8  7   5   4   2   1  -1
            
            `先手勝ち10点、後手勝ち19点　目標190点` のとき、理論値は `対局数 14～37` だが、実際には `実際   13～37` となったことがあった
            先後交互制で最短は？
                ・   Ａ   ａ   Ａ    ａ   Ａ   ａ   Ａ  ａ  Ａ   ａ  Ａ  ａ  Ａ   ａ  で14局
                190  180  161  151  132  122  103  93  74  64  45  35  16   6  -13

                ・   ｂ   Ｂ   ｂ    Ｂ   ｂ   Ｂ   ｂ  Ｂ  ｂ   Ｂ  ｂ  Ｂ  ｂ  で最短13局
                190  171  161  142  132  113  103  84  74  55  45  26  16  -3
        """

        # FIXME 先後交互制用の変数を使いたい
        remainder = self._span_when_frozen_turn

        if self._b_step + self._w_step <= remainder:
            # NOTE なるべく割り算で小数点以下の数がでないように、割り切れる数にしてから割るようにし、整数だけを使って計算する
            new_remainder = self._span_when_frozen_turn % (self._b_step + self._w_step)
            bout = math.floor( (remainder - new_remainder) / (self._b_step + self._w_step)) * 2
            remainder = new_remainder

        else:
            bout = 0

        # 端数があれば［白勝ちの価値］を引く（１回分を加算）
        #
        #   NOTE 白（後手）の方が step 値が黒（先手）より大きいか、等しいです。［白勝ちの価値］の方から先に引きます
        #
        if 0 < remainder:
            bout += 1
            remainder -= self._w_step

            # まだ端数があれば［黒勝ちの価値］を引く（１回分を加算）
            if 0 < remainder:
                bout += 1
                remainder -= self._b_step

                # remainder は負数になっているはず（割り切れないはず）
                if 0 <= remainder:
                    raise ValueError(f"ここで余りが負数になっていないのはおかしい {remainder=}  {self._span_when_frozen_turn=}  {self._b_step=}  {self._w_step=}")
            
            # remainder は零か負数になっているはず
            elif 0 < remainder:
                raise ValueError(f"ここで余りが零か負数になっていないのはおかしい {remainder=}  {self._span_when_frozen_turn=}  {self._b_step=}  {self._w_step=}")

        return bout


    def let_number_of_longest_bout_when_alternating_turn(self):
        """［最長対局数（先後交互制）］

        ＡさんとＢさんの両者が先手で勝ち続けた回数と同じ

        筆算
        ----

            理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
                ・  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  で、最長１９対局
                10  9   9   8   8   7   7   6  6   5   5   4   4   3  3   2   2   1   1   0
                10 10   9   9   8   8   7   7  6   6   5   5   4   4  3   3   2   2   1   1
        """

        # FIXME 先後交互制用の変数を使いたい
        return  (self.b_time-1) + (self.b_time-1) + 1
