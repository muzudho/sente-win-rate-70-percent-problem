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


# デバッグ・ログ用のインデント
INDENT = '    '


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
FROZEN_TURN = 1

# ［先後交互制］。配列のインデックスに使う
ALTERNATING_TURN = 2


# Opponent pair
# -------------

# ［コインの表と裏］。配列のインデックスに使う
FACE_OF_COIN = 1

# ［ＡさんとＢさん］。配列のインデックスに使う
PLAYERS = 2


# Generation Algorithm
# --------------------

# 力任せ探索
BRUTE_FORCE = 1

# 理論から算出する
THEORETICAL = 2


# p_step が 0 の場合、ベスト値が設定されていないので、その行データは有効ではありません
IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO = 0


class Converter():
    """変換する機能まとめ"""


    _face_of_coin_to_str = None

    @classmethod
    def face_of_coin_to_str(clazz, face_of_coin):
        if clazz._face_of_coin_to_str is None:
            clazz._face_of_coin_to_str = {
                EMPTY: '失',    # 失敗の頭文字
                HEAD : '表',
                TAIL : '裏',
            }
        
        return clazz._face_of_coin_to_str[face_of_coin]


    _turn_system_to_str = None

    @classmethod
    def turn_system_to_str(clazz, turn_system):
        if clazz._turn_system_to_str is None:
            clazz._turn_system_to_str = {
                FROZEN_TURN : '先後固定制',
                ALTERNATING_TURN : '先後交互制',
            }

        return clazz._turn_system_to_str[turn_system]


    _turn_system_to_code = {
        FROZEN_TURN : 'frozen',
        ALTERNATING_TURN : 'alternating',
    }

    @classmethod
    def turn_system_to_code(clazz, turn_system):
        return clazz._turn_system_to_code[turn_system]


    # 反対
    _opponent = {
        HEAD : TAIL,
        TAIL : HEAD,
        ALICE : BOB,
        BOB : ALICE,
    }

    @classmethod
    def opponent(clazz, elementary_event):
        return clazz._opponent[elementary_event]


    @staticmethod
    def make_generation_algorythm(failure_rate, turn_system):
        # 現在のところ、［先後固定制］で、かつ［表も裏も出ない確率］が 0 のときのみ、理論値を求めることができます
        if failure_rate == 0 and turn_system == FROZEN_TURN:
            return THEORETICAL
        return BRUTE_FORCE


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
            ［先後の決め方］
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


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}Specification
{indent}-------------
{succ_indent}{self._p=}
{succ_indent}{self._failure_rate=}
{succ_indent}{self._turn_system=}
"""



def round_letro(number, format='0'):
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

    # 数を文字列型に変換して Decimal オブジェクトを生成。
    # Decimal オブジェクト quantize によって丸める。さらに int 型に変換して返す
    #
    # quantize には、小数第一位を四捨五入するときは '0', 小数第二位を四捨五入するときは `0.1`、
    # 小数第三位を四捨五入するときは '0.01' のように、書式を指定する必要がある
    return int(Decimal(str(number)).quantize(Decimal(format), ROUND_HALF_UP))


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


class SequenceOfFaceOfCoin():
    """［コインの表］、［コインの裏］、［コインの表でも裏でもないもの］の印が並んだもの"""


    @staticmethod
    def make_list_of_all_pattern_face_of_coin(can_failure, series_rule):
        """［コインの表］、［コインの裏］、［コインの表でも裏でもないもの］の印の組み合わせが全て入っているリストを作成します

        TODO ［先後固定制］での１シリーズについて、フル対局分の、全パターンのコイントスの結果を作りたい
        
        １タイムは　勝ち、負けの２つ、または　勝ち、負け、引き分けの３つ。

        Returns
        -------
        series_rule : SeriesRule
            ［シリーズ・ルール］
        power_set_list : list
            勝った方の色（引き分け含む）のリストが全パターン入っているリスト
        """

        # 要素数
        if can_failure:
            # 表勝ち、裏勝ち、勝者なしの３要素
            elements = [HEAD, TAIL, EMPTY]
        else:
            # 表勝ち、裏勝ちけの２要素
            elements = [HEAD, TAIL]

        # 桁数
        depth = series_rule.upper_limit_coins

        # １シーズン分のコイントスの全ての結果
        stats = []

        position = []


        def search(depth, stats, position, can_failure):

            # 表勝ちを追加
            position.append(HEAD)

            # スタッツに、ポジションのコピーを追加
            stats.append(list(position))

            if 0 < depth:
                search(depth - 1, stats, position, can_failure=False)

            # 末尾の要素を削除
            position.pop()


            # 裏勝ちを追加
            position.append(TAIL)

            # スタッツに、ポジションのコピーを追加
            stats.append(list(position))

            if 0 < depth:
                search(depth - 1, stats, position, can_failure=False)

            # 末尾の要素を削除
            position.pop()


            if can_failure:
                # 引分けを追加
                position.append(EMPTY)

                # スタッツに、ポジションのコピーを追加
                stats.append(list(position))

                if 0 < depth:
                    search(depth - 1, stats, position, can_failure=False)

                # 末尾の要素を削除
                position.pop()



        search(depth, stats, position, can_failure=False)

        return stats


    @staticmethod
    def make_sequence_of_playout(spec, upper_limit_coins):
        """［コイントスの結果］を並べたものを作成します

        Parameters
        ----------
        spec : Specification
            ［仕様］
        upper_limit_coins : int
            ［上限対局数］
        """

        list_of_face_of_coin = []

        # ［上限対局数］までやる
        for time_th in range(1, upper_limit_coins + 1):

            face_of_coin = toss_a_coin(
                    p=spec.p,
                    failure_rate=spec.failure_rate)

            list_of_face_of_coin.append(face_of_coin)


        return list_of_face_of_coin


    @staticmethod
    def cut_down(list_of_face_of_coin, number_of_times):
        """コイントスの結果のリストの長さを切ります。
        対局は必ずしも［上限対局数］になるわけではありません"""
        return list_of_face_of_coin[0:number_of_times]


class PointCalculation():
    """勝ち点計算に使う"""


    def __init__(self, spec, series_rule):
        """初期化
        
        Parameters
        ----------
        spec : Specification
            ［仕様］
        series_rule : SeriesRule
            ［シリーズ・ルール］
        """

        self._spec = spec
        self._series_rule = series_rule

        # （Points list）［勝ち点］のリスト。要素は、未使用、未使用、未使用、Ａさん、Ｂさん
        self._pts_list = [None, None, None, 0, 0]


    @property
    def series_rule(self):
        """［勝ち点ルール］の構成"""
        return self._series_rule


    @staticmethod
    def get_successful_player(elementary_event, time_th, turn_system):

        # ［先後交互制］
        if turn_system == ALTERNATING_TURN:
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
        if turn_system == FROZEN_TURN:
            if elementary_event == HEAD:
                return ALICE

            if elementary_event == TAIL:
                return BOB

            # 表も裏も出なかった
            if elementary_event == EMPTY:
                return EMPTY

            raise ValueError(f"{elementary_event=}")


        raise ValueError(f"{turn_system=}")


    def get_gameover_reason(self):
        """TODO 終局している場合、その理由を記述した文字列を返す。終局していなければナン
        
        NOTE ［先後交互制］では、表番が満点でも勝利条件ではないことに注意すること。［先後固定制］にしろ、［先後交互制］にしろ、プレイヤーの勝ち負けを見ればよい
        """

        a_fully_won = self._series_rule.step_table.span <= self._pts_list[ALICE]
        b_fully_won = self._series_rule.step_table.span <= self._pts_list[BOB]

        # 両者が同時に満点を取っているケースはおかしい
        if a_fully_won and b_fully_won:
            raise ValueError(f"両者が同時に満点を取っているケースはおかしい  {a_fully_won=}  {b_fully_won=}")

        # Ａさんが満点
        if a_fully_won:
            return 'a_fully_won'

        # Ｂさんが満点
        if b_fully_won:
            return 'b_fully_won'

        # 終局していない
        return None


    def append_point_when_won(self, successful_face_of_coin, time_th, list_of_face_of_coin):
        """加点

        Parameters
        ----------
        successful_face_of_coin : int
            ［コインの表か裏］
        list_of_face_of_coin : list
            ［検証用］
        """

        successful_player = PointCalculation.get_successful_player(successful_face_of_coin, time_th, self._spec.turn_system)

        # ［勝ち点］
        step = self._series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=successful_face_of_coin)


        # FIXME 検算用
        old_pts_list = list(self._pts_list)

        self._pts_list[successful_player] += step


        # FIXME 検算
        if self._series_rule.step_table.span <= self._pts_list[ALICE] and self._series_rule.step_table.span <= self._pts_list[BOB]:
            print(f"""\
PointCalculation
----------------
self.stringify_dump:
{self.stringify_dump(INDENT)}
{old_pts_list=}
""")

            # スコアボード表示
            score_board = ScoreBoard(
                    spec=self._spec,
                    series_rule=self._series_rule,
                    list_of_face_of_coin=list_of_face_of_coin)
            print(score_board.stringify_csv())

            raise ValueError(f"ＡさんとＢさんがどちらも満点勝ちしている、これはおかしい  {self._pts_list[ALICE]=}  {self._pts_list[BOB]=}")


    def get_pts_of(self, player):
        return self._pts_list[player]


    def is_fully_won(self, player):
        """［目標の点数］を満たしているか？"""
        return self._series_rule.step_table.span <= self.get_pts_of(player=player)


    def x_has_more_than_y(self, x, y):
        """xの方がyより勝ち点が多いか？"""
        return self.get_pts_of(player=y) < self.get_pts_of(player=x)


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}PointCalculation
{indent}----------------
{succ_indent}self._series_rule:
{self._series_rule.stringify_dump(succ_indent)}
{succ_indent}{self._pts_list=}
"""


def assert_list_of_face_of_coin(list_of_face_of_coin):
    """［コインの表］、［コインの裏］、［コインの表と裏のどちらでもない］のいずれかしか含んでいないはずです"""
    for mark in list_of_face_of_coin:
        if mark not in [HEAD, TAIL, EMPTY]:
            raise ValueError(f"予期しない値がリストに入っています  {mark=}")


def judge_series(spec, series_rule, list_of_face_of_coin):
    """［コインの表］、［コインの裏］、［コインの表と裏のどちらでもない］の３つの内のいずれかを印をつけ、
    その印が並んだものを、１シリーズ分の疑似対局結果として読み取ります

    Parameters
    ----------
    spec : Specification
        仕様
    series_rule : int
        ［シリーズ・ルール］
    list_of_face_of_coin : list
        コイントスした結果のリスト。引き分け含む
    """

    # FIXME 検証
    if len(list_of_face_of_coin) < series_rule.shortest_coins:
        text = f"{spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
        print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
        raise ValueError(text)


    # FIXME 検算
    assert_list_of_face_of_coin(list_of_face_of_coin=list_of_face_of_coin)


    # ［先後固定制］
    if spec.turn_system == FROZEN_TURN:
        """［勝ち点差判定］や［タイブレーク］など、決着が付かなかったときの処理は含みません
        もし、引き分けがあれば、［引き分けを１局として数えるケース］です。

        Parameters
        ----------
        series_rule : SeriesRule
            ［シリーズ・ルール］
        
        Returns
        -------
        trial_results_for_one_series : TrialResultsForOneSeries
            ［シリーズ］１つ分の試行結果
        """

        # ［勝ち点計算］
        point_calculation = PointCalculation(
                spec=spec,
                series_rule=series_rule)

        # ［このシリーズで引き分けた対局数］
        failed_coins = 0

        time_th = 0

        # 予め作った１シリーズ分の対局結果を読んでいく
        for face_of_coin in list_of_face_of_coin:
            time_th += 1

            # 引き分けを１局と数えるケース
            #
            #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
            #
            if face_of_coin == EMPTY:
                failed_coins += 1
            
            else:
                
                # FIXME 検算
                gameover_reason = point_calculation.get_gameover_reason()
                if gameover_reason is not None:
                    raise ValueError(f"終局後に加点してはいけません1  {gameover_reason=}")


                point_calculation.append_point_when_won(
                        successful_face_of_coin=face_of_coin,
                        time_th=time_th,
                        list_of_face_of_coin=list_of_face_of_coin[0:time_th])


                # 終局
                gameover_reason = point_calculation.get_gameover_reason()
                if gameover_reason is not None:

                    # コイントスの結果のリストの長さを切ります。
                    # 対局は必ずしも［上限対局数］になるわけではありません
                    list_of_face_of_coin = SequenceOfFaceOfCoin.cut_down(list_of_face_of_coin, time_th)

                    # FIXME 検証
                    if len(list_of_face_of_coin) != time_th:
                        raise ValueError(f"テープの長さがおかしい1 {len(list_of_face_of_coin)=}  {time_th=}  {gameover_reason=}")

                    # FIXME 検証
                    if time_th < series_rule.shortest_coins:
                        text = f"{spec.p=} 対局数の実際値 {time_th} が最短対局数の理論値 {series_rule.shortest_coins} を下回った1  {gameover_reason=}"
                        print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
                        raise ValueError(text)

                    # FIXME 検証
                    if series_rule.upper_limit_coins < time_th:
                        text = f"{spec.p=} 対局数の実際値 {time_th} が上限対局数の理論値 {series_rule.upper_limit_coins} を上回った1"
                        print(f"""{text}
{list_of_face_of_coin=}
{shortest_coins=}
""")
                        raise ValueError(text)


                    return TrialResultsForOneSeries(
                            spec=spec,
                            series_rule=series_rule,
                            failed_coins=failed_coins,
                            point_calculation=point_calculation,
                            list_of_face_of_coin=list_of_face_of_coin)


        # FIXME 検証
        if len(list_of_face_of_coin) != time_th:
            raise ValueError(f"テープの長さがおかしい2 {len(list_of_face_of_coin)=}  {time_th=}")

        # FIXME 検証
        if time_th < series_rule.shortest_coins:
            text = f"{spec.p=} 対局数の実際値 {time_th} が最短対局数の理論値 {series_rule.shortest_coins} を下回った2"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
            raise ValueError(text)

        # FIXME 検証
        if series_rule.upper_limit_coins < time_th:
            text = f"{spec.p=} 対局数の実際値 {time_th} が上限対局数の理論値 {series_rule.upper_limit_coins} を上回った2"
            print(f"""{text}
{list_of_face_of_coin=}
{shortest_coins=}
""")
            raise ValueError(text)

        # タイブレークをするかどうかは、この関数の呼び出し側に任せます
        return TrialResultsForOneSeries(
                spec=spec,
                series_rule=series_rule,
                failed_coins=failed_coins,
                point_calculation=point_calculation,
                list_of_face_of_coin=list_of_face_of_coin)


    # ［先後交互制］
    if spec.turn_system == ALTERNATING_TURN:
        """で１対局行う（どちらの勝ちが出るまでコイントスを行う）
        
        Parameters
        ----------
        series_rule : SeriesRule
            ［シリーズ・ルール］
        
        Returns
        -------
        trial_results_for_one_series : TrialResultsForOneSeries
            ［シリーズ］１つ分の試行結果
        """

        # ［勝ち点計算］
        point_calculation = PointCalculation(
                spec=spec,
                series_rule=series_rule)

        # ［このシリーズで引き分けた対局数］
        failed_coins = 0

        time_th = 0

        # 予め作った１シリーズ分の対局結果を読んでいく
        for face_of_coin in list_of_face_of_coin:
            time_th += 1

            # 引き分けを１局と数えるケース
            #
            #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
            #
            if face_of_coin == EMPTY:
                failed_coins += 1

            else:

                # FIXME 検算
                gameover_reason = point_calculation.get_gameover_reason()
                if gameover_reason is not None:
                    raise ValueError(f"終局後に加点してはいけません2  {gameover_reason=}")


                successful_player = PointCalculation.get_successful_player(face_of_coin, time_th, turn_system=spec.turn_system)

                point_calculation.append_point_when_won(
                        successful_face_of_coin=face_of_coin,
                        time_th=time_th,
                        list_of_face_of_coin=list_of_face_of_coin[0:time_th])


                # 終局
                gameover_reason = point_calculation.get_gameover_reason()
                if gameover_reason is not None:

                    # コイントスの結果のリストの長さを切ります。
                    # 対局は必ずしも［上限対局数］になるわけではありません
                    list_of_face_of_coin = SequenceOfFaceOfCoin.cut_down(list_of_face_of_coin, time_th)

                    # FIXME 検証
                    if len(list_of_face_of_coin) != time_th:
                        raise ValueError(f"テープの長さがおかしい3 {len(list_of_face_of_coin)=}  {time_th=}  {gameover_reason=}")

                    # FIXME 検証
                    if time_th < series_rule.shortest_coins:
                        text = f"{spec.p=} 対局数の実際値 {time_th} が最短対局数の理論値 {series_rule.shortest_coins} を下回った3  {gameover_reason=}"
                        print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
                        raise ValueError(text)

                    # FIXME 検証
                    if series_rule.upper_limit_coins < time_th:
                        text = f"{spec.p=} 対局数の実際値 {time_th} が上限対局数の理論値 {series_rule.upper_limit_coins} を上回った3  {gameover_reason=}"
                        print(f"""{text}
{list_of_face_of_coin=}
{shortest_coins=}
""")
                        raise ValueError(text)

                    # FIXME カットダウン後のテープと、引き分けの数を確認
                    failed_coins_2 = 0
                    for face_of_coin_2 in list_of_face_of_coin:
                        if face_of_coin_2 == EMPTY:
                            failed_coins_2 += 1
                    if failed_coins != failed_coins_2:
                        raise ValueError(f"検算で、引き分けの数が一致しません {failed_coins=}  {failed_coins_2=}  {list_of_face_of_coin=}  {gameover_reason=}")


                    return TrialResultsForOneSeries(
                            spec=spec,
                            series_rule=series_rule,
                            failed_coins=failed_coins,
                            point_calculation=point_calculation,
                            list_of_face_of_coin=list_of_face_of_coin)


        # FIXME 検証
        if len(list_of_face_of_coin) != time_th:
            raise ValueError(f"テープの長さがおかしい4 {len(list_of_face_of_coin)=}  {time_th=}")

        # FIXME 検証
        if time_th < series_rule.shortest_coins:
            text = f"{spec.p=} 対局数の実際値 {time_th} が最短対局数の理論値 {series_rule.shortest_coins} を下回った4"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
            raise ValueError(text)

        # FIXME 検証
        if series_rule.upper_limit_coins < time_th:
            text = f"{spec.p=} 対局数の実際値 {time_th} が上限対局数の理論値 {series_rule.upper_limit_coins} を上回った4"
            print(f"""{text}
{list_of_face_of_coin=}
{shortest_coins=}
""")
            raise ValueError(text)

        # タイブレークをするかどうかは、この関数の呼び出し側に任せます
        return TrialResultsForOneSeries(
                spec=spec,
                series_rule=series_rule,
                failed_coins=failed_coins,
                point_calculation=point_calculation,
                list_of_face_of_coin=list_of_face_of_coin)


    raise ValueError(f"{spec.turn_system=}")


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


class SeriesRule():
    """［シリーズ・ルール］
    
    NOTE ［最短対局数］、［上限対局数］は指定できず、計算で求めるもの
    """


    class StepTable():
        """［１勝の点数テーブル］"""

        
        def __init__(self, p_step, q_step, p_step_when_failed, q_step_when_failed, span):
            """初期化
            
            Parameters
            ----------
            p_step : int
                ［表が出て勝ったときの点数］
            q_step : int
                ［裏が出て勝ったときの点数］
            p_step_when_failed : float
                ［コインの表も裏も出なかったときの、表番の方の勝ち点］
            q_step_when_failed : float
                ［コインの表も裏も出なかったときの、裏番の方の勝ち点］
            span : int
                ［目標の点数］
            """

            self._step_list = [
                    # 0: ［未使用］
                    None,
                    # 1: ［コインの表が出たときの勝ち点］
                    p_step,
                    # 2: ［コインの裏が出たときの勝ち点］
                    q_step,
                    # 3: ［コインの表も裏も出なかったときの、表番の方の勝ち点］
                    p_step_when_failed,
                    # 4: ［コインの表も裏も出なかったときの、裏番の方の勝ち点］
                    q_step_when_failed]

            self._span = span


        @property
        def span(self):
            """［目標の点数］"""
            return self._span


        def get_step_by(self, challenged, face_of_coin):
            """［１勝の点数］を取得します
            
            Parameters
            ----------
            challenged : int
                ［成功か失敗］
            face_of_coin : int
                ［コインの表か裏かそれ以外］
            """

            if challenged == SUCCESSFUL:
                # ［コインの表が出たときの勝ち点］
                if face_of_coin == HEAD:
                    return self._step_list[1]

                # ［コインの裏が出たときの勝ち点］
                if face_of_coin == TAIL:
                    return self._step_list[2]

                raise ValueError(f"{face_of_coin=}")


            if challenged == FAILED:
                # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
                if face_of_coin == HEAD:
                    return self._step_list[3]
                
                # ［コインの表も裏も出なかったときの、裏番の方の勝ち点］
                if face_of_coin == TAIL:
                    return self._step_list[4]
                
                raise ValueError(f"{face_of_coin=}")


            raise ValueError(f"{challenged=}")


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


        def stringify_dump(self, indent):
            succ_indent = indent + INDENT
            return f"""\
{indent}StepTable
{indent}---------
{succ_indent}{self._step_list=}
{succ_indent}{self._span=}
"""


    def __init__(self, spec, step_table, shortest_coins, upper_limit_coins):
        """初期化
        
        Parameters
        ----------
        spec : Specification
            ［仕様］
        step_table : StepTable
            ［１勝の点数テーブル］
        shortest_coins : int
            ［最短対局数］
        upper_limit_coins : int
            ［上限対局数］
        """

        self._spec = spec

        self._step_table = step_table

        # ［最短対局数］
        self._shortest_coins = shortest_coins

        # ［上限対局数］
        self._upper_limit_coins = upper_limit_coins


    @staticmethod
    def make_series_rule_base(spec, p_step, q_step, span):
        """
        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        # NOTE numpy.int64 型は、 float NaN が入っていることがある？
        if not isinstance(p_step, int):
            raise ValueError(f"int 型であることが必要 {type(p_step)=}  {p_step=}")

        if not isinstance(q_step, int):
            raise ValueError(f"int 型であることが必要 {type(q_step)=}  {q_step=}")

        if not isinstance(span, int):
            raise ValueError(f"int 型であることが必要 {type(span)=}  {span=}")

        # ベスト値が未設定の場合、 p_step は 0 が入っています
        if p_step < IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
            raise ValueError(f"非負の整数であることが必要 {p_step=}")

        if q_step < 1:
            raise ValueError(f"正の整数であることが必要 {q_step=}")

        if span < 1:
            raise ValueError(f"正の整数であることが必要 {span=}")

        if q_step < p_step:
            raise ValueError(f"［コインの表が出たときの勝ち点］{p_step=} が、［コインの裏が出たときの勝ち点］ {q_step} を上回るのはおかしいです")

        if span < q_step:
            raise ValueError(f"［コインの裏が出たときの勝ち点］{q_step=} が、［目標の点数］{span} を上回るのはおかしいです")


        p_step_when_failed = 0

        q_step_when_failed = 0

        # if q_step_when_failed < p_step_when_failed:
        #     raise ValueError(f"［コインの表も裏も出なかったときの、表番の方の勝ち点］{p_step_when_failed=} が、［コインの表も裏も出なかったときの、裏番の方の勝ち点］ {q_step_when_failed} を上回るのはおかしいです")

        step_table = SeriesRule.StepTable(
                p_step=p_step,
                q_step=q_step,
                p_step_when_failed=p_step_when_failed,
                q_step_when_failed=q_step_when_failed,
                span=span)


        # 0除算を避ける
        if p_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
            # ［最短対局数］
            shortest_coins = 0

            # ［上限対局数］
            upper_limit_coins = 0

        else:
            # ［最短対局数］
            shortest_coins = SeriesRule.let_shortest_coins(
                    p_step=p_step,
                    q_step=q_step,
                    span=span,
                    turn_system=spec.turn_system)

            # ［上限対局数］
            upper_limit_coins = SeriesRule.let_upper_limit_coins(
                    spec=spec,
                    p_time=step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                    q_time=step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))


        if upper_limit_coins < shortest_coins:
            text = f"［最短対局数］{shortest_coins} が、［上限対局数］{upper_limit_coins} より長いです"

            succ_indent = INDENT
            print(f"""\
spec:
{spec.stringify_dump(succ_indent)}
{text}
{p_step=}
{q_step=}
{span=}
step_table:
{step_table.stringify_dump('   ')}
""")
            raise ValueError(text)


        return SeriesRule(
                spec=spec,
                step_table=step_table,
                # ［最短対局数］
                shortest_coins=shortest_coins,
                # ［上限対局数］
                upper_limit_coins=upper_limit_coins)


    @property
    def is_enabled(self):
        """このシリーズ・ルールは有効な値かどうか？"""
        return self._step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD) != IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO


    @staticmethod
    def make_series_rule_auto_span(spec, p_time, q_time):
        """［表勝ちだけでの対局数］と［裏勝ちだけでの対局数］が分かれば、［かくきんシステムのｐの構成］を分析して返す
        
        Parameters
        ----------
        spec : Specificetion
            ［仕様］
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

        return SeriesRule.make_series_rule_base(
                spec=spec,
                p_step=p_step,
                q_step=q_step,
                span=span)


    @property
    def step_table(self):
        return self._step_table


    @property
    def spec(self):
        """［仕様］"""
        return self._spec


    @property
    def shortest_coins(self):
        """［最短対局数］"""
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        """［上限対局数］"""
        return self._upper_limit_coins


    @staticmethod
    def let_shortest_coins(p_step, q_step, span, turn_system):
        """［最短対局数］を算出"""

        if turn_system == FROZEN_TURN:
            """［先後固定制］での［最短対局数］
            
            裏が全勝したときの回数と同じ

            `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
                ・  裏  裏  裏  裏  裏  で、最短５局
                10  10  10  10 10  10
                10   8   6   4  2   0
            """

            # ［目標の点数］は最小公倍数なので割り切れる
            return round_letro(span / q_step)

        if turn_system == ALTERNATING_TURN:
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

                表1点、裏1点、目標1点
                    ・  Ａ  で、最短１局
                     1   1
                     1   0
            """

            remainder = span

            successful_step = p_step + q_step

            if p_step + q_step <= remainder:
                # NOTE なるべく割り算で小数点以下の数がでないように、割り切れる数にしてから割るようにし、整数だけを使って計算する
                new_remainder = span % successful_step
                # 余りから端数を引いて割り切れるようにしてから割る。先手と後手のペアだから、回数は２倍
                time = math.floor((remainder - new_remainder) / successful_step) * 2
                remainder = new_remainder

            else:
                time = 0

            # 端数があれば［裏勝ち１つの点数］を引く（１回分を加算）
            #
            #   NOTE 裏（後手）の方が step 値が表（先手）より大きいか、等しいです。［裏勝ち１つの点数］の方から先に引きます
            #
            if 0 < remainder:
                time += 1
                remainder -= q_step

                # まだ端数があれば［表勝ち１つの点数］を引く（１回分を加算）
                if 0 < remainder:
                    time += 1
                    remainder -= p_step

                    # remainder は負数になっているはず（割り切れないはず）
                    if 0 <= remainder:
                        raise ValueError(f"ここで余りが負数になっていないのはおかしい {remainder=}  {span=}  {p_step=}  {q_step=}")
                
                # remainder は零か負数になっているはず
                elif 0 < remainder:
                    raise ValueError(f"ここで余りが零か負数になっていないのはおかしい {remainder=}  {span=}  {p_step=}  {q_step=}")

            return time


        raise ValueError(f"{turn_system=}")


    @staticmethod
    def let_upper_limit_coins_without_failure_rate(spec, p_time, q_time):
        """［上限対局数］を算出します

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        # ［先後固定制］
        if spec.turn_system == FROZEN_TURN:
            """
            裏があと１つで勝てるところで止まり、表が全勝したときの回数と同じ

            筆算
            ----
                `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
                    ・  表  表  表  表  表  表  表  表  表  裏  裏  裏  裏  裏  で、最長１４局
                    10   9   8   7   6   5  4   3   2   1  1   1   1   1   1
                    10  10  10  10  10  10 10  10  10  10  8   6   4   2   0

                    ・  裏  裏  裏   裏  表  表  表  表  表  表  表  表  表  表  で、最長１４局
                    10  10  10  10  10   9   8   7   6  5   4   3   2   1   0  
                    10   8   6   4   2   2   2   2   2  2   2   2   2   2   2

                `10表 12裏 14目（先後固定制）`
                    ・  表  裏  で最長２局
                    14   4   4
                    14  14   0

                    ・  裏  表  表  で最長３局
                    14   2   2   2
                    14  14   4  -6
            """
            return  p_time + q_time - 1


        # ［先後交互制］
        elif spec.turn_system == ALTERNATING_TURN:
            """
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
            
            表1点、裏1点、目標1点
                ・  Ａ  で、最長１局
                    1   1
                    1   0
        """
            return 2 * p_time - 1


        else:
            raise ValueError(f"{spec.turn_system=}")


    @staticmethod
    def let_upper_limit_coins_with_failure_rate(spec, number_of_longest_time_without_failure_rate):
        """［上限対局数］を算出します

        Parameters
        ----------
        spec : Specification
            ［仕様］
        
        ［表も裏も出ない確率］の考え方
        ----------------------------

        例えば failure_rate=0.1 のとき、つまり１０回に１回は引き分けのとき、本来１０回対局することを想定しているのに１０回対局できないので、計算式が合わなくなります。

            10 * (1 - 0.1) = 9
        
        そこで、

            y * (1 - 0.1) = 10
        
        の y を求めたい。 y は試行シリーズ数。（10 は、failure_rate=0 のときの試行シリーズ数）

            = n * (1 - 0.1) = 10
            = n             = 10 / (1 - 0.1)
            = n             =  11.1111...
        
        仮に小数点以下切り上げして 12 とします。

            12 * (1 - 0.1) = 10.8
        
        １２回対局すれば、その１割が引き分けでも、１０回の対局は決着するようです。

        小数点以下四捨五入なら 11 なので

            11 * (1 - 0.1) = 9.9
        
        四捨五入（または切り捨て）だと１０回に足りないようです。

            y = n * (1 - failure_rate)
        
                n は、failure_rate=0 のときの試行シリーズ数
                y は、0 < failure_rate のときの試行シリーズ数
        """
        return math.ceil(number_of_longest_time_without_failure_rate / (1 - spec.failure_rate))


    @staticmethod
    def let_upper_limit_coins(spec, p_time, q_time):
        """［上限対局数］を算出します

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        number_of_longest_time_without_failure_rate = SeriesRule.let_upper_limit_coins_without_failure_rate(
                spec=spec,
                p_time=p_time,
                q_time=q_time)

        return SeriesRule.let_upper_limit_coins_with_failure_rate(
                spec=spec,
                number_of_longest_time_without_failure_rate=number_of_longest_time_without_failure_rate)


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}SeriesRule
{indent}-------------------
{succ_indent}self._step_table:
{self._step_table.stringify_dump(succ_indent)}
{succ_indent}{self._shortest_coins=}
{succ_indent}{self._upper_limit_coins=}
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)=}
"""


class TrialResultsForOneSeries():
    """［シリーズ］１つ分の試行結果"""


    def __init__(self, spec, series_rule, failed_coins, point_calculation, list_of_face_of_coin):
        """初期化
    
        Parameters
        ----------
        spec : Specification
            ［仕様］
        series_rule : SeriesRule
            ［シリーズ・ルール］。値チェック用
        failed_coins : int
            ［表も裏も出なかった対局数］
        point_calculation : PointCalculation
            ［勝ち点計算］
        list_of_face_of_coin : list

        """

        # 共通
        self._spec = spec
        self._failed_coins = failed_coins
        self._series_rule = series_rule
        self._point_calculation = point_calculation
        self._list_of_face_of_coin = list_of_face_of_coin


    # 共通
    # ----

    @property
    def spec(self):
        return self._spec
    

    @property
    def point_calculation(self):
        """［勝ち点計算］"""
        return self._point_calculation


    @property
    def number_of_times(self):
        """行われた対局数"""
        return len(self._list_of_face_of_coin)


    @property
    def failed_coins(self):
        """［表も裏も出なかった対局数］"""
        return self._failed_coins


    @property
    def list_of_face_of_coin(self):
        """"""
        return self._list_of_face_of_coin


    def is_pts_won(self, winner):
        """winner の［勝ち点］は［目標の点数］に達していないが、 loser の［勝ち点］より多くて winner さんの勝ち
        
        FIXME Points Won というのは、シリーズ中に引き分けの対局が１つ以上あって、かつ、相手より点数が多く、かつ、自分が［目標の点数］に達していない状態
        """
        loser = Converter.opponent(winner)
        return 0 < self.failed_coins and not self._point_calculation.is_fully_won(player=winner) and self._point_calculation.x_has_more_than_y(winner, loser)


    def is_won(self, winner):
        """FIXME このシリーズで winner が loser に勝ったか？"""

        loser = Converter.opponent(winner)

        # 両者が満点勝ちしている、これはおかしい
        if self._point_calculation.is_fully_won(winner) and self._point_calculation.is_fully_won(loser):
            print(f"""\
TrialResultsForOneSeries
------------------------
self._point_calculation.stringify_dump:
{self._point_calculation.stringify_dump(INDENT)}
{self._list_of_face_of_coin=}
""")

            score_board = ScoreBoard(
                    spec=self._spec,
                    series_rule=self._series_rule,
                    list_of_face_of_coin=self._list_of_face_of_coin)
            print(score_board.stringify_csv())

            raise ValueError(f"両者が満点勝ちしている、これはおかしい {winner=}  {loser=}  {self.point_calculation.is_fully_won(winner)=}  {self.point_calculation.is_fully_won(loser)=}  {self._series_rule.step_table.span=}")

        # 両者が判定勝ちしている、これはおかしい
        if self.is_pts_won(winner=winner) and self.is_pts_won(winner=loser):
            print(f"""\
TrialResultsForOneSeries
------------------------
self._point_calculation.stringify_dump:
{self._point_calculation.stringify_dump(INDENT)}
{self._list_of_face_of_coin=}
""")
            raise ValueError(f"両者が判定勝ちしている、これはおかしい {winner=}  {loser=}  {self.is_pts_won(winner=winner)=}  {self.is_pts_won(winner=loser)=}  {self._series_rule.step_table.span=}")

        # 満点勝ちなら確定、判定勝ちでもOK 
        return self.point_calculation.is_fully_won(winner) or self.is_pts_won(winner=winner)


    def is_no_won(self):
        """TODO 勝者なし。どちらも勝者でないとき"""
        return not self.is_won(ALICE) and not self.is_won(BOB)


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}TrialResultsForOneSeries
{indent}------------------------
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)}
{succ_indent}{self.number_of_times=}
{succ_indent}{self._failed_coins=}
{succ_indent}self._series_rule.stringify_dump(succ_indent):
{self._series_rule.stringify_dump(succ_indent)=}
{succ_indent}self._point_calculation:
{self._point_calculation.stringify_dump(succ_indent)}
{succ_indent}{self._list_of_face_of_coin=}
{succ_indent}{self.is_pts_won(winner=ALICE)=}
{succ_indent}{self.is_pts_won(winner=BOB)=}
{succ_indent}{self.is_won(winner=ALICE)=}
{succ_indent}{self.is_won(winner=BOB)=}
{succ_indent}{self.is_no_won()}
"""
    

class LargeSeriesTrialSummary():
    """［大量のシリーズを試行した結果］"""


    def __init__(self, list_of_trial_results_for_one_series):
        """初期化
        
        Parameters
        ----------
        list_of_trial_results_for_one_series : list
            ［シリーズ］の結果のリスト
        """

        self._list_of_trial_results_for_one_series = list_of_trial_results_for_one_series
        self._shortest_time_th = None
        self._longest_time_th = None
        self._successful_series = None
        self._failed_series = None

        # （Fully wins）［満点勝ち］数。二次元配列[challenged][PLAYERS]
        self._ful_wins = [
            # 未使用
            None,
            # ［引き分けが起こらなかったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［満点勝ち］数
                None],  # Ｂさんの［満点勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［満点勝ち］数
                None],  # Ｂさんの［満点勝ち］数
        ]

        # （Points wins）［勝ち点判定勝ち］の件数。二次元配列[challenged][PLAYERS]
        self._pts_wins = [
            # 未使用
            None,
            # ［引き分けが起こらなかったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［満点勝ち］数
                None],  # Ｂさんの［満点勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［満点勝ち］数
                None],  # Ｂさんの［満点勝ち］数
        ]

        # ［勝者がなかった回数］。ＡさんとＢさんについて。初期値は None
        self._no_wins = None


    # 共通
    # ----

    @property
    def total(self):
        """シリーズ数"""

        # FIXME 検算をしている

        # 全部＝［表でも裏でもないものは出なかったシリーズの数］＋［表でも裏でもないものが出たシリーズの数］
        succ = self.successful_series
        fail = self.failed_series
        total_2 = succ + fail

        s_wins_a = self.wins(challenged=SUCCESSFUL, winner=ALICE)
        s_wins_b = self.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_a = self.wins(challenged=FAILED, winner=ALICE)
        f_wins_b = self.wins(challenged=FAILED, winner=BOB)

        s_ful_wins_a = self.ful_wins(challenged=SUCCESSFUL, winner=ALICE)
        s_pts_wins_a = self.pts_wins(challenged=SUCCESSFUL, winner=ALICE)
        s_ful_wins_b = self.ful_wins(challenged=SUCCESSFUL, winner=BOB)
        s_pts_wins_b = self.pts_wins(challenged=SUCCESSFUL, winner=BOB)
        f_ful_wins_a = self.ful_wins(challenged=FAILED, winner=ALICE)
        f_pts_wins_a = self.pts_wins(challenged=FAILED, winner=ALICE)
        f_ful_wins_b = self.ful_wins(challenged=FAILED, winner=BOB)
        f_pts_wins_b = self.pts_wins(challenged=FAILED, winner=BOB)

        if s_wins_a != (s_ful_wins_a + s_pts_wins_a):
            raise ValueError(f"合計が合いません {s_wins_a=} != ({s_ful_wins_a=} + {s_pts_wins_a=})")

        if s_wins_b != (s_ful_wins_b + s_pts_wins_b):
            raise ValueError(f"合計が合いません {s_wins_b=} != ({s_ful_wins_b=} + {s_pts_wins_b=})")

        if f_wins_a != (f_ful_wins_a + f_pts_wins_a):
            raise ValueError(f"合計が合いません {f_wins_a=} != ({f_ful_wins_a=} + {f_pts_wins_a=})")

        if f_wins_b != (f_ful_wins_b + f_pts_wins_b):
            raise ValueError(f"合計が合いません {f_wins_b=} != ({f_ful_wins_b=} + {f_pts_wins_b=})")


        # 全部  ＝  ［表でも裏でもないものは出なかったシリーズでＡさんが勝った数］＋
        #           ［表でも裏でもないものは出なかったシリーズでＢさんが勝った数］＋
        #           NOTE これはない？ ［表でも裏でもないものは出なかったシリーズで、かつ勝ち負け付かずのシリーズの数］＋
        #           ［表でも裏でもないものが出たシリーズでＡさんが勝った数］＋
        #           ［表でも裏でもないものが出たシリーズでＢさんが勝った数］＋
        #           ［勝ち負け付かずのシリーズ数］
        #
        # FIXME 合計が合いません。
        #   total_1=21638  total_2=20000
        #   s_wins_a=0(s_ful_wins_a=0 + s_pts_wins_a=0) +
        #   s_wins_b=0(s_ful_wins_b=0 + s_pts_wins_b=0) +
        #   f_wins_a= 9155(f_ful_wins_a=9141 + f_pts_wins_a=14) +
        #   f_wins_b=10793(f_ful_wins_b=10775 + f_pts_wins_b=18) +
        #   self.no_wins=52
        #   succ=13269  fail=6731
        total_1 = s_wins_a + s_wins_b + f_wins_a + f_wins_b + self.no_wins

        if total_1 != total_2:
            raise ValueError(f"""合計が合いません。 {total_1=}  {total_2=}\
   {s_wins_a=}({s_ful_wins_a=} + {s_pts_wins_a=})\
 + {s_wins_b=}({s_ful_wins_b=} + {s_pts_wins_b=})\
 + {f_wins_a=}({f_ful_wins_a=} + {f_pts_wins_a=})\
 + {f_wins_b=}({f_ful_wins_b=} + {f_pts_wins_b=})\
 + {self.no_wins=}\
 {succ=}  {fail=}""")

        return total_1


    @property
    def shortest_time_th(self):
        """［最短対局数］"""
        if self._shortest_time_th is None:
            self._shortest_time_th = 2_147_483_647
            for s in self._list_of_trial_results_for_one_series:
                if s.number_of_times < self._shortest_time_th:
                    self._shortest_time_th = s.number_of_times

        return self._shortest_time_th


    @property
    def longest_time_th(self):
        """［上限対局数］"""
        if self._longest_time_th is None:
            self._longest_time_th = 0
            for s in self._list_of_trial_results_for_one_series:
                if self._longest_time_th < s.number_of_times:
                    self._longest_time_th = s.number_of_times

        return self._longest_time_th


    @property
    def successful_series(self):
        """［表も裏も出なかった対局を含まないシリーズ数］"""
        if self._successful_series is None:
            self._successful_series = 0
            for s in self._list_of_trial_results_for_one_series:
                if s.failed_coins < 1:
                    self._successful_series += 1

        return self._successful_series


    @property
    def failed_series(self):
        """［表も裏も出なかった対局を含むシリーズ数］"""
        if self._failed_series is None:
            self._failed_series = 0
            for s in self._list_of_trial_results_for_one_series:
                if 0 < s.failed_coins:
                    self._failed_series += 1

        return self._failed_series


    def ful_wins(self, challenged, winner):
        """elementary_event が［目標の点数］を集めて勝った回数

        TODO 勝利数は、［引き分けが起こったシリーズか、起こってないシリーズか］［目標の点数に達したか、点数差での判定勝ちか］も分けてカウントしたい
        """
        if self._ful_wins[challenged][winner] is None:
            self._ful_wins[challenged][winner] = 0
            for s in self._list_of_trial_results_for_one_series:

                if challenged == SUCCESSFUL:
                    if 0 < s.failed_coins:
                        # ［引き分けが起こらなかったシリーズ］ではない
                        continue
                
                elif challenged == FAILED:
                    if s.failed_coins < 1:
                        # ［引き分けが起こったシリーズ］ではない
                        continue
                
                else:
                    raise ValueError(f"{challenged=}")

                if not s.point_calculation.is_fully_won(winner):
                    # ［目標の点数］を満たしてない
                    continue

                self._ful_wins[challenged][winner] += 1

        return self._ful_wins[challenged][winner]


    def pts_wins(self, challenged, winner):
        """winner が［勝ち点差判定］で loser に勝った回数

        TODO 勝利数は、［引き分けが起こったシリーズか、起こってないシリーズか］［目標の点数に達したか、点数差での判定勝ちか］も分けてカウントしたい
        """
        loser = Converter.opponent(winner)
        if self._pts_wins[challenged][winner] is None:
            self._pts_wins[challenged][winner] = 0
            for s in self._list_of_trial_results_for_one_series:

                if challenged == SUCCESSFUL:
                    if 0 < s.failed_coins:
                        # ［引き分けが起こらなかったシリーズ］ではない
                        continue
                
                elif challenged == FAILED:
                    if s.failed_coins < 1:
                        # ［引き分けが起こったシリーズ］ではない
                        continue
                
                else:
                    raise ValueError(f"{challenged=}")

                if not s.is_pts_won(winner=winner):
                    # ［点差による勝ち］ではないい
                    continue

                self._pts_wins[challenged][winner] += 1


        return self._pts_wins[challenged][winner]


    @property
    def number_of_no_won_series(self):
        """［勝敗付かず］で終わったシリーズ数"""

        # ［Ａさんが勝った回数］と［Ｂさんが勝った回数］を数えるメソッドの働きの確認をしている
        #
        #   シリーズ数　－　［Ａさんが勝った回数］　－　［Ｂさんが勝った回数］
        #
        s_wins_a = self.wins(challenged=SUCCESSFUL, winner=ALICE)
        s_wins_b = self.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_a = self.wins(challenged=FAILED, winner=ALICE)
        f_wins_b = self.wins(challenged=FAILED, winner=BOB)

        return self.total - (s_wins_a + s_wins_b + f_wins_a + f_wins_b)


    def won_rate(self, success_rate, winner):
        """試行した結果、 winner が loser に勝った率

        ［コインの表か裏が出た確率］ × ［winner が loser に勝った回数］ / ［シリーズ数］

        Parameters
        ----------
        success_rate : float
            ［コインの表か裏が出た確率］
        winner : int
            ［Ａさん］か［Ｂさん］

        """
        return success_rate * self.wins(winner=winner) / self.total


    def won_rate_error(self, success_rate, winner):
        """試行した結果、 winner が loser に勝った率と0.5との誤差］

        ［試行した結果、 winner が loser に勝った率］ - 0.5

        Parameters
        ----------
        success_rate : float
            ［コインの表か裏が出た確率］
        winner : int
            ［コインの表］か［コインの裏］か［Ａさん］か［Ｂさん］
        """
        return self.won_rate(success_rate=success_rate, winner=winner) - 0.5


    def trial_no_won_series_rate(self):
        """試行した結果、［勝敗付かず］で終わったシリーズの割合"""
        return self.number_of_no_won_series / self.total


    def wins(self, challenged, winner):
        """winner が loser に勝った数"""
        return self.ful_wins(challenged=challenged, winner=winner) + self.pts_wins(challenged=challenged, winner=winner)


    @property
    def no_wins(self):
        """勝者がなかった回数"""
        if self._no_wins is None:
            self._no_wins = 0
            for s in self._list_of_trial_results_for_one_series:
                if s.is_no_won():
                    self._no_wins += 1

        return self._no_wins


class Candidate():
    """［シリーズ・ルール候補］"""


    def __init__(self, p_error, number_of_series, p_step, q_step, span, shortest_coins, upper_limit_coins):

        if not isinstance(number_of_series, int):
            raise ValueError(f"［試行シリーズ回数］は int 型である必要があります {number_of_series=}")

        if not isinstance(p_step, int):
            raise ValueError(f"［表番の勝ち１つ分の点数］は int 型である必要があります {p_step=}")

        if not isinstance(q_step, int):
            raise ValueError(f"［裏番の勝ち１つ分の点数］は int 型である必要があります {q_step=}")

        if not isinstance(span, int):
            raise ValueError(f"［目標の点数］は int 型である必要があります {span=}")

        if not isinstance(shortest_coins, int):
            raise ValueError(f"［最短対局数］は int 型である必要があります {shortest_coins=}")

        if not isinstance(upper_limit_coins, int):
            raise ValueError(f"［上限対局数］は int 型である必要があります {upper_limit_coins=}")

        self._p_error = p_error
        self._number_of_series = number_of_series
        self._p_step = p_step
        self._q_step = q_step
        self._span = span
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


    @property
    def p_error(self):
        return self._p_error


    @property
    def number_of_series(self):
        return self._number_of_series


    @property
    def p_step(self):
        return self._p_step


    @property
    def q_step(self):
        return self._q_step


    @property
    def span(self):
        return self._span


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    def as_str(self):
        # NOTE 可読性があり、かつ、パースのしやすい書式にする
        return f'[{self._p_error:.6f} {self._p_step}表 {self._q_step}裏 {self._span}目 {self._shortest_coins}～{self._upper_limit_coins}局 {self._number_of_series}試]'


    _re_pattern_of_candidate = None

    @classmethod
    def parse_candidate(clazz, candidate):

        if clazz._re_pattern_of_candidate is None:
            clazz._re_pattern_of_candidate = re.compile(r'([0-9.-]+) (\d+)表 (\d+)裏 (\d+)目 (\d+)～(\d+)局 (\d+)試')

        result = _re_pattern_of_candidate.match(candidate)
        if result:
            return Candidate(
                    p_error=float(result.group(1)),
                    number_of_series=float(result.group(7)),
                    p_step=int(result.group(2)),
                    q_step=int(result.group(3)),
                    span=int(result.group(4)),
                    shortest_coins=int(result.group(5)),
                    upper_limit_coins=int(result.group(6)))

        raise ValueError(f"パースできません {candidate=}")


class ScoreBoard():
    """１シリーズ分の経過の記録。
    以下の表のようなものを作る。CSVで出力する

    ［先後固定制］
    -------------

        Specification
        p        failure_rate  turn_system
        70.0000  10.0000       frozen

        Series Rule
        p_step  q_step  span
        2       3       6

        Score Sheet
                 S   1   2   3  4   5
        表番        Ａ  Ａ  Ａ  Ａ  Ａ
        出目        表  表  裏  失  表
        Ａさん   6   4   2   2   2  0
        Ｂさん   6   6   6   3   3  3

        Result
        Ａさんの勝ち

    ［先後交互制］
    -------------

        Specification
        p        failure_rate  turn_system
        70.0000  10.0000       alternating

        Series Rule
        p_step  q_step  span
        2       3       6

        Score Sheet
                S   1   2   3   4   5
        表番        Ａ  Ｂ  Ａ  Ｂ  Ａ
        出目        表  表  裏  失  表
        Ａさん  6    4   4   1   1  -1
        Ｂさん  6    6   4   4   4   4

        Result
        Ａさんの勝ち
    """


    def __init__(self, spec, series_rule, list_of_face_of_coin):
        """初期化

        Parameters
        ----------
        spec : Specification
            ［仕様］
        series_rule : SeriesRule
            ［シリーズ・ルール］
        list_of_face_of_coin : list
            コイントスした結果のリスト。引き分け含む
        """
        self._spec = spec
        self._series_rule = series_rule
        self._list_of_face_of_coin = list_of_face_of_coin


    @property
    def spec(self):
        """［仕様］"""
        return self._spec
    

    @property
    def series_rule(self):
        """［シリーズ・ルール］"""
        return self._series_rule


    @property
    def list_of_face_of_coin(self):
        """コイントスした結果のリスト。引き分け含む"""
        return self._list_of_face_of_coin


    def stringify_csv(self):
        """TODO"""

        span = self._series_rule.step_table.span
        h_step = self._series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)
        t_step = self._series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)
        shortest_coins = self._series_rule.shortest_coins
        upper_limit_coins = self._series_rule.upper_limit_coins

        if h_step < 1:
            raise ValueError(f"正の整数でなければいけません {h_step=}")

        if t_step < 1:
            raise ValueError(f"正の整数でなければいけません {t_step=}")


        t11 = f"{self._spec.p * 100:7.4f}"
        t12 = f"{self._spec.failure_rate * 100:7.4f}"
        t13 = Converter.turn_system_to_code(self._spec.turn_system)

        t21 = f"{h_step}"
        t22 = f"{t_step}"
        t23 = f"{span}"
        t24 = f"{shortest_coins}"
        t25 = f"{upper_limit_coins}"

        csv = f"""\
Specification
p    , failure_rate, turn_system  
{t11}, {t12}       , {t13}

Series Rule
h_step, t_step, span , shortest_coins, upper_limit_coins
{t21} , {t22} , {t23}, {t24}         , {t25}

Source Data
{self._list_of_face_of_coin=}

Score Sheet
"""

        a_point = span
        b_point = span

        round_list = []
        round_list.append(['S', '', '  ', a_point, b_point])

        for round_th, face_of_coin in enumerate(self._list_of_face_of_coin, 1):
            last_round = round_list[-1]

            if last_round[1] in ['', 'B']:
                head_player = 'A'
            else:
                head_player = 'B'

            face_of_coin_str = Converter.face_of_coin_to_str(face_of_coin)

            if face_of_coin == HEAD:
                if head_player == 'A':
                    a_point -= h_step
                else:
                    b_point -= h_step

            elif face_of_coin == TAIL:
                if head_player == 'A':
                    b_point -= t_step
                else:
                    a_point -= t_step

            elif face_of_coin == EMPTY:
                pass

            else:
                raise ValueError(f"{face_of_coin=}")
            

            round_list.append([round_th, head_player, face_of_coin_str, a_point, b_point])


        list_of_round_number = ['      ']        # ラウンド番号
        list_of_head_player = ['表番  ']
        list_of_face_of_coin_str = ['出目  ']
        list_of_a_points = ['Ａさん']
        list_of_b_points = ['Ｂさん']

        for round in round_list:
            list_of_round_number.append(f"{round[0]:>3}")
            list_of_head_player.append(f"{round[1]:>3}")
            list_of_face_of_coin_str.append(f" {round[2]}")
            list_of_a_points.append(f"{round[3]:>3}")
            list_of_b_points.append(f"{round[4]:>3}")

        csv += f"""\
{','.join(list_of_round_number)}
{','.join(list_of_head_player)}
{','.join(list_of_face_of_coin_str)}
{','.join(list_of_a_points)}
{','.join(list_of_b_points)}

"""

        if list_of_a_points[-1] < list_of_b_points[-1]:
            csv += "Ａさんの勝ち"

        elif list_of_b_points[-1] < list_of_a_points[-1]:
            csv += "Ｂさんの勝ち"
        
        else:
            csv += "勝者なし"


        return csv


    def stringify_dump(self, indent):
        """ダンプ"""
        succ_indent = indent + INDENT
        return f"""\
{indent}ElementaryEventSequence
{indent}-----------------------
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)}
{succ_indent}{self._upper_limit_coins=}
{succ_indent}{self._list_of_face_of_coin=}
"""
