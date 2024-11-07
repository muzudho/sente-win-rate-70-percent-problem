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


############################
# MARK: SequenceOfFaceOfCoin
############################
class SequenceOfFaceOfCoin():
    """［コインの表］、［コインの裏］、［コインの表でも裏でもないもの］の印が並んだもの"""


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

        path_of_face_of_coin = []

        # ［上限対局数］までやる
        for time_th in range(1, upper_limit_coins + 1):

            face_of_coin = toss_a_coin(
                    p=spec.p,
                    failure_rate=spec.failure_rate)

            path_of_face_of_coin.append(face_of_coin)


        return path_of_face_of_coin


    @staticmethod
    def cut_down(path_of_face_of_coin, number_of_coins):
        """コイントスの結果のリストの長さを切ります。
        対局は必ずしも［上限対局数］になるわけではありません"""
        return path_of_face_of_coin[0:number_of_coins]


############################
# MARK: TreeNodeOfFaceOfCoin
############################
class TreeNodeOfFaceOfCoin():
    """コインの出目のツリー構造のノード"""


    def __init__(self, face_of_coin, parent_node):
        """初期化
        
        Parameters
        ----------
        face_of_coin : int
            ルート・ノードならナン
        parent_node : TreeNodeOfFaceOfCoin
            親ノード。無ければナン
        """
        self._face_of_coin = face_of_coin
        self._parent_node = parent_node

        self._child_head = None
        self._child_tail = None
        self._child_failure = None


    @property
    def face_of_coin(self):
        return self._face_of_coin


    @property
    def parent_node(self):
        return self._parent_node


    @property
    def child_head(self):
        return self._child_head


    @property
    def child_tail(self):
        return self._child_tail


    @property
    def child_failure(self):
        return self._child_failure


    @property
    def is_leaf_node(self):
        return self._child_head is None and self._child_tail is None and self._child_failure is None


    def new_child_head(self, parent_node):
        if self._child_head is not None:
            raise ValueError("child_head を増やすには、 child_head が None である必要があります")

        self._child_head = TreeNodeOfFaceOfCoin(face_of_coin=HEAD, parent_node=parent_node)
        return self._child_head


    def new_child_tail(self, parent_node):
        if self._child_tail is not None:
            raise ValueError("child_tail を増やすには、 child_tail が None である必要があります")

        self._child_tail = TreeNodeOfFaceOfCoin(face_of_coin=TAIL, parent_node=parent_node)
        return self._child_tail


    def new_child_failure(self, parent_node):
        if self._child_failure is not None:
            raise ValueError("child_failure を増やすには、 child_failure が None である必要があります")

        self._child_failure = TreeNodeOfFaceOfCoin(face_of_coin=EMPTY, parent_node=parent_node)
        return self._child_failure


    # def delete_child_head(self):
    #     if self._child_head is None:
    #         raise ValueError("child_head がなければ、 child_head を削除できません")
    #     self._child_head = None


    # def delete_child_tail(self):
    #     if self._child_tail is None:
    #         raise ValueError("child_tail がなければ、 child_tail を削除できません")
    #     self._child_tail = None


    # def delete_child_failure(self):
    #     if self._child_failure is None:
    #         raise ValueError("child_failure がなければ、 child_failure を削除できません")
    #     self._child_failure = None


    def create_path_of_face_of_coin(self):

        if self.face_of_coin is None:
            raise ValueError("ルートノードが create_path_of_face_of_coin メソッドを呼び出さないでください")

        path_of_face_of_coin = []

        cur_node = self

        while cur_node is not None:
            # ルート・ノードはナンが入ってる
            if cur_node.face_of_coin is None:
                #print("ルート・ノードはナンが入ってる")
                break

            #print(f"{cur_node.face_of_coin=}")
            path_of_face_of_coin.append(cur_node.face_of_coin)

            cur_node = cur_node.parent_node

        path_of_face_of_coin.reverse()

        if len(path_of_face_of_coin) < 1:
            raise ValueError(f"要素を持たない経路があるのはおかしい {len(path_of_face_of_coin)=}")

        return path_of_face_of_coin


########################
# MARK: TreeOfFaceOfCoin
########################
class TreeOfFaceOfCoin():
    """コインの出目のツリー構造"""


    def __init__(self):
        self._root_node = TreeNodeOfFaceOfCoin(face_of_coin=None, parent_node=None)
        self._current_node = self._root_node


    def go_to_new_child_head(self):
        child_head = self._current_node.new_child_head(parent_node=self._current_node)
        self._current_node = child_head


    def go_to_new_child_tail(self):
        child_tail = self._current_node.new_child_tail(parent_node=self._current_node)
        self._current_node = child_tail


    def go_to_new_child_failure(self):
        child_failure = self._current_node.new_child_failure(parent_node=self._current_node)
        self._current_node = child_failure


    def back_to_parent_node(self):
        parent_node = self._current_node.parent_node

        if parent_node is None:
            raise ValueError("親要素がないので、親には戻れません")

        # if self._current_node.face_of_coin == HEAD:
        #     parent_node.delete_child_head()

        # elif self._current_node.face_of_coin == TAIL:
        #     parent_node.delete_child_tail()

        # elif self._current_node.face_of_coin == EMPTY:
        #     parent_node.delete_child_failure()
        
        # else:
        #     raise ValueError(f"{self._current_node.face_of_coin=}")

        self._current_node = parent_node


    def search_for_each_node(self, cur_node, on_each_leaf_node, timeout):


        if timeout.is_expired('recursive search for each node'):
            return


        if cur_node.is_leaf_node:
            on_each_leaf_node(cur_node)
            return


        child_count = 0

        if cur_node.child_head is not None:
            self.search_for_each_node(cur_node=cur_node.child_head, on_each_leaf_node=on_each_leaf_node, timeout=timeout)

            if timeout.is_expired('cur_node.child_head is not None'):
                return

            child_count += 1


        if cur_node.child_tail is not None:
            self.search_for_each_node(cur_node=cur_node.child_tail, on_each_leaf_node=on_each_leaf_node, timeout=timeout)

            if timeout.is_expired('cur_node.child_tail is not None'):
                return

            child_count += 1


        if cur_node.child_failure is not None:
            self.search_for_each_node(cur_node=cur_node.child_failure, on_each_leaf_node=on_each_leaf_node, timeout=timeout)

            if timeout.is_expired('cur_node.child_failure is not None'):
                return

            child_count += 1


        if child_count < 0:
            raise ValueError(f"葉ノードでないのなら、子は必ずあるはずです {child_count=}")


        return


    def for_each_node(self, on_each_leaf_node, timeout):
        self.search_for_each_node(cur_node=self._root_node, on_each_leaf_node=on_each_leaf_node, timeout=timeout)


    def create_list_of_path_of_face_of_coin(self, timeout):


        def make_return_value(list_of_path):
            """戻り値の作成
            
            Parameters
            ----------
            list_of_path : list
                パスのリスト
            """
            return {'list_of_path':list_of_path}


        list_of_path = []

        def on_each_leaf_node(leaf_node):

            # ルートノードは、スコアボードに含まないのでスキップします
            if leaf_node.face_of_coin is None:
                #print("ルートノードは、スコアボードに含まないのでスキップします")
                return

            path_of_face_of_coin = leaf_node.create_path_of_face_of_coin()

            if len(path_of_face_of_coin) < 1:
                raise ValueError(f"長さが０の経路があるのはおかしい {len(path_of_face_of_coin)=}")

            list_of_path.append(path_of_face_of_coin)


        self.for_each_node(on_each_leaf_node=on_each_leaf_node, timeout=timeout)


        if timeout.is_expired('create_list_of_path_of_face_of_coin'):
            return make_return_value(list_of_path=None)


        if len(list_of_path) < 1:
            raise ValueError(f"経路の長さが０コインなのはおかしい {len(list_of_path)=}")


        return make_return_value(list_of_path=list_of_path)


#############################
# MARK: AllPatternsFaceOfCoin
#############################
class AllPatternsFaceOfCoin():
    """［コインの表］、［コインの裏］、［コインの表でも裏でもないもの］の印の組み合わせが全て入っているリスト"""


    def __init__(self, can_failure, series_rule):
        """初期化

        Parameters
        ----------
        can_failure : bool
            ［表も裏も出なかった事象］の有無
        series_rule : SeriesRule
            ［シリーズ・ルール］
        """
        self._can_failure = can_failure
        self._series_rule = series_rule
        self._tree_of_face_of_coin = None


    def __search(self, depth, timeout):


        if depth < 1:
            return


        # 表勝ちを追加
        self._tree_of_face_of_coin.go_to_new_child_head()            
        self.__search(depth=depth - 1, timeout=timeout)


        if timeout.is_expired('TreeOfFaceOfCoin#__search head win'):
            return


        # 親へ戻る
        self._tree_of_face_of_coin.back_to_parent_node()


        # 裏勝ちを追加
        self._tree_of_face_of_coin.go_to_new_child_tail()
        self.__search(depth=depth - 1, timeout=timeout)


        if timeout.is_expired('TreeOfFaceOfCoin#__search tail win'):
            return


        # 親へ戻る
        self._tree_of_face_of_coin.back_to_parent_node()


        if self._can_failure:
            # 引分けを追加
            self._tree_of_face_of_coin.go_to_new_child_failure()
            self.__search(depth=depth - 1, timeout=timeout)


            if timeout.is_expired('TreeOfFaceOfCoin#__search draw'):
                return


            # 親へ戻る
            self._tree_of_face_of_coin.back_to_parent_node()


        return


    def make_tree_of_all_pattern_face_of_coin(self, timeout):
        """１シリーズについて、フル対局分の、全パターンのコイントスの結果を作りたい
        
        １コインは　勝ち、負けの２つ、または　勝ち、負け、引き分けの３つ。

        Parameters
        ----------
        timeout : Timeout
            タイムアウト

        Returns
        -------
        tree_of_face_of_coin : TreeOfFaceOfCoin
            勝った方の色（引き分け含む）のリストが全パターン入っているリスト
        """


        def make_return_value(tree_of_face_of_coin):
            """戻り値の作成
            
            Parameters
            ----------
            tree_of_face_of_coin : TreeOfFaceOfCoin
                
            """
            return {'tree_of_face_of_coin':tree_of_face_of_coin}


        # 要素数
        if self._can_failure:
            # 表勝ち、裏勝ち、勝者なしの３要素
            elements = [HEAD, TAIL, EMPTY]

        else:
            # 表勝ち、裏勝ちけの２要素
            elements = [HEAD, TAIL]

        # 桁数
        depth = self._series_rule.upper_limit_coins


        # FIXME リスト状だと MemoryError になるので、木構造にしたい
        self._tree_of_face_of_coin = TreeOfFaceOfCoin()

        self.__search(depth=depth, timeout=timeout)


        if timeout.is_expired('make_tree_of_all_pattern_face_of_coin'):
            return make_return_value(tree_of_face_of_coin=None)


        return make_return_value(tree_of_face_of_coin=self._tree_of_face_of_coin)


########################
# MARK: PointCalculation
########################
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
    def get_successful_player(elementary_event, time_th, turn_system_id):

        # ［先後交互制］
        if turn_system_id == ALTERNATING_TURN:
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
        if turn_system_id == FROZEN_TURN:
            if elementary_event == HEAD:
                return ALICE

            if elementary_event == TAIL:
                return BOB

            # 表も裏も出なかった
            if elementary_event == EMPTY:
                return EMPTY

            raise ValueError(f"{elementary_event=}")


        raise ValueError(f"{turn_system_id=}")


    def get_gameover_reason(self):
        """TODO 終局している場合、その理由を記述した文字列を返す。終局していなければナン
        
        NOTE ［先後交互制］では、表番が達成でも勝利条件ではないことに注意すること。［先後固定制］にしろ、［先後交互制］にしろ、プレイヤーの勝ち負けを見ればよい
        """

        a_fully_won = self._series_rule.step_table.span <= self._pts_list[ALICE]
        b_fully_won = self._series_rule.step_table.span <= self._pts_list[BOB]

        # 両者が同時に達成を取っているケースはおかしい
        if a_fully_won and b_fully_won:
            raise ValueError(f"両者が同時に達成を取っているケースはおかしい  {a_fully_won=}  {b_fully_won=}")

        # Ａさんが達成
        if a_fully_won:
            return 'a_fully_won'

        # Ｂさんが達成
        if b_fully_won:
            return 'b_fully_won'

        # 終局していない
        return None


    def append_point_when_won(self, successful_face_of_coin, time_th, path_of_face_of_coin):
        """加点

        Parameters
        ----------
        successful_face_of_coin : int
            ［コインの表か裏］
        path_of_face_of_coin : list
            ［検証用］
        """

        successful_player = PointCalculation.get_successful_player(successful_face_of_coin, time_th, self._spec.turn_system_id)

        # ［勝ち点］
        step = self._series_rule.step_table.get_step_by(face_of_coin=successful_face_of_coin)


        # 検証用
        old_pts_list = list(self._pts_list)

        self._pts_list[successful_player] += step


        # 検証
        if self._series_rule.step_table.span <= self._pts_list[ALICE] and self._series_rule.step_table.span <= self._pts_list[BOB]:
            print(f"""\
PointCalculation
----------------
self.stringify_dump:
{self.stringify_dump(INDENT)}
{old_pts_list=}
""")

            raise ValueError(f"ＡさんとＢさんがどちらも達成勝ちしている、これはおかしい  {self._pts_list[ALICE]=}  {self._pts_list[BOB]=}")


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


def assert_path_of_face_of_coin(path_of_face_of_coin):
    """［コインの表］、［コインの裏］、［コインの表と裏のどちらでもない］のいずれかしか含んでいないはずです"""
    for mark in path_of_face_of_coin:
        if mark not in [HEAD, TAIL, EMPTY]:
            raise ValueError(f"予期しない値がリストに入っています  {mark=}")


def judge_series(spec, series_rule, path_of_face_of_coin):
    """［コインの表］、［コインの裏］、［コインの表と裏のどちらでもない］の３つの内のいずれかを印をつけ、
    その印が並んだものを、１シリーズ分の疑似対局結果として読み取ります

    Parameters
    ----------
    spec : Specification
        仕様
    series_rule : int
        ［シリーズ・ルール］
    path_of_face_of_coin : list
        コイントスした結果のリスト。引き分け含む
    """

    # 検証
    if len(path_of_face_of_coin) < series_rule.shortest_coins:
        text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
        print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
        raise ValueError(text)

    # 検証
    if series_rule.upper_limit_coins < len(path_of_face_of_coin):
        text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、上限対局数の理論値 {series_rule.upper_limit_coins} を上回っています。このような対局シートを指定してはいけません"
        print(f"""{text}
{path_of_face_of_coin=}
{series_rule.shortest_coins=}
""")
        raise ValueError(text)


    # 検証
    #assert_path_of_face_of_coin(path_of_face_of_coin=path_of_face_of_coin)


    # ［勝ち点計算］
    point_calculation = PointCalculation(
            spec=spec,
            series_rule=series_rule)


    # ［このシリーズで引き分けた対局数］
    failed_coins = 0

    time_th = 0

    # ［勝ち点差判定］や［タイブレーク］など、決着が付かなかったときの処理は含みません
    # もし、引き分けがあれば、［引き分けを１局として数えるケース］です。
    # 予め作った１シリーズ分の対局結果を読んでいく
    for face_of_coin in path_of_face_of_coin:

        # ［上限対局数］に達していたら、コイン投げを終了します
        if series_rule.upper_limit_coins <= time_th:
            break


        time_th += 1

        # 引き分けを１局と数えるケース
        #
        #   NOTE シリーズの中で引分けが１回でも起こると、（点数が足らず）シリーズ全体も引き分けになる確率が上がるので、後段で何かしらの対応をします
        #
        if face_of_coin == EMPTY:
            failed_coins += 1
        
        else:
            
            # 検証
            gameover_reason = point_calculation.get_gameover_reason()
            if gameover_reason is not None:
                raise ValueError(f"終局後に加点してはいけません1  {gameover_reason=}")

            # 勝ち点の加点
            point_calculation.append_point_when_won(
                    successful_face_of_coin=face_of_coin,
                    time_th=time_th,
                    path_of_face_of_coin=path_of_face_of_coin[0:time_th])

            # 終局
            gameover_reason = point_calculation.get_gameover_reason()
            if gameover_reason is not None:

                # コイントスの結果のリストの長さを切ります。
                # 対局は必ずしも［上限対局数］になるわけではありません
                path_of_face_of_coin = SequenceOfFaceOfCoin.cut_down(path_of_face_of_coin, time_th)

                break


    # 検証
    if len(path_of_face_of_coin) != time_th:
        raise ValueError(f"テープの長さがおかしい2 {len(path_of_face_of_coin)=}  {time_th=}  {point_calculation.get_gameover_reason()=}")

    # 検証
    if time_th < series_rule.shortest_coins:
        text = f"{spec.p=} 対局数の実際値 {time_th} が最短対局数の理論値 {series_rule.shortest_coins} を下回った2  {point_calculation.get_gameover_reason()=}"
        print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
        raise ValueError(text)

    # 検証
    if series_rule.upper_limit_coins < time_th:
        text = f"{spec.p=} 対局数の実際値 {time_th} が上限対局数の理論値 {series_rule.upper_limit_coins} を上回った2  {point_calculation.get_gameover_reason()=}"
        print(f"""{text}
{path_of_face_of_coin=}
{series_rule.shortest_coins=}
""")
        raise ValueError(text)


    # FIXME カットダウン後のテープと、引き分けの数を確認
    failed_coins_2 = 0
    for face_of_coin_2 in path_of_face_of_coin:
        if face_of_coin_2 == EMPTY:
            failed_coins_2 += 1
    if failed_coins != failed_coins_2:
        raise ValueError(f"検算で、引き分けの数が一致しません {failed_coins=}  {failed_coins_2=}  {path_of_face_of_coin=}  {point_calculation.get_gameover_reason()=}")


    return TrialResultsForOneSeries(
            spec=spec,
            series_rule=series_rule,
            failed_coins=failed_coins,
            point_calculation=point_calculation,
            path_of_face_of_coin=path_of_face_of_coin)


def calculate_probability(p, H, T):
    """［表側を持っているプレイヤー］が勝つ確率を返します

    TODO オーバーフロー例外に対応したプログラミングをすること

    NOTE ＡさんとＢさんは、表、裏を入れ替えて持つことがあるので、［表側を持っているプレイヤー］が必ずＡさんとは限らない

    ［表側を持っているプレイヤー］が勝つ条件：　表が H 回出る前に裏が T 回出ないこと
    試行回数の考え方：　ゲームは最小で H 回、最大で N = H + T - 1 回のコイン投げで終了します
    確率の計算：　総試行回数 N 回で、表が H 回以上出る確率を計算します

    # パラメータの設定例
    p = 0.7  # 表が出る確率
    H = 7    # ［表側を持っているプレイヤー］が必要な表の回数
    T = 3    # ［裏側を持っているプレイヤー］が必要な裏の回数

    # 計算の実行例
    probability, err = calculate_probability(p, H, T)
    if err is not None:
        pass # エラー時対応

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
    err : str
        エラーが有ればメッセージを、無ければナンを返す
    """

    from math import comb

    try:

        err = None

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

            # この累乗で、浮動小数点数が大きすぎてオーバーフロー例外を投げることがある
            prob = combinations * (p ** n) * (q ** (N - n))

            probability += prob

        return probability, err
    
    except OverflowError as ex:
        err = f"{ex}"
        return UPPER_OUT_OF_P, err


##################
# MARK: SeriesRule
##################
class SeriesRule():
    """［シリーズ・ルール］
    
    NOTE ［最短対局数］、［上限対局数］は指定できず、計算で求めるもの
    """


    class StepTable():
        """［１勝の点数テーブル］"""


        @staticmethod
        def let_t_time(span, t_step):
            """t_time の計算方法は、 span / t_step ※小数点切り上げ"""
            return math.ceil(span / t_step)


        @staticmethod
        def let_h_time(span, h_step):
            """h_time の計算方法は、 span / h_step ※小数点切り上げ"""
            return math.ceil(span / h_step)


        @staticmethod
        def let_t_step_divisible_by_h_step(t_step, h_step, h_time):
            # 割り切れないなら 0
            if t_step % h_step != 0 or t_step // h_step >= h_time:
                return 0
            

            # 割り切れるなら、割る数
            return t_step // h_step

        
        def __init__(self, h_step, t_step, span):
            """初期化
            
            Parameters
            ----------
            h_step : int
                ［表番で勝ったときの勝ち点］
            t_step : int
                ［裏番で勝ったときの勝ち点］
            span : int
                ［目標の点数］
            """

            self._step_list = [
                    # 0: ［未使用］
                    None,
                    # 1: ［表番で勝ったときの勝ち点］
                    h_step,
                    # 2: ［裏番で勝ったときの勝ち点］
                    t_step]

            self._span = span


        @property
        def span(self):
            """［目標の点数］"""
            return self._span


        def get_step_by(self, face_of_coin):
            """［表番または裏番で勝ったときの勝ち点］を取得します
            
            Parameters
            ----------
            face_of_coin : int
                ［コインの表か裏かそれ以外］
            """

            # ［コインの表が出たときの勝ち点］
            if face_of_coin == HEAD:
                return self._step_list[1]

            # ［コインの裏が出たときの勝ち点］
            if face_of_coin == TAIL:
                return self._step_list[2]

            raise ValueError(f"{face_of_coin=}")


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
                    return round_letro(math.ceil(self._span / self.get_step_by(face_of_coin=HEAD)))

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
                    return round_letro(math.ceil(self._span / self.get_step_by(face_of_coin=TAIL)))

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
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


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


        step_table = SeriesRule.StepTable(
                h_step=h_step,
                t_step=t_step,
                span=span)


        # ［最短対局数］
        shortest_coins = SeriesRule.let_shortest_coins(
                h_step=h_step,
                t_step=t_step,
                span=span,
                turn_system_id=spec.turn_system_id)

        # ［上限対局数］
        upper_limit_coins = SeriesRule.let_upper_limit_coins(
                spec=spec,
                h_time=step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                t_time=step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))


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
step_table:
{step_table.stringify_dump('   ')}
""")
            raise ValueError(text)


        return SeriesRule(
                spec=spec,
                step_table=step_table,
                shortest_coins=shortest_coins,          # ［最短対局数］
                upper_limit_coins=upper_limit_coins)    # ［上限対局数］


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


    @property
    def spec(self):
        """［仕様］"""
        return self._spec


    @property
    def step_table(self):
        return self._step_table


    @property
    def shortest_coins(self):
        """［最短対局数］"""
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        """［上限対局数］"""
        return self._upper_limit_coins


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
        """［上限対局数］を算出します

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
        elif spec.turn_system_id == ALTERNATING_TURN:
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


        else:
            raise ValueError(f"{spec.turn_system_id=}")


    @staticmethod
    def let_upper_limit_coins_with_failure_rate(spec, upper_limit_coins_without_failure_rate):
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
        return math.ceil(upper_limit_coins_without_failure_rate / (1 - spec.failure_rate))


    @staticmethod
    def let_upper_limit_coins(spec, h_time, t_time):
        """［上限対局数］を算出します

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        upper_limit_coins_without_failure_rate = SeriesRule.let_upper_limit_coins_without_failure_rate(
                spec=spec,
                h_time=h_time,
                t_time=t_time)

        return SeriesRule.let_upper_limit_coins_with_failure_rate(
                spec=spec,
                upper_limit_coins_without_failure_rate=upper_limit_coins_without_failure_rate)


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


################################
# MARK: TrialResultsForOneSeries
################################
class TrialResultsForOneSeries():
    """［シリーズ］１つ分の試行結果"""


    def __init__(self, spec, series_rule, failed_coins, point_calculation, path_of_face_of_coin):
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
        path_of_face_of_coin : list

        """

        # 共通
        self._spec = spec
        self._failed_coins = failed_coins
        self._series_rule = series_rule
        self._point_calculation = point_calculation
        self._path_of_face_of_coin = path_of_face_of_coin


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
    def number_of_coins(self):
        """行われた対局数"""
        return len(self._path_of_face_of_coin)


    @property
    def failed_coins(self):
        """［表も裏も出なかった対局数］"""
        return self._failed_coins


    @property
    def path_of_face_of_coin(self):
        """"""
        return self._path_of_face_of_coin


    def is_pts_won(self, winner):
        """winner の［勝ち点］は［目標の点数］に達していないが、 loser の［勝ち点］より多くて winner さんの勝ち
        
        FIXME Points Won というのは、シリーズ中に引き分けの対局が１つ以上あって、かつ、相手より点数が多く、かつ、自分が［目標の点数］に達していない状態
        """
        loser = Converter.opponent(winner)
        return 0 < self.failed_coins and not self._point_calculation.is_fully_won(player=winner) and self._point_calculation.x_has_more_than_y(winner, loser)


    def is_won(self, winner):
        """FIXME このシリーズで winner が loser に勝ったか？"""

        loser = Converter.opponent(winner)

        # 両者が達成勝ちしている、これはおかしい
        if self._point_calculation.is_fully_won(winner) and self._point_calculation.is_fully_won(loser):
            print(f"""\
TrialResultsForOneSeries
------------------------
self._point_calculation.stringify_dump:
{self._point_calculation.stringify_dump(INDENT)}
{self._path_of_face_of_coin=}
""")

            raise ValueError(f"両者が達成勝ちしている、これはおかしい {winner=}  {loser=}  {self.point_calculation.is_fully_won(winner)=}  {self.point_calculation.is_fully_won(loser)=}  {self._series_rule.step_table.span=}")

        # 両者が判定勝ちしている、これはおかしい
        if self.is_pts_won(winner=winner) and self.is_pts_won(winner=loser):
            print(f"""\
TrialResultsForOneSeries
------------------------
self._point_calculation.stringify_dump:
{self._point_calculation.stringify_dump(INDENT)}
{self._path_of_face_of_coin=}
""")
            raise ValueError(f"両者が判定勝ちしている、これはおかしい {winner=}  {loser=}  {self.is_pts_won(winner=winner)=}  {self.is_pts_won(winner=loser)=}  {self._series_rule.step_table.span=}")

        # 達成勝ちなら確定、判定勝ちでもOK 
        return self.point_calculation.is_fully_won(winner) or self.is_pts_won(winner=winner)


    def is_no_win_match(self):
        """TODO 勝者なし。どちらも勝者でないとき"""
        return not self.is_won(ALICE) and not self.is_won(BOB)


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}TrialResultsForOneSeries
{indent}------------------------
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)}
{succ_indent}{self.number_of_coins=}
{succ_indent}{self._failed_coins=}
{succ_indent}self._series_rule.stringify_dump(succ_indent):
{self._series_rule.stringify_dump(succ_indent)=}
{succ_indent}self._point_calculation:
{self._point_calculation.stringify_dump(succ_indent)}
{succ_indent}{self._path_of_face_of_coin=}
{succ_indent}{self.is_pts_won(winner=ALICE)=}
{succ_indent}{self.is_pts_won(winner=BOB)=}
{succ_indent}{self.is_won(winner=ALICE)=}
{succ_indent}{self.is_won(winner=BOB)=}
{succ_indent}{self.is_no_win_match()}
"""
    

###############################
# MARK: LargeSeriesTrialSummary
###############################
class LargeSeriesTrialSummary():
    """［大量のシリーズを試行した結果］"""


    def __init__(self, specified_trial_series, list_of_trial_results_for_one_series):
        """初期化
        
        Parameters
        ----------
        specified_trial_series : int
            ［シリーズ試行回数］
        list_of_trial_results_for_one_series : list
            ［シリーズ］の結果のリスト
        """

        self._specified_trial_series = specified_trial_series
        self._list_of_trial_results_for_one_series = list_of_trial_results_for_one_series
        self._series_shortest_coins = None
        self._series_longest_coins = None
        self._successful_series = None
        self._failed_series = None

        # （Fully wins）［達成勝ち］数。二次元配列[challenged][PLAYERS]
        self._ful_wins = [
            # 未使用
            None,
            # ［引き分けが起こらなかったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
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
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
        ]

        # ［勝者がなかった回数］。ＡさんとＢさんについて。初期値は None
        self._no_wins = None


    @property
    def specified_trial_series(self):
        """シリーズ試行回数"""
        return self._specified_trial_series


    # 共通
    # ----

    @property
    def total(self):
        """シリーズ数"""

        # 検証
        # ----

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
    def series_shortest_coins(self):
        """［シリーズ最短対局数］"""
        if self._series_shortest_coins is None:
            self._series_shortest_coins = 2_147_483_647
            for s in self._list_of_trial_results_for_one_series:
                if s.number_of_coins < self._series_shortest_coins:
                    self._series_shortest_coins = s.number_of_coins

        return self._series_shortest_coins


    @property
    def series_longest_coins(self):
        """［シリーズ最長対局数］"""
        if self._series_longest_coins is None:
            self._series_longest_coins = 0
            for s in self._list_of_trial_results_for_one_series:
                if self._series_longest_coins < s.number_of_coins:
                    self._series_longest_coins = s.number_of_coins

        return self._series_longest_coins


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
    def number_of_no_win_match_series(self):
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


    def trial_no_win_match_series_rate(self):
        """試行した結果、［勝敗付かず］で終わったシリーズの割合"""
        return self.number_of_no_win_match_series / self.total


    def wins(self, challenged, winner):
        """winner が loser に勝った数"""
        return self.ful_wins(challenged=challenged, winner=winner) + self.pts_wins(challenged=challenged, winner=winner)


    @property
    def no_wins(self):
        """勝者がなかった回数"""
        if self._no_wins is None:
            self._no_wins = 0
            for s in self._list_of_trial_results_for_one_series:
                if s.is_no_win_match():
                    self._no_wins += 1

        return self._no_wins


#################
# MARK: Candidate
#################
class Candidate():
    """［シリーズ・ルール候補］"""


    def __init__(self, p_error, trial_series, h_step, t_step, span, shortest_coins, upper_limit_coins):

        if not isinstance(trial_series, int):
            raise ValueError(f"［試行シリーズ数］は int 型である必要があります {trial_series=}")

        if not isinstance(h_step, int):
            raise ValueError(f"［表番で勝ったときの勝ち点］は int 型である必要があります {h_step=}")

        if not isinstance(t_step, int):
            raise ValueError(f"［裏番で勝ったときの勝ち点］は int 型である必要があります {t_step=}")

        if not isinstance(span, int):
            raise ValueError(f"［目標の点数］は int 型である必要があります {span=}")

        if not isinstance(shortest_coins, int):
            raise ValueError(f"［最短対局数］は int 型である必要があります {shortest_coins=}")

        if not isinstance(upper_limit_coins, int):
            raise ValueError(f"［上限対局数］は int 型である必要があります {upper_limit_coins=}")

        self._p_error = p_error
        self._trial_series = trial_series
        self._h_step = h_step
        self._t_step = t_step
        self._span = span
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


    @property
    def p_error(self):
        return self._p_error


    @property
    def trial_series(self):
        return self._trial_series


    @property
    def h_step(self):
        return self._h_step


    @property
    def t_step(self):
        return self._t_step


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
        return f'[{self._p_error:.6f} {self._h_step}表 {self._t_step}裏 {self._span}目 {self._shortest_coins}～{self._upper_limit_coins}局 {self._trial_series}試]'


    _re_pattern_of_candidate = None

    @classmethod
    def parse_candidate(clazz, candidate):

        if clazz._re_pattern_of_candidate is None:
            clazz._re_pattern_of_candidate = re.compile(r'([0-9.-]+) (\d+)表 (\d+)裏 (\d+)目 (\d+)～(\d+)局 (\d+)試')

        result = _re_pattern_of_candidate.match(candidate)
        if result:
            return Candidate(
                    p_error=float(result.group(1)),
                    trial_series=float(result.group(7)),
                    h_step=int(result.group(2)),
                    t_step=int(result.group(3)),
                    span=int(result.group(4)),
                    shortest_coins=int(result.group(5)),
                    upper_limit_coins=int(result.group(6)))

        raise ValueError(f"パースできません {candidate=}")


##################
# MARK: ScoreBoard
##################
class ScoreBoard():
    """１シリーズ分の経過の記録。
    以下の表のようなものを作る。CSVで出力する

    ［先後固定制］
    -------------

        Specification
        p        failure_rate  turn_system_name
        70.0000  10.0000       frozen

        Series Rule
        h_step  t_step  span
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
        p        failure_rate  turn_system_name
        70.0000  10.0000       alternating

        Series Rule
        h_step  t_step  span
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


    def __init__(self, pattern_no, pattern_p, spec, series_rule, path_of_face_of_coin, game_results, round_list):
        """初期化

        Parameters
        ----------
        pattern_no : int
            パターン通し番号
        pattern_p : int
            このパターンが選ばれる確率
        spec : Specification
            ［仕様］
        series_rule : SeriesRule
            ［シリーズ・ルール］
        path_of_face_of_coin : list
            コイントスした結果のリスト。引き分け含む
        game_results : int
            対局結果
        round_list : list
            対局過程
        """

        if pattern_p <= 0:
            raise ValueError(f"選ばれる確率のない経路があるのはおかしい。 {pattern_p=}")

        self._pattern_no = pattern_no
        self._pattern_p = pattern_p
        self._spec = spec
        self._series_rule = series_rule
        self._path_of_face_of_coin = path_of_face_of_coin
        self._game_results = game_results
        self._round_list = round_list


    @staticmethod
    def make_score_board(pattern_no, spec, series_rule, path_of_face_of_coin):

        # 入力値チェック
        # いったん、［表が出る確率］、［裏が出る確率］、［表も裏も出なかった確率］を足して１００％になるような数にします
        #
        #   NOTE 自明の計算式だが、float 型でピッタリ 1 にならないケースがあることに注意しておく必要がある
        #
        p_with_draw = (1 - spec.failure_rate) * spec.p
        q_with_draw = (1 - spec.failure_rate) * (1 - spec.p)
        sum_rate = p_with_draw + q_with_draw + spec.failure_rate
        # ぴったり 1 にはならない。有効桁数を決めておく
        if not Precision.is_almost_one(sum_rate):
            raise ValueError(f"［ほぼ］ではなく合計はピッタリ 1 になるはずですが、コンピューターの都合でピッタリ 1 になりません。それにしても大きく外れています {sum_rate=}({p_with_draw=}  {q_with_draw=}  {spec.failure_rate=})")

        pattern_p = 1
        for face_of_coin in path_of_face_of_coin:
            if face_of_coin == HEAD:
                pattern_p *= p_with_draw
            elif face_of_coin == TAIL:
                pattern_p *= q_with_draw
            elif face_of_coin == EMPTY:
                pattern_p *= spec.failure_rate
            else:
                raise ValueError(f"{face_of_coin}")


        span = series_rule.step_table.span
        h_step = series_rule.step_table.get_step_by(face_of_coin=HEAD)
        t_step = series_rule.step_table.get_step_by(face_of_coin=TAIL)

        a_point = span
        b_point = span

        round_list = []
        round_list.append(['S', '', '', a_point, b_point])

        for round_th, face_of_coin in enumerate(path_of_face_of_coin, 1):
            # 最後のラウンドについて
            last_round = round_list[-1]

            # 表番がどちらか？
            #
            # ［先後固定制］では表番はずっとＡさん
            if spec.turn_system_id == FROZEN_TURN:
                head_player = 'A'

            # ［先後交互制］では、表番は１局ごとに入れ替えます
            elif spec.turn_system_id == ALTERNATING_TURN:
                if last_round[1] in ['', 'B']:
                    head_player = 'A'
                else:
                    head_player = 'B'
            
            else:
                raise ValueError(f"{spec.turn_system_id=}")


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
            

            round_list.append([round_th, head_player, Converter.face_of_coin_to_str(face_of_coin), a_point, b_point])


        last_round = round_list[-1]
        last_a_count_down_point = int(last_round[3])
        last_b_count_down_point = int(last_round[4])

        # 対局不成立
        if last_a_count_down_point <= 0 and last_b_count_down_point <= 0:
            raise ValueError(f"両者が達成はおかしい {round_list=}  {spec.p=}  {spec.failure_rate=}  turn_system_id={Converter.turn_system_id_to_name(spec.turn_system_id)}  {span=}  {t_step=}  {h_step=}")
        
        # 達成で,Ａさんの勝ち
        elif last_a_count_down_point <= 0:
            game_results = ALICE_FULLY_WON

        # 達成で,Ｂさんの勝ち
        elif last_b_count_down_point <= 0:
            game_results = BOB_FULLY_WON

        # 勝ち点差で,Ａさんの勝ち
        elif last_a_count_down_point < last_b_count_down_point:
            game_results = ALICE_POINTS_WON

        # 勝ち点差で,Ｂさんの勝ち
        elif last_b_count_down_point < last_a_count_down_point:
            game_results = BOB_POINTS_WON
        
        # 勝者なし
        else:
            game_results = NO_WIN_MATCH


        return ScoreBoard(
                pattern_no=pattern_no,
                pattern_p=pattern_p,
                spec=spec,
                series_rule=series_rule,
                path_of_face_of_coin=path_of_face_of_coin,
                game_results=game_results,
                round_list=round_list)


    @property
    def pattern_no(self):
        """［パターン通し番号］"""
        return self._pattern_no


    @property
    def pattern_p(self):
        """［このパターンが選ばれる確率］"""
        return self._pattern_p


    @property
    def spec(self):
        """［仕様］"""
        return self._spec
    

    @property
    def series_rule(self):
        """［シリーズ・ルール］"""
        return self._series_rule


    @property
    def path_of_face_of_coin(self):
        """コイントスした結果のリスト。引き分け含む"""
        return self._path_of_face_of_coin


    @property
    def game_results(self):
        """対局結果"""
        return self._game_results


    @property
    def round_list(self):
        """対局過程"""
        return self._round_list


    def stringify_dump(self, indent):
        """ダンプ"""
        succ_indent = indent + INDENT
        return f"""\
{indent}ElementaryEventSequence
{indent}-----------------------
{succ_indent}self._spec:
{self._spec.stringify_dump(succ_indent)}
{succ_indent}{self._upper_limit_coins=}
{succ_indent}{self._path_of_face_of_coin=}
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


def try_series(spec, series_rule, specified_trial_series):
    """シリーズをシミュレーションします
    
    Returns
    -------
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーション結果
    """
    list_of_trial_results_for_one_series = []

    # シミュレーション
    for round in range(0, specified_trial_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                spec=spec,
                upper_limit_coins=series_rule.upper_limit_coins)

        # 検証
        if len(path_of_face_of_coin) < series_rule.shortest_coins:
            text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
            print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
            raise ValueError(text)


        # ［シリーズ］１つ分の試行結果を返す
        trial_results_for_one_series = judge_series(
                spec=spec,
                series_rule=series_rule,
                path_of_face_of_coin=path_of_face_of_coin)
        #print(f"{trial_results_for_one_series.stringify_dump()}")

        
#         if trial_results_for_one_series.number_of_coins < series_rule.shortest_coins:
#             text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.shortest_coins} を下回った"
#             print(f"""{text}
# {path_of_face_of_coin=}
# {series_rule.upper_limit_coins=}
# {trial_results_for_one_series.stringify_dump('   ')}
# """)
#             raise ValueError(text)

#         if series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
#             text = f"{spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.upper_limit_coins} を上回った"
#             print(f"""{text}
# {path_of_face_of_coin=}
# {series_rule.shortest_coins=}
# {trial_results_for_one_series.stringify_dump('   ')}
# """)
#             raise ValueError(text)


        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    # ［大量のシリーズを試行した結果］
    large_series_trial_summary = LargeSeriesTrialSummary(
            specified_trial_series=specified_trial_series,
            list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)

    return large_series_trial_summary


######################
# MARK: RenamingBackup
######################
class RenamingBackup():
    """ファイルのリネーム・バックアップ
    
    拡張子に .bak を追加する。これは WinMerge のバックアップと同じ拡張子
    """


    def __init__(self, file_path):
        self._file_path = file_path


    @property
    def backup_file_path(self):
        directory_path, file_base = os.path.split(self._file_path)
        return f'{directory_path}/{file_base}.bak'


    def rollback_if_file_crushed(self):
        """対象のファイルを読み込む前に呼び出してください"""

        if os.path.isfile(self.backup_file_path):
            seconds = random.randint(30, 15*60)
            print(f"バックアップ・ファイルが存在しています。対象のファイルは保存中か、保存に失敗している可能性があります。 {seconds} 秒待ってから復元を試みます backup=`{self.backup_file_path}`")
            time.sleep(seconds)

            self._rollback()


    def make_backup(self):
        """既存のバックアップ・ファイルがあれば削除し、既存のファイルのバックアップ・ファイルを作成する"""

        # バックアップ・ファイルが既存ということは、問題が発生しているのでは？
        if os.path.isfile(self.backup_file_path):
            raise ValueError(f"バックアップ・ファイルが既存のまま、バックアップ・ファイルを作成しようとしたので、対象ファイルが破損したまま作業を行った可能性があります。ファイルを確認してください file={self.backup_file_path}")

        # 対象のファイルが存在しなければ、バックアップは作成しません
        if not os.path.isfile(self._file_path):
            return

        new_path = shutil.copy2(
            self._file_path,
            self.backup_file_path)    # 第２引数にファイル名を指定すると、既存なら上書きになる


    def remove_backup(self):
        """バックアップ・ファイルを削除する"""

        # バックアップ・ファイルが存在しなければ、無視します
        if not os.path.isfile(self.backup_file_path):
            return

        s = self.backup_file_path
        # 安全用
        if not s.endswith(".bak"):
            raise ValueError(f"バックアップ・ファイル以外のものを削除しようとしました name={s}")
        os.remove(s)


    def _rollback(self):
        """既存のファイルを削除し、バックアップ・ファイルを正のファイルにリネームする"""
        print(f"[{datetime.datetime.now()}] copy `{self.backup_file_path}` to `{self._file_path}`")

        if not os.path.isfile(self.backup_file_path):
            raise ValueError(f'ロールバックしようとしましたが、指定されたバックアップファイルが見つかりません。保存中でバックアップファイルが削除されたタイミングかもしれません {self.backup_file_path=}')

        try:
            new_path = shutil.copy2(
                self.backup_file_path,
                self._file_path)    # 第２引数にファイル名を指定すると、既存なら上書きになる

        # FIXME FileNotFoundError: [WinError 2] 指定されたファイルが見つかりません。
        except FileNotFoundError as e:
            print(f"""\
{self.backup_file_path=}
{self._file_path=}
""")
            raise


@staticmethod
def get_list_of_basename(dir_path):
    """GT のファイル名一覧取得
    
    📖 [ファイル名のみの一覧を取得](https://note.nkmk.me/python-listdir-isfile-isdir/#_1)
    """
    basename_list = [
        f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
    ]
    #print(basename_list)

    return basename_list
