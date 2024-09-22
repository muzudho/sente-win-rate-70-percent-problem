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


# 色は付いておらず、また、誰でもない。配列のインデックスに使う
EMPTY = 0

# 黒。表。先手。配列のインデックスに使う
BLACK = 1

# 白。裏。後手。配列のインデックスに使う
WHITE = 2

# Ａさん。配列のインデックスに使う
ALICE = 3

# Ｂさん。配列のインデックスに使う
BOB = 4


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
    """表が黒、裏が白のコインを投げる

    Parameters
    ----------
    black_rate : float
        黒が出る確率。例： 黒が７割出るなら 0.7
    """
    if random.random() < black_rate:
        return BLACK
    return WHITE


def draw(draw_rate):
    """確率的に引き分けになる

    Parameters
    ----------
    draw_rate : float
        引き分けになる確率。例： １割が引き分けなら 0.1
    """
    return random.random() < draw_rate


class CointossResultInSeries():
    """シリーズのコイントスした結果"""


    def __init__(self, p, draw_rate, longest_times, successful_color_list):
        """初期化

        Parameters
        ----------
        p : float
            ［表が出る確率］ 例： ７割なら 0.7
        draw_rate : float
            ［将棋の引分け率】 例： １割の確率で引き分けになるのなら 0.1
        longest_times : int
            ［最長対局数］
        successful_color_list : list
            コイントスした結果のリスト。引き分けは EMPTY
        """
        self._p = p,
        self._draw_rate = draw_rate
        self._longest_times = longest_times
        self._successful_color_list = successful_color_list


    @property
    def p(self):
        """［表が出る確率］"""
        return self._p


    @property
    def draw_rate(self):
        """［引き分ける確率］"""
        return self._draw_rate


    @property
    def longest_times(self):
        """最長対局数］"""
        return self._longest_times


    @property
    def successful_color_list(self):
        """コイントスした結果のリスト。引き分けは EMPTY"""
        return self._successful_color_list


    @staticmethod
    def make_pseudo_obj(p, draw_rate, longest_times):
        """１シリーズをフルに対局したときのコイントスした結果の疑似リストを生成

        Parameters
        ----------
        p : float
            ［表が出る確率］
        draw_rate : float
            ［引き分ける確率］
        longest_times : int
            ［最長対局数］
        """

        successful_color_list = []

        # ［最長対局数］までやる
        for time_th in range(1, longest_times + 1):

            # 引分け
            if draw(draw_rate):
                successful_color_list.append(EMPTY)

            # 黒勝ち、または白勝ちのどちらか
            else:
                successful_color_list.append(coin(p))


        return CointossResultInSeries(
                p=p,
                draw_rate=draw_rate,
                longest_times=longest_times,
                successful_color_list=successful_color_list)


    def cut_down(self, number_of_times):
        """コイントスの結果のリストの長さを切ります。
        対局は必ずしも［最長対局数］になるわけではありません"""
        self._successful_color_list = self._successful_color_list[0:number_of_times]


    def stringify_dump(self):
        """ダンプ"""
        return f"{self._p=}  {self._draw_rate=}  {self._longest_times=}  {self._successful_color_list}"


def make_all_results_of_cointoss_in_series_when_frozen_turn(can_draw, points_configuration):
    """TODO ［先後固定制］での１シリーズについて、フル対局分の、全パターンのコイントスの結果を作りたい
    
    １タイムは　勝ち、負けの２つ、または　勝ち、負け、引き分けの３つ。

    Returns
    -------
    power_set_list : list
        勝った方の色（引き分けなら EMPTY）のリストが全パターン入っているリスト
    """

    # 要素数
    if can_draw:
        # 黒勝ち、白勝ち、勝者なしの３要素
        elements = [BLACK, WHITE, EMPTY]
    else:
        # 黒勝ち、白勝ちけの２要素
        elements = [BLACK, WHITE]

    # 桁数
    depth = points_configuration.count_longest_time_when_frozen_turn()

    # １シーズン分のコイントスの全ての結果
    stats = []

    position = []


    def search(depth, stats, position, can_draw):

        # 黒勝ちを追加
        position.append(BLACK)

        # スタッツに、ポジションのコピーを追加
        stats.append(list(position))

        if 0 < depth:
            search(depth - 1, stats, position, can_draw=False)

        # 末尾の要素を削除
        position.pop()


        # 白勝ちを追加
        position.append(WHITE)

        # スタッツに、ポジションのコピーを追加
        stats.append(list(position))

        if 0 < depth:
            search(depth - 1, stats, position, can_draw=False)

        # 末尾の要素を削除
        position.pop()


        if can_draw:
            # 引分けを追加
            position.append(EMPTY)

            # スタッツに、ポジションのコピーを追加
            stats.append(list(position))

            if 0 < depth:
                search(depth - 1, stats, position, can_draw=False)

            # 末尾の要素を削除
            position.pop()



    search(depth, stats, position, can_draw=False)


    return stats


def play_series_when_frozen_turn(cointoss_result_in_series, points_configuration):
    """［先後固定制］で１シリーズ分の対局を行います。

    ［勝ち点差判定］や［タイブレーク］など、決着が付かなかったときの処理は含みません
    もし、引き分けがあれば、［引き分けを１局として数えるケース］です。

    Parameters
    ----------
    cointoss_result_in_series : CointossResultInSeries
        コイントス・リスト
    points_configuration : PointsConfiguration
        ［かくきんシステムのｐの構成］
    
    Returns
    -------
    series_result : SeriesResult
        ［シリーズ］の結果
    """

    # ［勝ち点］のリスト。要素は、未使用、黒番、白番、Ａさん、Ｂさん
    point_list = [0, 0, 0, 0, 0]

    # ［このシリーズで引き分けた対局数］
    number_of_draw_times = 0

    time_th = 0

    # 予め作った１シリーズ分の対局結果を読んでいく
    for successful_color in cointoss_result_in_series.successful_color_list:
        time_th += 1

        # 引き分けを１局と数えるケース
        #
        #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
        #
        if successful_color == EMPTY:
            number_of_draw_times += 1
        
        else:
            if successful_color == BLACK:
                successful_player = ALICE
                step = points_configuration.b_step

            else:
                successful_player = BOB
                step = points_configuration.w_step

            point_list[successful_color] += step
            point_list[successful_player] += step

            # 勝ち抜け
            if points_configuration.span <= point_list[successful_color]:

                # コイントスの結果のリストの長さを切ります。
                # 対局は必ずしも［最長対局数］になるわけではありません
                cointoss_result_in_series.cut_down(time_th)

                return SeriesResult(
                        number_of_all_times=time_th,
                        number_of_draw_times=number_of_draw_times,
                        span=points_configuration.span,
                        point_list=point_list,
                        cointoss_result_in_series=cointoss_result_in_series)


    # タイブレークをするかどうかは、この関数の呼び出し側に任せます
    return SeriesResult(
            number_of_all_times=time_th,
            number_of_draw_times=number_of_draw_times,
            span=points_configuration.span,
            point_list=point_list,
            cointoss_result_in_series=cointoss_result_in_series)


def play_tie_break(p, draw_rate):
    """［タイブレーク］を行います。１局勝負で、引き分けの場合は白勝ちです。

    Parameters
    ----------
    p : float
        ［表が出る確率］ 例： ７割なら 0.7
    draw_rate : float
        ［将棋の引分け率】 例： １割の確率で引き分けになるのなら 0.1
    
    Returns
    -------
    winner_color : int
        勝った方の色。引き分けなら白勝ち
    """

    # 引き分けなら白勝ち
    if draw(draw_rate):
        return WHITE

    else:
        return coin(p)


def play_game_when_alternating_turn(cointoss_result_in_series, points_configuration):
    """［先後交互制］で１対局行う（どちらの勝ちが出るまでコイントスを行う）
    
    Parameters
    ----------
    points_configuration : PointsConfiguration
        ［かくきんシステムのｐの構成］
    
    Returns
    -------
    series_result : SeriesResult
        ［シリーズ］の結果
    """

    # ［勝ち点］の配列。要素は、未使用、黒、白、Ａさん、Ｂさんの順
    point_list = [0, 0, 0, 0, 0]

    # ［このシリーズで引き分けた対局数］
    number_of_draw_times = 0

    time_th = 0

    # 予め作った１シリーズ分の対局結果を読んでいく
    for successful_color in cointoss_result_in_series.successful_color_list:
        time_th += 1

        # 引き分けを１局と数えるケース
        #
        #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
        #
        if successful_color == EMPTY:
            number_of_draw_times += 1
        
        else:
            # 黒が出た
            if successful_color == BLACK:
                step = points_configuration.b_step

                # 奇数本で黒番のプレイヤーはＡさん
                if time_th % 2 == 1:
                    successful_player = ALICE

                # 偶数本で黒番のプレイヤーはＢさん
                else:
                    successful_player = BOB

            # 白が出た
            else:
                step = points_configuration.w_step

                # 奇数本で白番のプレイヤーはＢさん
                if time_th % 2 == 1:
                    successful_player = BOB

                # 偶数本で白番のプレイヤーはＡさん
                else:
                    successful_player = ALICE


            point_list[successful_color] += step
            point_list[successful_player] += step

            if points_configuration.span <= point_list[successful_player]:

                # コイントスの結果のリストの長さを切ります。
                # 対局は必ずしも［最長対局数］になるわけではありません
                cointoss_result_in_series.cut_down(time_th)

                return SeriesResult(
                        number_of_all_times=time_th,
                        number_of_draw_times=number_of_draw_times,
                        span=points_configuration.span,
                        point_list=point_list,
                        cointoss_result_in_series=cointoss_result_in_series)


    # タイブレークをするかどうかは、この関数の呼び出し側に任せます
    return SeriesResult(
            number_of_all_times=time_th,
            number_of_draw_times=number_of_draw_times,
            span=points_configuration.span,
            point_list=point_list,
            cointoss_result_in_series=cointoss_result_in_series)


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
    """［かくきんシステムのｐの構成］"""


    def __init__(self, b_step, w_step, span):
        """初期化
        
        Parameters
        ----------
        b_step : int
            ［黒勝ち１つの点数］
        w_step : int
            ［白勝ち１つの点数］
        span : int
            ［目標の点数］
        """

        # NOTE numpy.int64 型は、 float NaN が入っていることがある？
        if not isinstance(b_step, int):
            raise ValueError(f"int 型であることが必要 {type(b_step)=}")

        if not isinstance(w_step, int):
            raise ValueError(f"int 型であることが必要 {type(w_step)=}")

        if not isinstance(span, int):
            raise ValueError(f"int 型であることが必要 {type(span)=}")

        if b_step < 1:
            raise ValueError(f"正の整数であることが必要 {b_step=}")

        if w_step < 1:
            raise ValueError(f"正の整数であることが必要 {w_step=}")

        if span < 1:
            raise ValueError(f"正の整数であることが必要 {span=}")

        if w_step < b_step:
            raise ValueError(f"{b_step=} <= {w_step}")

        if span < w_step:
            raise ValueError(f"{w_step=} <= {span}")

        self._b_step = b_step
        self._w_step = w_step
        self._span = span


    @property
    def b_step(self):
        """［黒勝ち１つの点数］"""
        return self._b_step


    @property
    def w_step(self):
        """［白勝ち１つの点数］"""
        return self._w_step


    @property
    def span(self):
        """［目標の点数］"""
        return self._span


    @property
    def b_time(self):
        """［黒勝ちだけでの対局数］

        筆算
        ----
        `10黒 12白 14目（先後固定制）`
            ・  黒  黒  で最長２局
            14  14  14
            14   4  -6
        """

        #
        #   NOTE 切り上げても .00001 とか .99999 とか付いているかもしれない？から、四捨五入して整数に変換しておく
        #
        return round_letro(math.ceil(self._span / self._b_step))


    @property
    def w_time(self):
        """［白勝ちだけでの対局数］

        筆算
        ----
        `10黒 12白 14目（先後固定制）`
            ・  白  で最長１局
            14   0
            14  14
        """

        #
        #   NOTE 切り上げても .00001 とか .99999 とか付いているかもしれない？から、四捨五入して整数に変換しておく
        #
        return round_letro(math.ceil(self._span / self._w_step))


    @staticmethod
    def let_points_from_repeat(b_time, w_time):
        """［黒勝ちだけでの対局数］と［白勝ちだけでの対局数］が分かれば、［かくきんシステムのｐの構成］を分析して返す
        
        Parameters
        ----------
        b_time : int
            ［黒勝ちだけでの対局数］
        w_time : int
            ［白勝ちだけでの対局数］
        """
        # DO 通分したい。最小公倍数を求める
        lcm = math.lcm(b_time, w_time)
        # ［黒勝ち１つの点数］
        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        b_step = round_letro(lcm / b_time)
        # ［白勝ち１つの点数］
        w_step = round_letro(lcm / w_time)
        # ［目標の点数］
        span = round_letro(w_time * w_step)

        # データチェック
        span_w = round_letro(b_time * b_step)
        if span != span_w:
            raise ValueError(f"{span=}  {span_w=}")

        return PointsConfiguration(
                b_step=b_step,
                w_step=w_step,
                span=span)


    def count_shortest_time_when_frozen_turn(self):
        """［先後固定制］での［最短対局数］
        
        白が全勝したときの回数と同じ

        `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
            ・  白  白  白  白  白  で、最短５局
            10  10  10  10 10  10
            10   8   6   4  2   0
        """
        return self.w_time


    def count_longest_time_when_frozen_turn(self):
        """［先後固定制］での［最長対局数］

        白があと１つで勝てるところで止まり、黒が全勝したときの回数と同じ

        NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
        NOTE 先手が１本、後手が１本取ればいいとき、最大で１本の勝負が行われる（先 or 後）から、１本勝負と呼ぶ
        NOTE 先手が２本、後手が１本取ればいいとき、最大で２本の勝負が行われる（先先 or 先後）から、２本勝負と呼ぶ

        `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
            ・  黒  黒  黒  黒  黒  黒  黒  黒  黒  白  白  白  白  白  で、最長１４局
            10   9   8   7   6   5  4   3   2   1  1   1   1   1   1
            10  10  10  10  10  10 10  10  10  10  8   6   4   2   0
        
        `10黒 12白 14目（先後固定制）`
            ・  白  黒  黒  で最長３局
            14   2   2   2
            14  14   4  -6
        """
        return  (self.b_time-1) + (self.w_time-1) + 1


    def count_shortest_time_when_alternating_turn(self):
        """［先後交互制］での［最短対局数］
        
        Ｂさんだけが勝ったときの回数と同じ。

        まず、［目標の点数］が［黒勝ち１つの点数］＋［白勝ち１つの点数］より上回っているなら、［目標の点数］から［黒勝ち１つの点数］＋［白勝ち１つの点数］を順に引いていく（２回分を加算していく）。
        端数が出たら［白勝ち１つの点数］（１回分）を加算する。
        まだ端数が出たら［黒勝ち１つの点数］（１回分）を加算する。
        そのような、［目標の点数］に達するまでの回数。

        筆算
        ----

            `先手勝ち 1点、後手勝ち 2点　目標  9点` のとき、先後交互制で最短は？
                ・  Ａ  ａ  Ａ  ａ  Ａ  ａ  で、最短６対局
                9   8  6   5   3   2   0

                ・  ｂ  Ｂ  ｂ  Ｂ  ｂ  Ｂ  で、最短６対局
                9   7  6   4   3   1   0


            `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後交互制で最短は？
                ・  Ａ  ａ  Ａ  ａ  Ａ  ａ  Ａ  で、最短７対局
                10   9  7   6   4   3   1   0

                ・  ｂ  Ｂ  ｂ  Ｂ  ｂ  Ｂ  ｂ  で、最短７対局
                10   8  7   5   4   2   1  -1
            
            `先手勝ち10点、後手勝ち19点　目標190点` のとき、先後交互制で最短は？
                ・   Ａ   ａ   Ａ    ａ   Ａ   ａ   Ａ  ａ  Ａ   ａ  Ａ  ａ  Ａ   ａ  で14局
                190  180  161  151  132  122  103  93  74  64  45  35  16   6  -13

                ・   ｂ   Ｂ   ｂ    Ｂ   ｂ   Ｂ   ｂ  Ｂ  ｂ   Ｂ  ｂ  Ｂ  ｂ  で最短13局
                190  171  161  142  132  113  103  84  74  55  45  26  16  -3
        """

        remainder = self._span

        if self._b_step + self._w_step <= remainder:
            # NOTE なるべく割り算で小数点以下の数がでないように、割り切れる数にしてから割るようにし、整数だけを使って計算する
            new_remainder = self._span % (self._b_step + self._w_step)
            time = math.floor( (remainder - new_remainder) / (self._b_step + self._w_step)) * 2
            remainder = new_remainder

        else:
            time = 0

        # 端数があれば［白勝ち１つの点数］を引く（１回分を加算）
        #
        #   NOTE 白（後手）の方が step 値が黒（先手）より大きいか、等しいです。［白勝ち１つの点数］の方から先に引きます
        #
        if 0 < remainder:
            time += 1
            remainder -= self._w_step

            # まだ端数があれば［黒勝ち１つの点数］を引く（１回分を加算）
            if 0 < remainder:
                time += 1
                remainder -= self._b_step

                # remainder は負数になっているはず（割り切れないはず）
                if 0 <= remainder:
                    raise ValueError(f"ここで余りが負数になっていないのはおかしい {remainder=}  {self._span=}  {self._b_step=}  {self._w_step=}")
            
            # remainder は零か負数になっているはず
            elif 0 < remainder:
                raise ValueError(f"ここで余りが零か負数になっていないのはおかしい {remainder=}  {self._span=}  {self._b_step=}  {self._w_step=}")

        return time


    def count_longest_time_when_alternating_turn(self):
        """［先後交互制］での［最長対局数］

        ＡさんとＢさんの両者が先手で勝ち続けた回数と同じ

        筆算
        ----

            理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
                ・  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  で、最長１９対局
                10  9   9   8   8   7   7   6  6   5   5   4   4   3  3   2   2   1   1   0
                10 10   9   9   8   8   7   7  6   6   5   5   4   4  3   3   2   2   1   1
        
            `0.014715 10黒 12白 14目 1～1局（先後交互制）`
                ・  Ａ  Ｂ  Ａ  で、最長３局
                14   4   4  -6
                14  14   4   4
        """

        return  (self.b_time-1) + (self.w_time-1) + 1


class SeriesResult():
    """［シリーズ］の結果"""


    def __init__(self, number_of_all_times, number_of_draw_times, span, point_list, cointoss_result_in_series):
        """初期化
    
        Parameters
        ----------
        number_of_all_times : int
            行われた対局数
        number_of_draw_times : int
            引分けだった対局数
        span : int
            ［目標の点数］
        point_list : list
            ［先後固定制］での［勝ち点］のリスト。要素は、未使用、黒番、白番、Ａさん、Ｂさん
        cointoss_result_in_series : CointossResultInSeries
            １シリーズ分をフルにコイントスした結果
        """

        # 共通
        self._number_of_all_times = number_of_all_times
        self._number_of_draw_times = number_of_draw_times
        self._span = span
        self._point_list = point_list
        self._cointoss_result_in_series = cointoss_result_in_series

        # ［先後固定制］
        self._is_no_won_color = None
        self._is_black_points_won = None
        self._is_white_points_won = None

        # ［先後交互制］
        self._is_no_won_player = None
        self._is_alice_points_won = None
        self._is_bob_points_won = None


    # 共通
    # ----

    @property
    def number_of_all_times(self):
        """行われた対局数"""
        return self._number_of_all_times


    @property
    def number_of_draw_times(self):
        """引分けだった対局数"""
        return self._number_of_draw_times


    @property
    def cointoss_result_in_series(self):
        """１シリーズ分をフルにコイントスした結果"""
        return self._cointoss_result_in_series

    # ［先後固定制］
    # -------------


    @property
    def is_no_won_color(self):
        """勝者なし。黒白ともに［勝ち点］が［目標の点数］の半数（小数点以下切り捨て）以下か、または、両者の［勝ち点］が等しいとき"""
        if self._is_no_won is None:
            half = math.floor(self._span / 2)
            self._is_no_won = (self._point_list[BLACK] <= half and self._point_list[WHITE] <= half) or self._point_list[BLACK] == self._point_list[WHITE]

        return self._is_no_won


    @property
    def is_black_fully_won(self):
        """黒が［目標の点数］を集めて黒の勝ち"""
        return self._span <= self._point_list[BLACK]


    @property
    def is_white_fully_won(self):
        """白が［目標の点数］を集めて白の勝ち"""
        return self._span <= self._point_list[WHITE]


    @property
    def is_black_points_won(self):
        """黒の［勝ち点］は［目標の点数］に達していないが、過半数は集めており、さらに白の［勝ち点］より多くて黒の勝ち"""
        if self._is_black_points_won is None:
            half = math.floor(self._span / 2)
            self._is_black_points_won = half < self._point_list[BLACK] and self._point_list[BLACK] < self._span and self._point_list[WHITE] < self._point_list[BLACK]

        return self._is_black_points_won


    @property
    def is_white_points_won(self):
        """白の［勝ち点］は［目標の点数］に達していないが、過半数は集めており、さらに黒の［勝ち点］より多くて白の勝ち"""
        if self._is_white_points_won is None:
            half = math.floor(self._span / 2)
            self._is_white_points_won = half < self._point_list[WHITE] and self._point_list[WHITE] < self._span and self._point_list[BLACK] < self._point_list[WHITE]

        return self._is_white_points_won


    @property
    def is_black_won(self):
        """黒勝ち"""
        return self.is_black_fully_won or self.is_black_points_won


    @property
    def is_white_won(self):
        """白勝ち"""
        return self.is_white_fully_won or self.is_white_points_won


    # ［先後交互制］
    # -------------


    @property
    def is_no_won_player(self):
        """勝者なし。ＡさんＢさんともに［勝ち点］が［目標の点数］の半数（小数点以下切り捨て）以下か、または、両者の［勝ち点］が等しいとき"""
        if self._is_no_won is None:
            half = math.floor(self._span / 2)
            self._is_no_won = (self._point_list[ALICE] <= half and self._point_list[BOB] <= half) or self._point_list[ALICE] == self._point_list[BOB]

        return self._is_no_won


    @property
    def is_alice_fully_won(self):
        """Ａさんが［目標の点数］を集めて黒の勝ち"""
        return self._span <= self._point_list[ALICE]


    @property
    def is_bob_fully_won(self):
        """Ｂさんが［目標の点数］を集めて白の勝ち"""
        return self._span <= self._point_list[BOB]


    @property
    def is_alice_points_won(self):
        """Ａさんの［勝ち点］は［目標の点数］に達していないが、過半数は集めており、さらにＢさんの［勝ち点］より多くてＡさんの勝ち"""
        if self._is_alice_points_won is None:
            half = math.floor(self._span / 2)
            self._is_alice_points_won = half < self._point_list[ALICE] and self._point_list[ALICE] < self._span and self._point_list[BOB] < self._point_list[ALICE]

        return self._is_alice_points_won


    @property
    def is_bob_points_won(self):
        """Ｂさんの［勝ち点］は［目標の点数］に達していないが、過半数は集めており、さらにＡさんの［勝ち点］より多くてＢさんの勝ち"""
        if self._is_bob_points_won is None:
            half = math.floor(self._span / 2)
            self._is_bob_points_won = half < self._point_list[BOB] and self._point_list[BOB] < self._span and self._point_list[ALICE] < self._point_list[BOB]

        return self._is_bob_points_won


    @property
    def is_alice_won(self):
        """Ａさんの勝ち"""
        return self.is_alice_fully_won() or self.is_alice_points_won


    @property
    def is_bob_won(self):
        """Ｂさんの勝ち"""
        return self.is_bob_fully_won() or self.is_bob_points_won


class SimulationResult():
    """シミュレーションの結果"""


    def __init__(self, series_result_list):
        """初期化
        
        Parameters
        ----------
        series_result_list : list
            ［シリーズ］の結果のリスト
        """


        # 共通
        # ----

        self._series_result_list = series_result_list
        self._shortest_time_th = None
        self._longest_time_th = None
        self._number_of_draw_times = None


        # 「先後固定制］
        # -------------

        self._number_of_black_fully_wons = None
        self._number_of_white_fully_wons = None
        self._number_of_black_points_wons = None
        self._number_of_white_points_wons = None


        # ［先後交互制］
        # -------------

        self._number_of_alice_fully_wons = None
        self._number_of_bob_fully_wons = None
        self._number_of_alice_points_wons = None
        self._number_of_bob_points_wons = None


    # 共通
    # ----


    @property
    def number_of_series(self):
        """シリーズ数"""
        return len(self._series_result_list)


    @property
    def shortest_time_th(self):
        """［最短対局数］"""
        if self._shortest_time_th is None:
            self._shortest_time_th = 2_147_483_647
            for series_result in self._series_result_list:
                if series_result.number_of_all_times < self._shortest_time_th:
                    self._shortest_time_th = series_result.number_of_all_times

        return self._shortest_time_th


    @property
    def longest_time_th(self):
        """［最長対局数］"""
        if self._longest_time_th is None:
            self._longest_time_th = 0
            for series_result in self._series_result_list:
                if self._longest_time_th < series_result.number_of_all_times:
                    self._longest_time_th = series_result.number_of_all_times

        return self._shortest_time_th


    @property
    def number_of_draw_times(self):
        """全シリーズ通算の引分けの対局数"""
        if self._number_of_draw_times is None:
            self._number_of_draw_times = 0
            for series_result in self._series_result_list:
                if series_result.number_of_draw_times:
                    self._number_of_draw_times += 1

        return self._number_of_draw_times


    # 「先後固定制］
    # -------------


    @property
    def number_of_black_fully_wons(self):
        """黒が［目標の点数］を集めて勝った回数"""
        if self._number_of_black_fully_wons is None:
            self._number_of_black_fully_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_black_fully_won:
                    self._number_of_black_fully_wons += 1

        return self._number_of_black_fully_wons


    @property
    def number_of_white_fully_wons(self):
        """白が［目標の点数］を集めて勝った回数"""
        if self._number_of_white_fully_wons is None:
            self._number_of_white_fully_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_white_fully_won:
                    self._number_of_white_fully_wons += 1

        return self._number_of_white_fully_wons


    @property
    def number_of_black_points_wons(self):
        """黒が［勝ち点差判定］で勝った回数"""
        if self._number_of_black_points_wons is None:
            self._number_of_black_points_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_black_points_won:
                    self._number_of_black_points_wons += 1

        return self._number_of_black_points_wons


    @property
    def number_of_white_points_wons(self):
        """白が［勝ち点差判定］で勝った回数"""
        if self._number_of_white_points_wons is None:
            self._number_of_white_points_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_white_points_won:
                    self._number_of_white_points_wons += 1

        return self._number_of_white_points_wons


    @property
    def number_of_black_all_wons(self):
        """黒の勝利数"""
        return self.number_of_black_fully_wons + self.number_of_black_points_wons


    @property
    def number_of_white_all_wons(self):
        """白の勝利数"""
        return self.number_of_white_fully_wons + self.number_of_white_points_wons


    @property
    def number_of_draw_series_ft(self):
        """引分けで終わったシリーズ数"""
        return self.number_of_series - self.number_of_black_all_wons - self.number_of_white_all_wons


    @property
    def trial_black_win_rate_without_draw(self):
        """試行した結果、［黒が勝つ確率］
        
        引分けを除いて計算する
        """
        return self.number_of_black_all_wons / (self.number_of_series - self.number_of_draw_series_ft)


    @property
    def trial_black_win_rate_error_without_draw(self):
        """試行した結果、［黒が勝つ確率と0.5との誤差］
        
        引分けを除いて計算する
        """
        return self.trial_black_win_rate_without_draw - 0.5


    @property
    def trial_draw_rate_ft(self):
        """試行した結果、［引き分ける確率］"""
        return self.number_of_draw_series_ft / self.number_of_series


    # ［先後交互制］
    # -------------


    @property
    def number_of_alice_fully_wons(self):
        """Ａさんが［目標の点数］を集めて勝った回数"""
        if self._number_of_alice_fully_wons is None:
            self._number_of_alice_fully_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_alice_fully_won:
                    self._number_of_alice_fully_wons += 1

        return self._number_of_alice_fully_wons


    @property
    def number_of_bob_fully_wons(self):
        """Ｂさんが［目標の点数］を集めて勝った回数"""
        if self._number_of_bob_fully_wons is None:
            self._number_of_bob_fully_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_bob_fully_won:
                    self._number_of_bob_fully_wons += 1

        return self._number_of_bob_fully_wons


    @property
    def number_of_alice_points_wons(self):
        """Ａさんが［勝ち点差判定］で勝った回数"""
        if self._number_of_alice_points_wons is None:
            self._number_of_alice_points_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_alice_points_won:
                    self._number_of_alice_points_wons += 1

        return self._number_of_alice_points_wons


    @property
    def number_of_bob_points_wons(self):
        """Ｂさんが［勝ち点差判定］で勝った回数"""
        if self._number_of_bob_points_wons is None:
            self._number_of_bob_points_wons = 0
            for series_result in self._series_result_list:
                if series_result.is_bob_points_won:
                    self._number_of_bob_points_wons += 1

        return self._number_of_bob_points_wons


    @property
    def number_of_alice_all_wons(self):
        """Ａさんの勝利数"""
        return self.number_of_alice_fully_wons + self.number_of_alice_points_wons


    @property
    def number_of_bob_all_wons(self):
        """Ｂさんの勝利数"""
        return self.number_of_bob_fully_wons + self.number_of_bob_points_wons


    @property
    def number_of_draw_series_at(self):
        """引分けで終わったシリーズ数"""
        return self.number_of_series - self.number_of_alice_all_wons - self.number_of_bob_all_wons


    @property
    def trial_alice_win_rate_without_draw(self):
        """試行した結果、［Ａさんが勝つ確率］
        
        引分けを除いて計算する
        """
        return self.number_of_alice_all_wons / (self.number_of_series - self.number_of_draw_series_at)

    @property
    def trial_alice_win_rate_error_without_draw(self):
        """試行した結果、［Ａさんが勝つ確率］
        
        引分けを除いて計算する
        """
        return self.trial_alice_win_rate_without_draw - 0.5


    @property
    def trial_draw_rate_at(self):
        """試行した結果、［引き分ける確率］"""
        return self.number_of_draw_series_at / self.number_of_series

