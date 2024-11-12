#
# 共通コード
#
#   ファイル出力、ログ等を除く
#

import os
import shutil
import time
import random
import math
import datetime
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


# Geme results
# ------------
IN_GAME = 0             # ゲーム中
ALICE_FULLY_WON = 1     # Ａさんの達成勝ち
BOB_FULLY_WON = 2       # Ｂさんの達成勝ち
ALICE_POINTS_WON = 3    # Ａさんの勝ち点差勝ち
BOB_POINTS_WON = 4      # Ｂさんの勝ち点差勝ち
NO_WIN_MATCH = 5        # 勝者無し。１局としては成立
#UNSUCCESSFUL_GAME = 6   # 不成立試合。プログラミングのエラーなどが発生して結果付かず


# Calculation status
# ------------------
TERMINATED = 1          # 計算は停止した
YIELD = 2               # 途中まで処理したところでタイムアップした（時間を譲った）
CONTINUE = 3            # 計算中だ。時間も譲らない。計算を続行する
CALCULATION_FAILED = 4  # 計算しようとしているが、計算できなかったケース。シェアされる時間が足りてないなど


# 範囲外のあり得ない値。浮動小数点が大きすぎてオーバーフロー例外が出て計算不可能だったケースなど
UPPER_OUT_OF_P = 1.01


# 誤差の範囲外のありえない値の絶対値。勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差の絶対値は 0.5 が最大
ABS_OUT_OF_ERROR = 0.51


# 小数点第４位を四捨五入しても 0.01% の精度が出るように
SMALL_P_ABS_ERROR = 0.0004


# 五分五分
EVEN = 0.5


#################
# MARK: Precision
#################
class Precision():


    @staticmethod
    def is_almost_zero(rate):
        """ほぼ 0 か？"""
        return -0.0000000001 <= rate and rate <= 0.0000000001


    @staticmethod
    def is_almost_one(rate):
        """ほぼ 1 か？
        これは、［ほぼ］ではなく 1 なのに、２進数が割り切れない都合で 0.9999999999999984 や 1.0000000000123324 になってしまうケースを 1 と判定したいときがある
        """
        return 0.9999999999 <= rate and rate <= 1.0000000001


    @staticmethod
    def is_almost_even(rate):
        """ほぼ五分か？"""
        return 0.4999999999 <= rate and rate <= 0.5000000001


    @staticmethod
    def is_it_zero_enough(rate):
        """じゅうぶん 0 か？
        つまり、小数点第４位を四捨五入して 0 か？

        負数は絶対値にして四捨五入して負の符号を付けるものとする
        """
        return -0.0004 <= rate and rate <= 0.0004


    @staticmethod
    def is_it_one_enough(rate):
        """じゅうぶん 1 か？
        つまり、小数点第４位を四捨五入して 1 か？
        """
        return 0.9995 <= rate and rate <= 1.0004


    @staticmethod
    def is_it_even_enough(rate):
        """じゅうぶん五分か？
        つまり、小数点第４位を四捨五入して５分か？
        """
        return 0.4995 <= rate and rate <= 0.5004


#################
# MARK: Converter
#################
class Converter():
    """変換する機能まとめ"""


    _face_of_coin_to_str = None

    @classmethod
    def face_of_coin_to_str(clazz, face_of_coin):
        if clazz._face_of_coin_to_str is None:
            clazz._face_of_coin_to_str = {
                EMPTY: '失',    # 失敗の頭文字
                HEAD : '表',
                TAIL : 'ｳﾗ',    # 表と裏の字が似すぎているので、"裏" から "ｳﾗ" へ仕様変更した
            }
        
        return clazz._face_of_coin_to_str[face_of_coin]


    _turn_system_to_readable = None

    @classmethod
    def turn_system_id_to_readable(clazz, turn_system_id):
        if clazz._turn_system_to_readable is None:
            clazz._turn_system_to_readable = {
                FROZEN_TURN : '先後固定制',
                ALTERNATING_TURN : '先後交互制',
            }

        return clazz._turn_system_to_readable[turn_system_id]


    _turn_system_to_name = None

    @classmethod
    def turn_system_id_to_name(clazz, turn_system_id):
        if clazz._turn_system_to_name is None:
            clazz._turn_system_to_name = {
                FROZEN_TURN : 'frozen',
                ALTERNATING_TURN : 'alternating',
            }

        return clazz._turn_system_to_name[turn_system_id]


    _code_to_turn_system = None

    @classmethod
    def turn_system_code_to_id(clazz, code):
        if clazz._code_to_turn_system is None:
            clazz._code_to_turn_system = {
                'froze' : FROZEN_TURN,      # ファイル名で使用
                'frozen' : FROZEN_TURN,
                'alter' : ALTERNATING_TURN, # ファイル名で使用
                'alternating' : ALTERNATING_TURN,
            }

        return clazz._code_to_turn_system[code]


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


    _precision_to_trial_series = {
        -1: 1
    }


    @staticmethod
    def precision_to_trial_series(precision):
        """
        下式の通り

            trial_series = 2 * 10 ^ precision

            # 逆関数は precision = lg(trial_series / 2)

        NOTE n を 0 にしても 2 になるので、 1 にするには 0.3000...ちょっとの数だから整数では precision を指定できない

        precision  trial_series
        ---------  -------------
                0              2
                1             20
                2            200
                3           2000
                4          20000
                5         200000
                6        2000000
        
        precision はゼロの数と覚えると覚えやすい

        Parameters
        ----------
        precision : int
            ［精度］
        """
        return 2 * 10 ** precision


    @staticmethod
    def precision_to_small_error(precision):
        """誤差がこの数以下なら十分だ、といったように判定するのに使う閾値。precision_to_trial_series() に対応。

        small_error = 0.9 * 10^-precision

        precision  small_error
        ---------  -----------
                0  0.9
                1  0.09
                2  0.009
                3  0.0009
                4  0.00009
                5  0.000009
                6  0.0000009
                       
        
        precision は小数点以下のゼロの数と覚えると覚えやすい

        Parameters
        ----------
        precision : int
            ［精度］
        """
        return 0.9 * 10 ** -precision


    _calculation_status_to_code = {
        TERMINATED : 'terminated',
        YIELD : 'yield',
        CONTINUE : 'continue'}

    @classmethod
    def calculation_status_to_code(clazz, calculation_status):
        return clazz._calculation_status_to_code[calculation_status]


#####################
# MARK: Specification
#####################
class Specification():
    """仕様"""


    @staticmethod
    def by_three_rates(turn_system_id, failure_rate, head_rate):
        """表が出る確率、ｳﾗが出る確率、表もｳﾗも出ない確率を足して 1 になるよう指定する方法"""
        return Specification(
                p=(1 - failure_rate) * head_rate,
                failure_rate=failure_rate,
                turn_system_id=turn_system_id)


    def __init__(self, p, failure_rate, turn_system_id):
        """初期化

        Parameters
        ----------
        p : float
            ［表が出る確率］
        failure_rate : float
            ［表も裏も出ない確率］。例： １割が引き分けなら 0.1
        turn_system_id : int
            ［先後の決め方］
        """

        self._p = p
        self._failure_rate = failure_rate
        self._turn_system_id = turn_system_id


    @property
    def p(self):
        """［表が出る確率］"""
        return self._p


    @property
    def failure_rate(self):
        """［表も裏も出ない確率］"""
        return self._failure_rate


    @property
    def turn_system_id(self):
        """［先後運営制度］"""
        return self._turn_system_id


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}Specification
{indent}-------------
{succ_indent}{self._p=}
{succ_indent}{self._failure_rate=}
{succ_indent}{self._turn_system_id=}
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


def p_to_b_t_times(p):
    """［表が出る確率］ p を与えると、［表勝ちだけでの対局数］、［裏勝ちだけでの対局数］を返す
    
    Parameters
    ----------
    p : float
        ［表が出る確率］
    
    Returns
    -------
    h_time : int
        ［表勝ちだけでの対局数］
    t_time : int
        ［裏勝ちだけでの対局数］
    """

    # 説明２  コインの表裏の確率の整数化
    # --------------------------------
    scale = scale_for_float_to_int(p)

    # ［表勝ちだけでの対局数］基礎
    #
    #   NOTE int() を使って小数点以下切り捨てしようとすると、57 が 56 になったりするので、四捨五入にする
    #
    h_time = round_letro(p * scale)

    # ［裏勝ちだけでの対局数］基礎
    t_time = scale - h_time

    # 約分する
    fraction = Fraction(h_time, t_time)
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


##################
# MARK: SeriesRule
##################
class SeriesRule():
    """［シリーズ・ルール］
    
    NOTE ［最短対局数］、［上限対局数］は指定できず、計算で求めるもの
    """


    @staticmethod
    def let_t_time(span, t_step):
        """［コインを投げてｳﾗが出続けてシリーズ優勝できる回数］を算出。
        計算方法は、 span / t_step ※小数点切り上げ"""
        return math.ceil(span / t_step)


    @staticmethod
    def let_h_time(span, h_step):
        """［コインを投げて表が出続けてシリーズ優勝できる回数］を算出。
        計算方法は、 span / h_step ※小数点切り上げ"""
        return math.ceil(span / h_step)


    @staticmethod
    def let_t_step_divisible_by_h_step(t_step, h_step, h_time):
        """t_step を h_step で割り切れるときの、その割る数を算出。
        割り切れないなら 0"""

        # 割り切れないなら 0
        if t_step % h_step != 0 or t_step // h_step >= h_time:
            return 0

        # 割り切れるなら、割る数
        return t_step // h_step


    @staticmethod
    def let_t_time_by_duet(span, step_list):
        """［コインを投げてｳﾗだけ出続けたときに優勝する最短対局数］を算出

        ［コインを投げて表も裏も出ない確率］は 0 とする。
        計算には step の事前計算が必要

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
        return round_letro(math.ceil(span / step_list[TAIL]))


    @staticmethod
    def let_h_time_by_duet(span, step_list):
        """［コインを投げて表だけ出続けたときに優勝する最短対局数］を算出

        ［コインを投げて表も裏も出ない確率］は 0 とする。
        計算には step の事前計算が必要

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
        return round_letro(math.ceil(span / step_list[HEAD]))


    @staticmethod
    def let_shortest_coins(h_step, t_step, span, turn_system_id):
        """［最短対局数］を算出"""


        if turn_system_id == FROZEN_TURN:
            """［先後固定制］での［最短対局数］
            
            裏が全勝したときの回数と同じ

            `先手勝ち 1点、後手勝ち 2点　目標 10点` のとき、先後固定制で最長は？
                ・  裏  裏  裏  裏  裏  で、最短５局
                10  10  10  10 10  10
                10   8   6   4  2   0
            """

            # ［目標の点数］は最小公倍数なので割り切れる
            return round_letro(span / t_step)


        if turn_system_id == ALTERNATING_TURN:
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

            successful_step = h_step + t_step

            if h_step + t_step <= remainder:
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
                remainder -= t_step

                # まだ端数があれば［表勝ち１つの点数］を引く（１回分を加算）
                if 0 < remainder:
                    time += 1
                    remainder -= h_step

                    # remainder は負数になっているはず（割り切れないはず）
                    if 0 <= remainder:
                        raise ValueError(f"ここで余りが負数になっていないのはおかしい {remainder=}  {span=}  {h_step=}  {t_step=}")
                
                # remainder は零か負数になっているはず
                elif 0 < remainder:
                    raise ValueError(f"ここで余りが零か負数になっていないのはおかしい {remainder=}  {span=}  {h_step=}  {t_step=}")


            return time


        raise ValueError(f"{turn_system_id=}")


    @staticmethod
    def let_upper_limit_coins_without_failure_rate(spec, h_time, t_time):
        """［上限対局数］を算出

        これは［コインを投げて表もｳﾗも出ない確率］がゼロのケースです

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        # ［先後固定制］
        if spec.turn_system_id == FROZEN_TURN:
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
            return  h_time + t_time - 1


        # ［先後交互制］
        if spec.turn_system_id == ALTERNATING_TURN:
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
            return 2 * h_time - 1


        raise ValueError(f"{spec.turn_system_id=}")


    @staticmethod
    def let_upper_limit_coins_with_failure_rate(spec, upper_limit_coins_without_failure_rate):
        """［上限対局数］を算出

        これは［コインを投げて表もｳﾗも出ない確率］がゼロのケース、ゼロではないときのケースの両方を一般化したものです

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
        
        の y を求めたい。 y は１シリーズの中での試行対局数。（10 は、failure_rate=0 のときの試行シリーズ数）

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
        return math.ceil(upper_limit_coins_without_failure_rate / (1 - spec.failure_rate))


    @staticmethod
    def let_upper_limit_coins(spec, time_list):
        """［上限対局数］を算出

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        upper_limit_coins_without_failure_rate = SeriesRule.let_upper_limit_coins_without_failure_rate(
                spec=spec,
                h_time=time_list[HEAD],
                t_time=time_list[TAIL])

        return SeriesRule.let_upper_limit_coins_with_failure_rate(
                spec=spec,
                upper_limit_coins_without_failure_rate=upper_limit_coins_without_failure_rate)


    @staticmethod
    def make_series_rule_auto_span(spec, h_time, t_time):
        """［表勝ちだけでの対局数］と［裏勝ちだけでの対局数］が分かれば、［かくきんシステムのｐの構成］を分析して返す
        
        Parameters
        ----------
        spec : Specificetion
            ［仕様］
        h_time : int
            ［表勝ちだけでの対局数］
        t_time : int
            ［裏勝ちだけでの対局数］
        """
        # DO 通分したい。最小公倍数を求める
        lcm = math.lcm(h_time, t_time)
        # ［表番で勝ったときの勝ち点］
        #
        #   NOTE 必ず割り切れるが、 .00001 とか .99999 とか付いていることがあるので、四捨五入して整数に変換しておく
        #
        h_step = round_letro(lcm / h_time)
        # ［裏番で勝ったときの勝ち点］
        t_step = round_letro(lcm / t_time)
        # ［目標の点数］
        span = round_letro(t_time * t_step)

        # データチェック
        span_w = round_letro(h_time * h_step)
        if span != span_w:
            raise ValueError(f"{span=}  {span_w=}")

        return SeriesRule.make_series_rule_base(
                spec=spec,
                span=span,
                t_step=t_step,
                h_step=h_step)


    @staticmethod
    def make_series_rule_base(spec, span, t_step, h_step):
        """
        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        # NOTE numpy.int64 型は、 float NaN が入っていることがある？
        if not isinstance(h_step, int):
            raise ValueError(f"int 型であることが必要 {type(h_step)=}  {h_step=}")

        if not isinstance(t_step, int):
            raise ValueError(f"int 型であることが必要 {type(t_step)=}  {t_step=}")

        if not isinstance(span, int):
            raise ValueError(f"int 型であることが必要 {type(span)=}  {span=}")

        if h_step < 1:
            raise ValueError(f"正の整数であることが必要 {h_step=}")

        if t_step < 1:
            raise ValueError(f"正の整数であることが必要 {t_step=}")

        if span < 1:
            raise ValueError(f"正の整数であることが必要 {span=}")

        if t_step < h_step:
            raise ValueError(f"［コインの表が出たときの勝ち点］{h_step=} が、［コインの裏が出たときの勝ち点］ {t_step} を上回るのはおかしいです")

        if span < t_step:
            raise ValueError(f"［コインの裏が出たときの勝ち点］{t_step=} が、［目標の点数］{span} を上回るのはおかしいです")


        # ［最短対局数］
        shortest_coins = SeriesRule.let_shortest_coins(
                h_step=h_step,
                t_step=t_step,
                span=span,
                turn_system_id=spec.turn_system_id)

        step_list = [
                # 0: ［未使用］
                None,
                # 1: ［表番で勝ったときの勝ち点］
                h_step,
                # 2: ［裏番で勝ったときの勝ち点］
                t_step]

        time_list = [
                # 0: ［未使用］
                None,
                # 1: ［コインを投げて表だけ出続けたときに優勝する最短対局数］
                SeriesRule.let_h_time_by_duet(span=span, step_list=step_list),
                # 2: ［コインを投げてｳﾗだけ出続けたときに優勝する最短対局数］
                SeriesRule.let_t_time_by_duet(span=span, step_list=step_list)]

        # ［上限対局数］
        upper_limit_coins = SeriesRule.let_upper_limit_coins(
                spec=spec,
                time_list=time_list)


        # 検証
        if upper_limit_coins < shortest_coins:
            text = f"［最短対局数］{shortest_coins} が、［上限対局数］{upper_limit_coins} より長いです"

            succ_indent = INDENT
            print(f"""\
spec:
{spec.stringify_dump(succ_indent)}
{text}
{h_step=}
{t_step=}
{span=}
""")
            raise ValueError(text)


        return SeriesRule(
                spec=spec,
                span=span,
                step_list=step_list,
                time_list=time_list,
                shortest_coins=shortest_coins,          # ［最短対局数］
                upper_limit_coins=upper_limit_coins)    # ［上限対局数］


    def __init__(self, spec, span, step_list, time_list, shortest_coins, upper_limit_coins):
        """初期化
        
        Parameters
        ----------
        spec : Specification
            ［仕様］
        span : int
            ［目標の点数］
        step_list : list
            [0] - 未使用
            [1] - ［表番で勝ったときの勝ち点］
            [2] - ［裏番で勝ったときの勝ち点］
        time_list : list
            [0] - 未使用
            [1] - ［コインを投げて表だけ出続けたときに優勝する最短対局数］
            [2] - ［コインを投げてｳﾗだけ出続けたときに優勝する最短対局数］
        shortest_coins : int
            ［最短対局数］
        upper_limit_coins : int
            ［上限対局数］
        """

        self._spec = spec
        self._span = span
        self._step_list = step_list
        self._time_list = time_list
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


    @property
    def span(self):
        """［目標の点数］"""
        return self._span


    @property
    def spec(self):
        """［仕様］"""
        return self._spec


    @property
    def h_step(self):
        """［コインを投げて表が出る確率］"""
        return self._step_list[HEAD]


    @property
    def t_step(self):
        """［コインを投げてｳﾗが出る確率］"""
        return self._step_list[TAIL]


    @property
    def shortest_coins(self):
        """［最短対局数］"""
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        """［上限対局数］"""
        return self._upper_limit_coins


    def get_step_by(self, face_of_coin):
        """［表番または裏番で勝ったときの勝ち点］を取得します
        
        Parameters
        ----------
        face_of_coin : int
            ［コインの表か裏かそれ以外］
        """

        # ［コインの表が出たときの勝ち点］
        # ［コインの裏が出たときの勝ち点］
        # の２つに対応。他の値がきたらエラー
        return self._step_list[face_of_coin]


    def get_time_by(self, span, challenged, face_of_coin):
        """表、またはｳﾗだけが出続けたときの、優勝に必要な最短［対局数］を取得

        ［コインを投げて表も裏も出ない確率］は 0 とする。
        計算には step の事前計算が必要
        """

        return self._time_list[face_of_coin]


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}SeriesRule
{indent}-------------------
{succ_indent}{self._step_list=}
{succ_indent}{self._span=}
{succ_indent}{self._shortest_coins=}
{succ_indent}{self._upper_limit_coins=}
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)=}
"""


##################
# MARK: ThreeRates
##################
class ThreeRates():


    def __init__(self, a_win_rate, no_win_match_rate):
        """初期化

        ［Ａさんが勝つ確率］と［Ｂさんが勝つ確率］を足すと１００％になる。

        ［勝ち負けが付かない確率］は、［Ａさんが勝つ確率］、［Ｂさんが勝つ確率］とは関係なく、０～１００％で示される。

        Parameters
        ----------
        a_win_rate : float
            Ａさんが勝つ確率
        no_win_match_rate : float
            勝ち負けが付かない確率
        """
        self._a_win_rate = a_win_rate
        self._no_win_match_rate = no_win_match_rate


    @staticmethod
    def create_three_rates(a_win_rate, b_win_rate, no_win_match_rate):

        ab_win_rate = a_win_rate + b_win_rate
        if not Precision.is_almost_one(ab_win_rate):
            raise ValueError(f"［Ａさんの勝率］と［Ｂさんの勝率］を足したらピッタリ１００％になる必要があります。 {ab_win_rate=}  {a_win_rate=}  {b_win_rate=}  {no_win_match_rate=}")

        return ThreeRates(
                a_win_rate=a_win_rate,
                no_win_match_rate=no_win_match_rate)


    @property
    def a_win_rate(self):
        return self._a_win_rate


    @property
    def b_win_rate(self):
        return 1 - self._a_win_rate
    

    @property
    def no_win_match_rate(self):
        return self._no_win_match_rate


    @property
    def is_even(self):
        return Precision.is_it_even_enough(self._a_win_rate)
