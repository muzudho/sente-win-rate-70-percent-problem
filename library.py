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


# 配列の未使用インデックスに使う
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


def coin(p, draw_rate=0.0):
    """コインを投げて、表が出るか、裏が出るか、表も裏も出なかったかのいずれかを返す。
    このコインは表が黒く（BLACK）塗られており、裏は白く（WHITE）塗られている。
    表も裏もでない（EMPTY）ケースも確率で指定することができる。

    Parameters
    ----------
    p : float
        表が出る確率。例： 表が７割出るなら 0.7
        ただし、この数は表も裏も出なかった回数を含まない。表と裏の２つのうち表が出る確率を表す
    draw_rate : float
        表も裏も出ない確率。例： １割が引き分けなら 0.1
    
    Returns
    -------
    BLACK : int
        表が出た
    WHITE : int
        裏が出た
    EMPTY : int
        表も裏も出なかった
    """

    # 表も裏もでない確率
    if draw_rate != 0.0 and random.random() < draw_rate:
        return EMPTY

    if random.random() < p:
        return BLACK

    return WHITE


class PseudoSeriesResult():
    """疑似的にシリーズのコイントスした結果"""


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
            コイントスした結果のリスト。引き分け含む
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
        """コイントスした結果のリスト。引き分け含む"""
        return self._successful_color_list


    @staticmethod
    def playout_pseudo(p, draw_rate, longest_times):
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

            color = coin(p)

            # 引分け
            if color == EMPTY:
                successful_color_list.append(EMPTY)

            # 黒勝ち、または白勝ちのどちらか
            else:
                successful_color_list.append(color)


        return PseudoSeriesResult(
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


def make_all_pseudo_series_results_when_frozen_turn(can_draw, pts_conf):
    """TODO ［先後固定制］での１シリーズについて、フル対局分の、全パターンのコイントスの結果を作りたい
    
    １タイムは　勝ち、負けの２つ、または　勝ち、負け、引き分けの３つ。

    Returns
    -------
    pts_conf : PointsConfiguration
        ［勝ち点ルール］の構成
    power_set_list : list
        勝った方の色（引き分け含む）のリストが全パターン入っているリスト
    """

    # 要素数
    if can_draw:
        # 黒勝ち、白勝ち、勝者なしの３要素
        elements = [BLACK, WHITE, EMPTY]
    else:
        # 黒勝ち、白勝ちけの２要素
        elements = [BLACK, WHITE]

    # 桁数
    depth = pts_conf.number_longest_time_when_frozen_turn

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


class PointCalculation():
    """勝ち点計算に使う"""


    def __init__(self, pts_conf):
        """初期化
        
        Parameters
        ----------
        pts_conf : PointsConfiguration
            ［勝ち点ルール］の構成
        """

        self._pts_conf = pts_conf

        # ［勝ち点］のリスト。要素は、未使用、黒番、白番、Ａさん、Ｂさん
        self._point_list = [0, 0, 0, 0, 0]


    @property
    def pts_conf(self):
        """［勝ち点ルール］の構成"""
        return self._pts_conf


    @property
    def point_list(self):
        """［勝ち点］のリスト。要素は、未使用、黒番、白番、Ａさん、Ｂさん"""
        return self._point_list


    @staticmethod
    def get_successful_player(successful_color, time_th, is_alternating_turn):

        # ［先後交互制］
        if is_alternating_turn:
            # 黒が出た
            if successful_color == BLACK:

                # 奇数本で黒番のプレイヤーはＡさん
                if time_th % 2 == 1:
                    return ALICE

                # 偶数本で黒番のプレイヤーはＢさん
                return BOB

            # 白が出た

            # 奇数本で白番のプレイヤーはＢさん
            if time_th % 2 == 1:
                return BOB

            # 偶数本で白番のプレイヤーはＡさん
            return ALICE

        # ［先後固定制］
        if successful_color == BLACK:
            return ALICE

        return BOB


    def append_won(self, successful_color, time_th, is_alternating_turn):
        """加点

        Parameters
        ----------
        """

        successful_player = PointCalculation.get_successful_player(successful_color, time_th, is_alternating_turn)

        # 黒が出た
        if successful_color == BLACK:
            step = self._pts_conf.b_step
        # 白が出た
        else:
            step = self._pts_conf.w_step


        self._point_list[successful_color] += step
        self._point_list[successful_player] += step


    def append_draw(self, time_th, is_alternating_turn):
        """TODO 引分け。全員に、以下の点を加点します（勝ち点が実数になるので計算機を使ってください）

        引分け時の勝ち点 = 勝ち点 * ( 1 - 将棋の引分け率 ) / 2
        """

        self._point_list[BLACK] += self._pts_conf.b_step_when_draw
        self._point_list[WHITE] += self._pts_conf.w_step_when_draw

        # 奇数回はＡさんが先手
        if time_th % 2 == 1:
            self._point_list[ALICE] += self._pts_conf.b_step_when_draw
            self._point_list[BOB] += self._pts_conf.w_step_when_draw

        # 偶数回はＢさんが先手
        else:
            self._point_list[BOB] += self._pts_conf.b_step_when_draw
            self._point_list[ALICE] += self._pts_conf.w_step_when_draw


    def get_point_of(self, index):
        return self._point_list[index]


    def is_fully_won(self, index):
        """点数を満たしているか？"""
        return self._pts_conf.span <= self.get_point_of(index)


    def x_has_more_than_y(self, x, y):
        """xの方がyより勝ち点が多いか？"""
        return self.get_point_of(y) < self.get_point_of(x)



def judge_series_when_frozen_turn(pseudo_series_result, pts_conf):
    """１シリーズ分の疑似対局結果を読み取ります。［先後固定制］で判定します。

    ［勝ち点差判定］や［タイブレーク］など、決着が付かなかったときの処理は含みません
    もし、引き分けがあれば、［引き分けを１局として数えるケース］です。

    Parameters
    ----------
    pseudo_series_result : PseudoSeriesResult
        コイントス・リスト
    pts_conf : PointsConfiguration
        ［かくきんシステムのｐの構成］
    
    Returns
    -------
    series_result : SeriesResult
        ［シリーズ］の結果
    """

    # ［勝ち点計算］
    point_calculation = PointCalculation(pts_conf=pts_conf)

    # ［このシリーズで引き分けた対局数］
    number_of_draw_times = 0

    time_th = 0

    # 予め作った１シリーズ分の対局結果を読んでいく
    for successful_color in pseudo_series_result.successful_color_list:
        time_th += 1

        # 引き分けを１局と数えるケース
        #
        #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
        #
        if successful_color == EMPTY:
            number_of_draw_times += 1

            point_calculation.append_draw(time_th, is_alternating_turn=False)
        
        else:
            point_calculation.append_won(successful_color, time_th, is_alternating_turn=False)

            # 勝ち抜け
            if pts_conf.span <= point_calculation.get_point_of(successful_color):

                # コイントスの結果のリストの長さを切ります。
                # 対局は必ずしも［最長対局数］になるわけではありません
                pseudo_series_result.cut_down(time_th)

                return SeriesResult(
                        number_of_all_times=time_th,
                        number_of_draw_times=number_of_draw_times,
                        span=pts_conf.span,
                        point_calculation=point_calculation,
                        pseudo_series_result=pseudo_series_result)


    # タイブレークをするかどうかは、この関数の呼び出し側に任せます
    return SeriesResult(
            number_of_all_times=time_th,
            number_of_draw_times=number_of_draw_times,
            span=pts_conf.span,
            point_calculation=point_calculation,
            pseudo_series_result=pseudo_series_result)


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

    color = coin(p, draw_rate) 

    # 引き分けなら白勝ち
    if color == EMPTY:
        return WHITE

    else:
        return color


def play_game_when_alternating_turn(pseudo_series_result, pts_conf):
    """［先後交互制］で１対局行う（どちらの勝ちが出るまでコイントスを行う）
    
    Parameters
    ----------
    pts_conf : PointsConfiguration
        ［かくきんシステムのｐの構成］
    
    Returns
    -------
    series_result : SeriesResult
        ［シリーズ］の結果
    """

    # ［勝ち点計算］
    point_calculation = PointCalculation(pts_conf=pts_conf)

    # ［このシリーズで引き分けた対局数］
    number_of_draw_times = 0

    time_th = 0

    # 予め作った１シリーズ分の対局結果を読んでいく
    for successful_color in pseudo_series_result.successful_color_list:
        time_th += 1

        # 引き分けを１局と数えるケース
        #
        #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
        #
        if successful_color == EMPTY:
            number_of_draw_times += 1

            point_calculation.append_draw(time_th, is_alternating_turn=True)

        else:
            successful_player = PointCalculation.get_successful_player(successful_color, time_th, is_alternating_turn=True)

            point_calculation.append_won(successful_color, time_th, is_alternating_turn=True)

            # 勝ち抜け
            if pts_conf.span <= point_calculation.get_point_of(successful_player):

                # コイントスの結果のリストの長さを切ります。
                # 対局は必ずしも［最長対局数］になるわけではありません
                pseudo_series_result.cut_down(time_th)

                return SeriesResult(
                        number_of_all_times=time_th,
                        number_of_draw_times=number_of_draw_times,
                        span=pts_conf.span,
                        point_calculation=point_calculation,
                        pseudo_series_result=pseudo_series_result)


    # タイブレークをするかどうかは、この関数の呼び出し側に任せます
    return SeriesResult(
            number_of_all_times=time_th,
            number_of_draw_times=number_of_draw_times,
            span=pts_conf.span,
            point_calculation=point_calculation,
            pseudo_series_result=pseudo_series_result)


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


    @staticmethod
    def let_draw_point(draw_rate, step):
        """TODO 引分け時の［勝ち点］の算出。

        引分け時の勝ち点 = 勝ち点 * ( 1 - 将棋の引分け率 ) / 2

        // ２で割ってるのは、両者が１つの勝ちを半分ずつに按分するから。

        例： 勝ち点３で、将棋の引分け率を 0.1 と指定したとき、
        引分け時の勝ち点 = 3 * ( 1 - 0.1 ) / 2 = 1.35

        例： 勝ち点３で、将棋の引分け率を 0.9 と指定したとき、
        引分け時の勝ち点 = 3 * ( 1 - 0.9 ) / 2 = 0.15
        """

        return step * (1 - draw_rate) / 2


    def __init__(self, draw_rate, b_step, w_step, span):
        """初期化
        
        Parameters
        ----------
        draw_rate : float
            ［将棋の引分け率］
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

        self._draw_rate = draw_rate
        self._b_step = b_step
        self._w_step = w_step
        self._span = span

        # 黒番の［引分け時の黒勝ち１つの点数］
        self._b_step_when_draw = PointsConfiguration.let_draw_point(
                draw_rate=draw_rate,
                step=b_step)

        # 白番の［引分け時の白勝ち１つの点数］
        self._w_step_when_draw = PointsConfiguration.let_draw_point(
                draw_rate=draw_rate,
                step=w_step)


    @property
    def draw_rate(self):
        """［将棋の引分け率］"""
        return self._draw_rate


    @property
    def b_step(self):
        """［黒勝ち１つの点数］"""
        return self._b_step


    @property
    def w_step(self):
        """［白勝ち１つの点数］"""
        return self._w_step


    @property
    def b_step_when_draw(self):
        """［引分け時の黒勝ち１つの点数］"""
        return self._b_step_when_draw


    @property
    def w_step_when_draw(self):
        """［引分け時の白勝ち１つの点数］"""
        return self._w_step_when_draw


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
    def let_points_from_repeat(draw_rate, b_time, w_time):
        """［黒勝ちだけでの対局数］と［白勝ちだけでの対局数］が分かれば、［かくきんシステムのｐの構成］を分析して返す
        
        Parameters
        ----------
        draw_rate : float
            ［将棋の引分け率］
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
                draw_rate=draw_rate,
                b_step=b_step,
                w_step=w_step,
                span=span)


    @property
    def number_shortest_time_when_frozen_turn(self):
        """［先後固定制］での［最短対局数］
        
        白が全勝したときの回数と同じ

        `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
            ・  白  白  白  白  白  で、最短５局
            10  10  10  10 10  10
            10   8   6   4  2   0
        """
        return self.w_time


    @property
    def number_longest_time_when_frozen_turn(self):
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


    def __init__(self, number_of_all_times, number_of_draw_times, span, point_calculation, pseudo_series_result):
        """初期化
    
        Parameters
        ----------
        number_of_all_times : int
            行われた対局数
        number_of_draw_times : int
            引分けだった対局数
        span : int
            ［目標の点数］
        point_calculation : PointCalculation
            ［勝ち点計算］
        pseudo_series_result : PseudoSeriesResult
            １シリーズ分をフルにコイントスした結果
        """

        # 共通
        self._number_of_all_times = number_of_all_times
        self._number_of_draw_times = number_of_draw_times
        self._span = span
        self._point_calculation = point_calculation
        self._pseudo_series_result = pseudo_series_result


    # 共通
    # ----

    @property
    def point_calculation(self):
        """［勝ち点計算］"""
        return self._point_calculation


    @property
    def number_of_all_times(self):
        """行われた対局数"""
        return self._number_of_all_times


    @property
    def number_of_draw_times(self):
        """引分けだった対局数"""
        return self._number_of_draw_times


    @property
    def pseudo_series_result(self):
        """１シリーズ分をフルにコイントスした結果"""
        return self._pseudo_series_result


    def is_points_won(self, winner, loser):
        """winner の［勝ち点］は［目標の点数］に達していないが、 loser の［勝ち点］より多くて winner さんの勝ち"""
        return not self._point_calculation.is_fully_won(winner) and self._point_calculation.x_has_more_than_y(winner, loser)


    def is_won(self, winner, loser):
        """winner さんの勝ち"""
        return self.point_calculation.is_fully_won(winner) or self.is_points_won(winner=winner, loser=loser)


    # ［先後固定制］
    # -------------

    @property
    def is_black_won(self):
        """黒勝ち"""
        return self.point_calculation.is_fully_won(BLACK) or self.is_points_won(winner=BLACK, loser=WHITE)


    @property
    def is_white_won(self):
        """白勝ち"""
        return self.point_calculation.is_fully_won(WHITE) or self.is_points_won(winner=WHITE, loser=BLACK)


    # ［先後交互制］
    # -------------

    def is_no_won(self, x, y):
        """勝者なし。 x 、 y の［勝ち点］が等しいとき"""
        return self._point_calculation.get_point_of(x) == self._point_calculation.get_point_of(y)


class LargeSeriesTrialSummary():
    """大量のシリーズを試行した結果"""


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

        # ［満点勝ち］の件数。 未使用、黒、白、Ａさん、Ｂさんの順。初期値は None
        self._number_of_fully_wons = [None, None, None, None, None]

        # ［勝ち点判定勝ち］の件数。 未使用、黒、白、Ａさん、Ｂさんの順。初期値は None
        self._number_of_points_wons = [None, None, None, None, None]


        # 「先後固定制］
        # -------------
        self._number_of_no_wons_color = None


        # ［先後交互制］
        # -------------
        self._number_of_no_wons_player = None


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


    def number_of_fully_wons(self, index):
        """Ａさんが［目標の点数］を集めて勝った回数"""
        if self._number_of_fully_wons[index] is None:
            self._number_of_fully_wons[index] = 0
            for series_result in self._series_result_list:
                if series_result.point_calculation.is_fully_won(index):
                    self._number_of_fully_wons[index] += 1

        return self._number_of_fully_wons[index]


    def number_of_points_wons(self, winner, loser):
        """winner が［勝ち点差判定］で loser に勝った回数"""
        if self._number_of_points_wons[winner] is None:
            self._number_of_points_wons[winner] = 0
            for series_result in self._series_result_list:
                if series_result.is_points_won(winner=winner, loser=loser):
                    self._number_of_points_wons[winner] += 1

        return self._number_of_points_wons[winner]


    # 「先後固定制］
    # -------------


    @property
    def number_of_no_wons_color(self):
        """［先後固定制］で勝者がなかった回数"""
        if self._number_of_no_wons_color is None:
            self._number_of_no_wons_color = 0
            for series_result in self._series_result_list:
                if series_result.is_no_won(BLACK, WHITE):
                    self._number_of_no_wons_color += 1

        return self._number_of_no_wons_color


    def number_of_all_wons(self, winner, loser):
        """winner が loser に勝った数"""
        return self.number_of_fully_wons(winner) + self.number_of_points_wons(winner=winner, loser=loser)


    @property
    def number_of_draw_series_ft(self):
        """引分けで終わったシリーズ数"""
        return self.number_of_series - self.number_of_all_wons(winner=BLACK, loser=WHITE) - self.number_of_all_wons(winner=WHITE, loser=BLACK)


    def win_rate_without_draw_ft(self, winner, loser):
        """試行した結果、 winner が loser に勝つ確率
        
        引分けを除いて計算する
        """
        return self.number_of_all_wons(winner=winner, loser=loser) / (self.number_of_series - self.number_of_draw_series_ft)


    def win_rate_error_without_draw_ft(self, winner, loser):
        """試行した結果、 winner が loser に勝つ確率と0.5との誤差］
        
        引分けを除いて計算する
        """
        return self.win_rate_without_draw_ft(winner=winner, loser=loser) - 0.5


    @property
    def draw_rate_ft(self):
        """試行した結果、［引き分ける確率］"""
        return self.number_of_draw_series_ft / self.number_of_series


    # ［先後交互制］
    # -------------


    @property
    def number_of_no_wons_player(self):
        """［先後交代制］で勝者がなかった回数"""
        if self._number_of_no_wons_player is None:
            self._number_of_no_wons_player = 0
            for series_result in self._series_result_list:
                if series_result.is_no_won(ALICE, BOB):
                    self._number_of_no_wons_player += 1

        return self._number_of_no_wons_player


    @property
    def number_of_draw_series_at(self):
        """引分けで終わったシリーズ数"""
        return self.number_of_series - self.number_of_all_wons(winner=ALICE, loser=BOB) - self.number_of_all_wons(winner=BOB, loser=ALICE)


    def win_rate_without_draw_at(self, winner, loser):
        """試行した結果、［Ａさんが勝つ確率］
        
        引分けを除いて計算する
        """
        return self.number_of_all_wons(winner=winner, loser=loser) / (self.number_of_series - self.number_of_draw_series_at)


    def win_rate_error_without_draw_at(self, winner, loser):
        """試行した結果、［Ａさんが勝つ確率］
        
        引分けを除いて計算する
        """
        return self.win_rate_without_draw_at(winner=winner, loser=loser) - 0.5


    @property
    def draw_rate_at(self):
        """試行した結果、［引き分ける確率］"""
        return self.number_of_draw_series_at / self.number_of_series

