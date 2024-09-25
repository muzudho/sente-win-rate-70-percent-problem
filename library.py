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


# Elementary event
# ----------------

# 配列の未使用インデックスに使う
EMPTY = 0

#   Face of coin
#   ------------

# 表。表。先手。配列のインデックスに使う
HEAD = 1

# 裏。裏。後手。配列のインデックスに使う
TAIL = 2

#   Players
#   -------

# Ａさん。配列のインデックスに使う
ALICE = 3

# Ｂさん。配列のインデックスに使う
BOB = 4


# Challenged
# ----------

# ［コインを投げて表か裏が出た］
SUCCESSFUL = 1

# ［コインを投げて表も裏も出なかった］
FAILED = 2


# Turn system
# -----------

# ［先後固定制］。配列のインデックスに使う
WHEN_FROZEN_TURN = 1

# ［先後交互制］。配列のインデックスに使う
WHEN_ALTERNATING_TURN = 2


# Opponent pair
# -------------

# ［コインの表と裏］。配列のインデックスに使う
FACE_OF_COIN = 1

# ［ＡさんとＢさん］。配列のインデックスに使う
PLAYERS = 2


class Specification():
    """仕様"""


    def __init__(self, p, failure_rate, turn_system):
        """初期化

        Parameters
        ----------
        p : float
            ［表が出る確率］
        failure_rate : float
            ［表も裏も出ない確率］。例： １割が引き分けなら 0.1
        turn_system : int
            ［先後運営制度］
        """

        self._p = p
        self._failure_rate = failure_rate
        self._turn_system = turn_system


    @property
    def p(self):
        """［表が出る確率］"""
        return self._p


    @property
    def failure_rate(self):
        """［表も裏も出ない確率］"""
        return self._failure_rate


    @property
    def turn_system(self):
        """［先後運営制度］"""
        return self._turn_system



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


def p_to_b_q_times(p):
    """［表が出る確率］ p を与えると、［表勝ちだけでの対局数］、［裏勝ちだけでの対局数］を返す
    
    Parameters
    ----------
    p : float
        ［表が出る確率］
    
    Returns
    -------
    p_time : int
        ［表勝ちだけでの対局数］
    q_time : int
        ［裏勝ちだけでの対局数］
    """

    # 説明２  コインの表裏の確率の整数化
    # --------------------------------
    scale = scale_for_float_to_int(p)

    # ［表勝ちだけでの対局数］基礎
    #
    #   NOTE int() を使って小数点以下切り捨てしようとすると、57 が 56 になったりするので、四捨五入にする
    #
    p_time = round_letro(p * scale)

    # ［裏勝ちだけでの対局数］基礎
    q_time = scale - p_time

    # 約分する
    fraction = Fraction(p_time, q_time)
    return fraction.numerator, fraction.denominator


def toss_a_coin(p, failure_rate=0.0):
    """コインを投げて、表が出るか、裏が出るか、表も裏も出なかったかのいずれかを返す。

    Parameters
    ----------
    p : float
        表が出る確率。例： 表が７割出るなら 0.7
        ただし、この数は表も裏も出なかった回数を含まない。表と裏の２つのうち表が出る確率を表す
    failure_rate : float
        ［表も裏も出ない確率］。例： １割が引き分けなら 0.1
    
    Returns
    -------
    elementary_event : int
        HEAD（表が出た）、TAIL（裏が出た）、EMPTY（表も裏も出なかった）のいずれか        
    """

    # 表も裏もでない確率
    if failure_rate != 0.0 and random.random() < failure_rate:
        return EMPTY

    if random.random() < p:
        return HEAD

    return TAIL


class PseudoSeriesResult():
    """疑似的にシリーズのコイントスした結果"""


    def __init__(self, p, failure_rate, longest_times, face_of_coin_list):
        """初期化

        Parameters
        ----------
        p : float
            ［表が出る確率］ 例： ７割なら 0.7
        failure_rate : float
            ［将棋の引分け率】 例： １割の確率で引き分けになるのなら 0.1
        longest_times : int
            ［最長対局数］
        face_of_coin_list : list
            コイントスした結果のリスト。引き分け含む
        """
        self._p = p,
        self._failure_rate = failure_rate
        self._longest_times = longest_times
        self._face_of_coin_list = face_of_coin_list


    @property
    def p(self):
        """［表が出る確率］"""
        return self._p


    @property
    def failure_rate(self):
        """［引き分ける確率］"""
        return self._failure_rate


    @property
    def longest_times(self):
        """最長対局数］"""
        return self._longest_times


    @property
    def face_of_coin_list(self):
        """コイントスした結果のリスト。引き分け含む"""
        return self._face_of_coin_list


    @staticmethod
    def playout_pseudo(p, failure_rate, longest_times):
        """１シリーズをフルに対局したときのコイントスした結果の疑似リストを生成

        Parameters
        ----------
        p : float
            ［表が出る確率］
        failure_rate : float
            ［引き分ける確率］
        longest_times : int
            ［最長対局数］
        """

        face_of_coin_list = []

        # ［最長対局数］までやる
        for time_th in range(1, longest_times + 1):

            elementary_event = toss_a_coin(
                    p=p,
                    failure_rate=failure_rate)

            face_of_coin_list.append(elementary_event)


        return PseudoSeriesResult(
                p=p,
                failure_rate=failure_rate,
                longest_times=longest_times,
                face_of_coin_list=face_of_coin_list)


    def cut_down(self, number_of_times):
        """コイントスの結果のリストの長さを切ります。
        対局は必ずしも［最長対局数］になるわけではありません"""
        self._face_of_coin_list = self._face_of_coin_list[0:number_of_times]


    def stringify_dump(self, indent):
        """ダンプ"""
        return f"""\
{indent}PseudoSeriesResult
{indent}------------------
{indent}{indent}{self._p=}
{indent}{indent}{self._failure_rate=}
{indent}{indent}{self._longest_times=}
{indent}{indent}{self._face_of_coin_list=}
"""


def make_all_pseudo_series_results(can_draw, pts_conf, turn_system):
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
        # 表勝ち、裏勝ち、勝者なしの３要素
        elements = [HEAD, TAIL, EMPTY]
    else:
        # 表勝ち、裏勝ちけの２要素
        elements = [HEAD, TAIL]

    # 桁数
    depth = pts_conf.number_longest_time(turn_system=turn_system)

    # １シーズン分のコイントスの全ての結果
    stats = []

    position = []


    def search(depth, stats, position, can_draw):

        # 表勝ちを追加
        position.append(HEAD)

        # スタッツに、ポジションのコピーを追加
        stats.append(list(position))

        if 0 < depth:
            search(depth - 1, stats, position, can_draw=False)

        # 末尾の要素を削除
        position.pop()


        # 裏勝ちを追加
        position.append(TAIL)

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

        # ［勝ち点］のリスト。要素は、未使用、表番、裏番、Ａさん、Ｂさん
        self._point_list = [0, 0, 0, 0, 0]


    @property
    def pts_conf(self):
        """［勝ち点ルール］の構成"""
        return self._pts_conf


    @property
    def point_list(self):
        """［勝ち点］のリスト。要素は、未使用、表番、裏番、Ａさん、Ｂさん"""
        return self._point_list


    @staticmethod
    def get_successful_player(elementary_event, time_th, turn_system):

        # ［先後交互制］
        if turn_system == WHEN_ALTERNATING_TURN:
            # 表が出た
            if elementary_event == HEAD:

                # 奇数本で表番のプレイヤーはＡさん
                if time_th % 2 == 1:
                    return ALICE

                # 偶数本で表番のプレイヤーはＢさん
                return BOB

            # 裏が出た
            if elementary_event == TAIL:

                # 奇数本で裏番のプレイヤーはＢさん
                if time_th % 2 == 1:
                    return BOB

                # 偶数本で裏番のプレイヤーはＡさん
                return ALICE

            # 表も裏も出なかった
            if elementary_event == EMPTY:
                return EMPTY

            raise ValueError(f"{elementary_event=}")

        # ［先後固定制］
        if turn_system == WHEN_FROZEN_TURN:
            if elementary_event == HEAD:
                return ALICE

            if elementary_event == TAIL:
                return BOB

            # 表も裏も出なかった
            if elementary_event == EMPTY:
                return EMPTY

            raise ValueError(f"{elementary_event=}")


        raise ValueError(f"{turn_system=}")


    def append_won(self, successful_face_of_coin, time_th, turn_system):
        """加点

        Parameters
        ----------
        successful_face_of_coin : int
            ［コインの表か裏］
        """

        successful_player = PointCalculation.get_successful_player(successful_face_of_coin, time_th, turn_system)

        # ［勝ち点］
        step = self._pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=successful_face_of_coin)


        self._point_list[successful_face_of_coin] += step
        self._point_list[successful_player] += step


    def append_draw(self, time_th, turn_system):
        """TODO 引分け。全員に、以下の点を加点します（勝ち点が実数になるので計算機を使ってください）

        引分け時の勝ち点 = 勝ち点 * ( 1 - 将棋の引分け率 ) / 2
        """

        self._point_list[HEAD] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=HEAD)      # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
        self._point_list[TAIL] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=TAIL)      # ［コインの表も裏も出なかったときの、表番の方の勝ち点］

        if turn_system == WHEN_FROZEN_TURN:
            self._point_list[ALICE] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=HEAD)     # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
            self._point_list[BOB] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=TAIL)       # ［コインの表も裏も出なかったときの、表番の方の勝ち点］

        elif turn_system == WHEN_ALTERNATING_TURN:
            # 奇数回はＡさんが先手
            if time_th % 2 == 1:
                self._point_list[ALICE] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=HEAD)     # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
                self._point_list[BOB] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=TAIL)       # ［コインの表も裏も出なかったときの、表番の方の勝ち点］

            # 偶数回はＢさんが先手
            else:
                self._point_list[BOB] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=HEAD)       # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
                self._point_list[ALICE] += self._pts_conf.get_step_by(challenged=FAILED, face_of_coin=TAIL)     # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
            
        else:
            raise ValueError(f"{turn_system=}")


    def get_point_of(self, index):
        return self._point_list[index]


    def is_fully_won(self, index):
        """点数を満たしているか？"""
        return self._pts_conf.span <= self.get_point_of(index)


    def x_has_more_than_y(self, x, y):
        """xの方がyより勝ち点が多いか？"""
        return self.get_point_of(y) < self.get_point_of(x)


    def stringify_dump(self, indent):
        double_indent = indent + indent
        return f"""\
{indent}PointCalculation
{indent}----------------
{indent}{indent}self._pts_conf:
{self._pts_conf.stringify_dump(double_indent)}
{indent}{indent}{self._point_list=}
"""


def play_tie_break(p, failure_rate):
    """［タイブレーク］を行います。１局勝負で、引き分けの場合は裏勝ちです。

    Parameters
    ----------
    p : float
        ［表が出る確率］ 例： ７割なら 0.7
    failure_rate : float
        ［将棋の引分け率】 例： １割の確率で引き分けになるのなら 0.1
    
    Returns
    -------
    winner_color : int
        勝った方の色。引き分けなら裏勝ち
    """

    elementary_event = toss_a_coin(p, failure_rate) 

    # 引き分けなら裏勝ち
    if elementary_event == EMPTY:
        return TAIL

    else:
        return elementary_event


def judge_series(pseudo_series_result, pts_conf, turn_system):
    if turn_system == WHEN_FROZEN_TURN:
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
        number_of_failed = 0

        time_th = 0

        # 予め作った１シリーズ分の対局結果を読んでいく
        for face_of_coin in pseudo_series_result.face_of_coin_list:
            time_th += 1

            # 引き分けを１局と数えるケース
            #
            #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
            #
            if face_of_coin == EMPTY:
                number_of_failed += 1

                point_calculation.append_draw(time_th, turn_system=WHEN_FROZEN_TURN)
            
            else:
                point_calculation.append_won(
                    successful_face_of_coin=face_of_coin,
                    time_th=time_th,
                    turn_system=WHEN_FROZEN_TURN)

                # 勝ち抜け
                if pts_conf.span <= point_calculation.get_point_of(face_of_coin):

                    # コイントスの結果のリストの長さを切ります。
                    # 対局は必ずしも［最長対局数］になるわけではありません
                    pseudo_series_result.cut_down(time_th)

                    return SeriesResult(
                            number_of_times=time_th,
                            number_of_failed=number_of_failed,
                            span=pts_conf.span,
                            point_calculation=point_calculation,
                            pseudo_series_result=pseudo_series_result)


        # タイブレークをするかどうかは、この関数の呼び出し側に任せます
        return SeriesResult(
                number_of_times=time_th,
                number_of_failed=number_of_failed,
                span=pts_conf.span,
                point_calculation=point_calculation,
                pseudo_series_result=pseudo_series_result)


    if turn_system == WHEN_ALTERNATING_TURN:
        """［先後交互制］で１対局行う（どちらの勝ちが出るまでコイントスを行う）
        
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
        number_of_failed = 0

        time_th = 0

        # 予め作った１シリーズ分の対局結果を読んでいく
        for face_of_coin in pseudo_series_result.face_of_coin_list:
            time_th += 1

            # 引き分けを１局と数えるケース
            #
            #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
            #
            if face_of_coin == EMPTY:
                number_of_failed += 1

                point_calculation.append_draw(time_th, turn_system=WHEN_ALTERNATING_TURN)

            else:
                successful_player = PointCalculation.get_successful_player(face_of_coin, time_th, turn_system=WHEN_ALTERNATING_TURN)

                point_calculation.append_won(
                        successful_face_of_coin=face_of_coin,
                        time_th=time_th,
                        turn_system=WHEN_ALTERNATING_TURN)

                # 勝ち抜け
                if pts_conf.span <= point_calculation.get_point_of(successful_player):

                    # コイントスの結果のリストの長さを切ります。
                    # 対局は必ずしも［最長対局数］になるわけではありません
                    pseudo_series_result.cut_down(time_th)

                    return SeriesResult(
                            number_of_times=time_th,
                            number_of_failed=number_of_failed,
                            span=pts_conf.span,
                            point_calculation=point_calculation,
                            pseudo_series_result=pseudo_series_result)


        # タイブレークをするかどうかは、この関数の呼び出し側に任せます
        return SeriesResult(
                number_of_times=time_th,
                number_of_failed=number_of_failed,
                span=pts_conf.span,
                point_calculation=point_calculation,
                pseudo_series_result=pseudo_series_result)


    raise ValueError(f"{turn_system=}")


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
    def let_draw_point(failure_rate, step):
        """TODO 引分け時の［勝ち点］の算出。

        引分け時の勝ち点 = 勝ち点 * ( 1 - 将棋の引分け率 ) / 2

        // ２で割ってるのは、両者が１つの勝ちを半分ずつに按分するから。

        例： 勝ち点３で、将棋の引分け率を 0.1 と指定したとき、
        引分け時の勝ち点 = 3 * ( 1 - 0.1 ) / 2 = 1.35

        例： 勝ち点３で、将棋の引分け率を 0.9 と指定したとき、
        引分け時の勝ち点 = 3 * ( 1 - 0.9 ) / 2 = 0.15
        """

        return step * (1 - failure_rate) / 2


    def __init__(self, failure_rate, p_step, q_step, span, turn_system):
        """初期化
        
        Parameters
        ----------
        failure_rate : float
            ［将棋の引分け率］
        p_step : int
            ［表勝ち１つの点数］
        q_step : int
            ［裏勝ち１つの点数］
        span : int
            ［目標の点数］
        """

        # NOTE numpy.int64 型は、 float NaN が入っていることがある？
        if not isinstance(p_step, int):
            raise ValueError(f"int 型であることが必要 {type(p_step)=}  {p_step=}")

        if not isinstance(q_step, int):
            raise ValueError(f"int 型であることが必要 {type(q_step)=}  {q_step=}")

        if not isinstance(span, int):
            raise ValueError(f"int 型であることが必要 {type(span)=}  {span=}")

        if p_step < 1:
            raise ValueError(f"正の整数であることが必要 {p_step=}  {p_step=}")

        if q_step < 1:
            raise ValueError(f"正の整数であることが必要 {q_step=}  {q_step=}")

        if span < 1:
            raise ValueError(f"正の整数であることが必要 {span=}  {span=}")

        if q_step < p_step:
            raise ValueError(f"［コインの表が出たときの勝ち点］{p_step=} が、［コインの裏が出たときの勝ち点］ {q_step} を上回るのはおかしいです")

        if span < q_step:
            raise ValueError(f"［コインの裏が出たときの勝ち点］{q_step=} が、［目標の点数］{span} を上回るのはおかしいです")

        self._failure_rate = failure_rate
        self._span = span

        p_step_when_failed = PointsConfiguration.let_draw_point(
                failure_rate=failure_rate,
                step=p_step)

        q_step_when_failed = PointsConfiguration.let_draw_point(
                failure_rate=failure_rate,
                step=q_step)

        if q_step_when_failed < p_step_when_failed:
            raise ValueError(f"［コインの表も裏も出なかったときの、表番の方の勝ち点］{p_step_when_failed=} が、［コインの表も裏も出なかったときの、裏番の方の勝ち点］ {q_step_when_failed} を上回るのはおかしいです")

        self._step_list = [
                # 0: ［未使用］
                None,
                # 1: ［コインの表も裏も出なかったときの、表番の方の勝ち点］
                p_step_when_failed,
                # 2: ［コインの表も裏も出なかったときの、裏番の方の勝ち点］
                q_step_when_failed,
                # 3: ［コインの表が出たときの勝ち点］
                p_step,
                # 4: ［コインの裏が出たときの勝ち点］
                q_step]


    @property
    def failure_rate(self):
        """［将棋の引分け率］"""
        return self._failure_rate


    def get_step_by(self, challenged, face_of_coin):
        """［勝ち点］を取得します
        
        Parameters
        ----------
        challenged : int
            ［成功か失敗］
        face_of_coin : int
            ［コインの表か裏かそれ以外］
        """

        if challenged == FAILED:
            # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
            if face_of_coin == HEAD:
                return self._step_list[1]
            
            # ［コインの表も裏も出なかったときの、裏番の方の勝ち点］
            if face_of_coin == TAIL:
                return self._step_list[2]
            
            raise ValueError(f"{face_of_coin=}")


        elif challenged == SUCCESSFUL:
            # ［コインの表が出たときの勝ち点］
            if face_of_coin == HEAD:
                return self._step_list[3]

            # ［コインの裏が出たときの勝ち点］
            if face_of_coin == TAIL:
                return self._step_list[4]

            raise ValueError(f"{face_of_coin=}")


        raise ValueError(f"{challenged=}")


    @property
    def span(self):
        """［目標の点数］"""
        return self._span


    # p_time, q_time
    def get_time_by(self, challenged, face_of_coin):
        """［対局数］を取得
        """

        if challenged == SUCCESSFUL:
            if face_of_coin == HEAD:
                """
                筆算
                ----
                `10表 12裏 14目（先後固定制）`
                    ・  表  表  で最長２局
                    14  14  14
                    14   4  -6
                """

                #
                #   NOTE 切り上げても .00001 とか .99999 とか付いているかもしれない？から、四捨五入して整数に変換しておく
                #
                return round_letro(math.ceil(self._span / self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)))

            elif face_of_coin == TAIL:
                """［裏勝ちだけでの対局数］

                筆算
                ----
                `10表 12裏 14目（先後固定制）`
                    ・  裏  で最長１局
                    14   0
                    14  14
                """

                #
                #   NOTE 切り上げても .00001 とか .99999 とか付いているかもしれない？から、四捨五入して整数に変換しておく
                #
                return round_letro(math.ceil(self._span / self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)))

            else:
                raise ValueError(f"{face_of_coin=}")
        else:
            raise ValueError(f"{challenged=}")


    @staticmethod
    def let_points_from_time(failure_rate, p_time, q_time, turn_system):
        """［表勝ちだけでの対局数］と［裏勝ちだけでの対局数］が分かれば、［かくきんシステムのｐの構成］を分析して返す
        
        Parameters
        ----------
        failure_rate : float
            ［将棋の引分け率］
        p_time : int
            ［表勝ちだけでの対局数］
        q_time : int
            ［裏勝ちだけでの対局数］
        """
        # DO 通分したい。最小公倍数を求める
        lcm = math.lcm(p_time, q_time)
        # ［表勝ち１つの点数］
        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        p_step = round_letro(lcm / p_time)
        # ［裏勝ち１つの点数］
        q_step = round_letro(lcm / q_time)
        # ［目標の点数］
        span = round_letro(q_time * q_step)

        # データチェック
        span_w = round_letro(p_time * p_step)
        if span != span_w:
            raise ValueError(f"{span=}  {span_w=}")

        return PointsConfiguration(
                failure_rate=failure_rate,
                turn_system=turn_system,
                p_step=p_step,
                q_step=q_step,
                span=span)


    def number_shortest_time(self, turn_system):
        """［最短対局数］"""

        if turn_system == WHEN_FROZEN_TURN:
            """［先後固定制］での［最短対局数］
            
            裏が全勝したときの回数と同じ

            `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
                ・  裏  裏  裏  裏  裏  で、最短５局
                10  10  10  10 10  10
                10   8   6   4  2   0
            """

            return self.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL)

        if turn_system == WHEN_ALTERNATING_TURN:
            """［先後交互制］での［最短対局数］
            
            Ｂさんだけが勝ったときの回数と同じ。

            まず、［目標の点数］が［表勝ち１つの点数］＋［裏勝ち１つの点数］より上回っているなら、［目標の点数］から［表勝ち１つの点数］＋［裏勝ち１つの点数］を順に引いていく（２回分を加算していく）。
            端数が出たら［裏勝ち１つの点数］（１回分）を加算する。
            まだ端数が出たら［表勝ち１つの点数］（１回分）を加算する。
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

            if self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD) + self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL) <= remainder:
                # NOTE なるべく割り算で小数点以下の数がでないように、割り切れる数にしてから割るようにし、整数だけを使って計算する
                new_remainder = self._span % (self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD) + self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL))
                time = math.floor( (remainder - new_remainder) / (self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD) + self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL))) * 2
                remainder = new_remainder

            else:
                time = 0

            # 端数があれば［裏勝ち１つの点数］を引く（１回分を加算）
            #
            #   NOTE 裏（後手）の方が step 値が表（先手）より大きいか、等しいです。［裏勝ち１つの点数］の方から先に引きます
            #
            if 0 < remainder:
                time += 1
                remainder -= self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)

                # まだ端数があれば［表勝ち１つの点数］を引く（１回分を加算）
                if 0 < remainder:
                    time += 1
                    remainder -= self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)

                    # remainder は負数になっているはず（割り切れないはず）
                    if 0 <= remainder:
                        raise ValueError(f"ここで余りが負数になっていないのはおかしい {remainder=}  {self._span=}  {self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)=}  {self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)=}")
                
                # remainder は零か負数になっているはず
                elif 0 < remainder:
                    raise ValueError(f"ここで余りが零か負数になっていないのはおかしい {remainder=}  {self._span=}  {self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)=}  {self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)=}")

            return time


        raise ValueError(f"{turn_system=}")


    def number_longest_time(self, turn_system):
        """［最長対局数］"""

        if turn_system == WHEN_FROZEN_TURN:
            """［先後固定制］での［最長対局数］

            裏があと１つで勝てるところで止まり、表が全勝したときの回数と同じ

            NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、裏と表は何本取ればいいのか明示しなければ、伝わらない
            NOTE 先手が１本、後手が１本取ればいいとき、最大で１本の勝負が行われる（先 or 後）から、１本勝負と呼ぶ
            NOTE 先手が２本、後手が１本取ればいいとき、最大で２本の勝負が行われる（先先 or 先後）から、２本勝負と呼ぶ

            `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
                ・  表  表  表  表  表  表  表  表  表  裏  裏  裏  裏  裏  で、最長１４局
                10   9   8   7   6   5  4   3   2   1  1   1   1   1   1
                10  10  10  10  10  10 10  10  10  10  8   6   4   2   0
            
            `10表 12裏 14目（先後固定制）`
                ・  裏  表  表  で最長３局
                14   2   2   2
                14  14   4  -6
            """
            return  (self.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD) - 1) + (self.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL) - 1) + 1


        if turn_system == WHEN_ALTERNATING_TURN:
            """［先後交互制］での［最長対局数］

            ＡさんとＢさんの両者が先手で勝ち続けた回数と同じ

            筆算
            ----

                理論上 `対局数  5～14（先後固定制）   7～19（先後交互制）    先手勝ち 1点、後手勝ち 2点　目標 10点（先後固定制）`
                    ・  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  Ｂ  Ａ  で、最長１９対局
                    10  9   9   8   8   7   7   6  6   5   5   4   4   3  3   2   2   1   1   0
                    10 10   9   9   8   8   7   7  6   6   5   5   4   4  3   3   2   2   1   1
            
                `0.014715 10表 12裏 14目 1～1局（先後交互制）`
                    ・  Ａ  Ｂ  Ａ  で、最長３局
                    14   4   4  -6
                    14  14   4   4
            """

            return  (self.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD) - 1) + (self.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL) - 1) + 1


        raise ValueError(f"{turn_system=}")


    def stringify_dump(self, indent):
        return f"""\
{indent}PointsConfiguration
{indent}-------------------
{indent}{indent}{self._failure_rate=}
{indent}{indent}{self._span=}
{indent}{indent}{self._step_list=}
"""


class SeriesResult():
    """［シリーズ］の結果"""


    def __init__(self, number_of_times, number_of_failed, span, point_calculation, pseudo_series_result):
        """初期化
    
        Parameters
        ----------
        number_of_times : int
            行われた対局数
        number_of_failed : int
            引分けだった対局数
        span : int
            ［目標の点数］
        point_calculation : PointCalculation
            ［勝ち点計算］
        pseudo_series_result : PseudoSeriesResult
            １シリーズ分をフルにコイントスした結果
        """

        # 共通
        self._number_of_times = number_of_times
        self._number_of_failed = number_of_failed
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
    def number_of_times(self):
        """行われた対局数"""
        return self._number_of_times


    @property
    def number_of_failed(self):
        """［表も裏も出なかった対局数］"""
        return self._number_of_failed


    @property
    def pseudo_series_result(self):
        """１シリーズ分をフルにコイントスした結果"""
        return self._pseudo_series_result


    def is_points_won(self, winner, loser):
        """winner の［勝ち点］は［目標の点数］に達していないが、 loser の［勝ち点］より多くて winner さんの勝ち"""
        return not self._point_calculation.is_fully_won(winner) and self._point_calculation.x_has_more_than_y(winner, loser)


    def is_won(self, winner, loser):
        """FIXME winner が loser に勝った"""

        # 両者が満点勝ちしているという状況はない
        if self.point_calculation.is_fully_won(winner) and self.point_calculation.is_fully_won(loser):
            raise ValueError(f"両者が満点勝ちしているという状況はない {winner=}  {loser=}  {self.point_calculation.is_fully_won(winner)=}  {self.point_calculation.is_fully_won(loser)=}")

        # 両者が判定勝ちしているという状況はない
        if self.is_points_won(winner=winner, loser=loser) and self.is_points_won(winner=loser, loser=winner):
            raise ValueError(f"両者が判定勝ちしているという状況はない {winner=}  {loser=}  {self.is_points_won(winner=winner, loser=loser)=}  {self.is_points_won(winner=loser, loser=winner)=}")

        # 満点勝ちなら確定、判定勝ちでもOK 
        return self.point_calculation.is_fully_won(winner) or self.is_points_won(winner=winner, loser=loser)


    def is_no_won(self, opponent_pair):
        """勝者なし。 x 、 y の［勝ち点］が等しいとき"""

        if opponent_pair == FACE_OF_COIN:
            x = HEAD
            y = TAIL
        elif opponent_pair == PLAYERS:
            x = ALICE
            y = BOB
        else:
            raise ValueError(f"{opponent_pair=}")

        return self._point_calculation.get_point_of(x) == self._point_calculation.get_point_of(y)


    def stringify_dump(self, indent):
        double_indent = indent + indent
        return f"""\
{indent}SeriesResult
{indent}------------
{indent}{indent}{self._number_of_times=}
{indent}{indent}{self._number_of_failed=}
{indent}{indent}{self._span=}
{indent}{indent}self._point_calculation:
{self._point_calculation.stringify_dump(double_indent)}
{indent}{indent}self._pseudo_series_result:
{self._pseudo_series_result.stringify_dump(double_indent)}
{indent}{indent}{self.is_points_won(winner=HEAD, loser=TAIL)=}
{indent}{indent}{self.is_points_won(winner=TAIL, loser=HEAD)=}
{indent}{indent}{self.is_points_won(winner=ALICE, loser=BOB)=}
{indent}{indent}{self.is_points_won(winner=BOB, loser=ALICE)=}
{indent}{indent}{self.is_won(winner=HEAD, loser=TAIL)=}
{indent}{indent}{self.is_won(winner=TAIL, loser=HEAD)=}
{indent}{indent}{self.is_won(winner=ALICE, loser=BOB)=}
{indent}{indent}{self.is_won(winner=BOB, loser=ALICE)=}
{indent}{indent}{self.is_no_won(opponent_pair=FACE_OF_COIN)}
{indent}{indent}{self.is_no_won(opponent_pair=PLAYERS)}
"""
    

class LargeSeriesTrialSummary():
    """大量のシリーズを試行した結果"""


    def __init__(self, series_result_list):
        """初期化
        
        Parameters
        ----------
        series_result_list : list
            ［シリーズ］の結果のリスト
        """

        self._series_result_list = series_result_list
        self._shortest_time_th = None
        self._longest_time_th = None
        self._number_of_failed = None

        # ［満点勝ち］の件数。 未使用、表、裏、Ａさん、Ｂさんの順。初期値は None
        self._number_of_fully_wons = [None, None, None, None, None]

        # ［勝ち点判定勝ち］の件数。 未使用、表、裏、Ａさん、Ｂさんの順。初期値は None
        self._number_of_points_wons = [None, None, None, None, None]

        # ［勝者がなかった回数］。未使用、コインの表と裏、ＡさんとＢさんの順
        self._number_of_no_wons = [None, None, None]


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
                if series_result.number_of_times < self._shortest_time_th:
                    self._shortest_time_th = series_result.number_of_times

        return self._shortest_time_th


    @property
    def longest_time_th(self):
        """［最長対局数］"""
        if self._longest_time_th is None:
            self._longest_time_th = 0
            for series_result in self._series_result_list:
                if self._longest_time_th < series_result.number_of_times:
                    self._longest_time_th = series_result.number_of_times

        return self._longest_time_th


    def number_of_total_wons(self, opponent_pair):
        if opponent_pair == FACE_OF_COIN:
            return self.number_of_wons(winner=HEAD, loser=TAIL) + self.number_of_wons(winner=TAIL, loser=HEAD)
        elif opponent_pair == PLAYERS:
            return self.number_of_wons(winner=ALICE, loser=BOB) + self.number_of_wons(winner=BOB, loser=ALICE)


    def number_of_total_fully_wons(self, opponent_pair):
        if opponent_pair == FACE_OF_COIN:
            return self.number_of_fully_wons(elementary_event=HEAD) + self.number_of_fully_wons(elementary_event=TAIL)
        elif opponent_pair == PLAYERS:
            return self.number_of_fully_wons(elementary_event=ALICE) + self.number_of_fully_wons(elementary_event=BOB)


    def number_of_total_points_wons(self, opponent_pair):
        if opponent_pair == FACE_OF_COIN:
            return self.number_of_points_wons(winner=HEAD, loser=TAIL) + self.number_of_points_wons(winner=TAIL, loser=HEAD)
        elif opponent_pair == PLAYERS:
            return self.number_of_points_wons(winner=ALICE, loser=BOB) + self.number_of_points_wons(winner=BOB, loser=ALICE)


    @property
    def number_of_failed(self):
        """全シリーズ通算の引分けの対局数"""
        if self._number_of_failed is None:
            self._number_of_failed = 0
            for series_result in self._series_result_list:
                if series_result.number_of_failed:
                    self._number_of_failed += 1

        return self._number_of_failed


    def number_of_fully_wons(self, elementary_event):
        """elementary_event が［目標の点数］を集めて勝った回数"""
        if self._number_of_fully_wons[elementary_event] is None:
            self._number_of_fully_wons[elementary_event] = 0
            for series_result in self._series_result_list:
                if series_result.point_calculation.is_fully_won(elementary_event):
                    self._number_of_fully_wons[elementary_event] += 1

        return self._number_of_fully_wons[elementary_event]


    def number_of_points_wons(self, winner, loser):
        """winner が［勝ち点差判定］で loser に勝った回数"""
        if self._number_of_points_wons[winner] is None:
            self._number_of_points_wons[winner] = 0
            for series_result in self._series_result_list:
                if series_result.is_points_won(winner=winner, loser=loser):
                    self._number_of_points_wons[winner] += 1

        return self._number_of_points_wons[winner]


    def number_of_failed_series(self, turn_system):
        """引分けで終わったシリーズ数"""

        if turn_system == WHEN_FROZEN_TURN:
            return self.number_of_series - self.number_of_wons(winner=HEAD, loser=TAIL) - self.number_of_wons(winner=TAIL, loser=HEAD)
        
        elif turn_system == WHEN_ALTERNATING_TURN:
            return self.number_of_series - self.number_of_wons(winner=ALICE, loser=BOB) - self.number_of_wons(winner=BOB, loser=ALICE)
        
        else:
            raise ValueError(f"{turn_system=}")


    def win_rate_without_draw(self, winner, loser, turn_system):
        """試行した結果、 winner が loser に勝つ確率
        
        引分けを除いて計算する
        """
        return self.number_of_wons(winner=winner, loser=loser) / (self.number_of_series - self.number_of_failed_series(turn_system=turn_system))


    def win_rate_error_without_draw(self, winner, loser, turn_system):
        """試行した結果、 winner が loser に勝つ確率と0.5との誤差］
        
        引分けを除いて計算する
        """
        return self.win_rate_without_draw(winner=winner, loser=loser, turn_system=turn_system) - 0.5


    def failure_rate(self, turn_system):
        """試行した結果、［引き分けた率］"""
        return self.number_of_failed_series(turn_system=turn_system) / self.number_of_series


    def number_of_wons(self, winner, loser):
        """winner が loser に勝った数"""
        return self.number_of_fully_wons(elementary_event=winner) + self.number_of_points_wons(winner=winner, loser=loser)


    def number_of_no_wons(self, opponent_pair):
        """［先後固定制］で勝者がなかった回数"""
        if self._number_of_no_wons[opponent_pair] is None:
            self._number_of_no_wons[opponent_pair] = 0
            for series_result in self._series_result_list:
                if series_result.is_no_won(opponent_pair=opponent_pair):
                    self._number_of_no_wons[opponent_pair] += 1

        return self._number_of_no_wons[opponent_pair]
