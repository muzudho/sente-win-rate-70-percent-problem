# 計算
# python let_leap_cycle.py
#
#   閏対局の周期の算出
#
#   NOTE 閏対局は没案。累積二項分布を使うのが正しい。
#   // 計算上、先手勝率７０％の場合、先手勝ち１点、後手勝ち２点ルールで行い、
#   // ３対局毎に１回は、先手勝ち１点、後手勝ち３点ルールを行う閏対局を入れると、先後勝率が均等になるはず
#

import traceback
import math
import pandas as pd

from library import round_letro, scale_for_float_to_int, p_to_b_q_times
from library.database import get_df_p


class LeapRoundCalculate():
    """閏対局計算"""


    def __init__(self, p, strict_p_time, strict_q_time, practical_p_time, practical_q_time):
        """初期化
        
        Parameters
        ----------
        p : float
            表が出る確率
        strict_p_time : int
            表が出る確率の厳密な整数比
        strict_q_time : int
            裏が出る確率の厳密な整数比
        practical_p_time : int
            表が出る確率の実用的な整数比
        practical_q_time : int
            裏が出る確率の実用的な整数比
        """

        self._p = p
        self._strict_p_time = strict_p_time
        self._strict_q_time = strict_q_time
        self._practical_p_time = practical_p_time
        self._practical_q_time = practical_q_time


    @property
    def p(self):
        """［表が出る確率］"""
        return self._p


    @property
    def strict_p_time(self):
        """表が出る確率の厳密な整数比"""
        return self._strict_p_time


    @property
    def strict_q_time(self):
        """裏が出る確率の厳密な整数比"""
        return self._strict_q_time


    @property
    def practical_p_time(self):
        """表が出る確率の実用的な整数比"""
        return self._practical_p_time


    @property
    def practical_q_time(self):
        """裏が出る確率の実用的な整数比"""
        return self._practical_q_time


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = get_df_p()

        # 先手勝率（表が出る確率）
        for p in df['p']:

            # 説明１　コインの表裏の確率
            # ------------------------

            print(f"先手勝率{p:4.2f}  ", end='')


            # 説明３　表のｎ本先取
            # -------------------

            # 厳密な値
            strict_p_time, strict_q_time = p_to_b_q_times(p=p)
            print(f"厳密な、先後固定制での回数  先手だけ：後手だけ＝{strict_p_time:>2}：{strict_q_time:>2}  ", end='')

            # 実用的な値（［裏勝ちだけでの対局数］が１になるよう丸めたもの）
            practical_p_time = round_letro(strict_p_time / strict_q_time) # 小数点以下四捨五入
            practical_q_time = 1
            print(f"実用的な、先後固定制での回数  先手だけ：後手だけ＝{practical_p_time:>2}：{practical_q_time:>2}  ", end='')


            # 説明４　表がまだ多めに出る得
            # --------------------------

            # 剰余（remainder）。繰り上がり先手勝率点
            strict_carried = strict_p_time % strict_q_time            
            print(f"割り切れない先手得{strict_carried:2}  ", end='')


            # 以下で行っているのは、余りの解消
            # -----------------------------
            #
            #   方法としては、足し算の筆算の繰り上がりと同じ。
            #   NOTE 余りを全て解消しても、また最初から繰り返しを行うこと
            #


            # 説明５　繰り上がり込みの表のポイント
            # ---------------------------------

            # 繰り上がり先手勝率点込みの先手勝率点
            carryover_strict_p_time = strict_p_time + strict_carried


            # 繰り上がりがある場合
            if strict_carried != 0:
                # 次の閏対局
                next_leap = 0

                print(f"先手得をチャラにするのに必要な次の閏対局", end='')

                # 余り解消の周期
                #
                #   NOTE もしかすると、繰り上がりが解消しないかもしれないから、循環時に打ち切るよう上限を付けておく
                #
                countdown = 100
                while strict_carried != 0 and 0 < countdown:

                    # ※繰り返し


                    # 説明６　あと何回対局すると、表の得が、裏が出る確率の整数比を上回るか
                    # ---------------------------------------------------------------

                    # あと何対局すると、余りが後手の整数比を上回るか（次の閏対局までの長さ）
                    fill_times = math.ceil(strict_q_time / strict_carried)
                    #print(f"\n  一対局毎に余りが{strict_carried}ずつ溜まり、{strict_q_time}以上になるのが、次の閏対局までの長さ{fill_times:2}")
                    print(f"(得{strict_carried:2}×{fill_times:2}局>=分子{strict_q_time:2})", end='')


                    if strict_carried != 0:
                        for i in range(0, 1):

                            # 次に余りを解消できる閏対局
                            next_leap += fill_times
                            #print(f"  次に余りを解消できる閏対局第{next_leap:2}")

                            # 次の繰り上がり先手勝率点
                            strict_carried = strict_p_time % strict_carried
                            #print(f"  次の繰り上がり先手勝率点{strict_carried}")
                            print(f"[第{next_leap:2}](新得{strict_carried:2}) ", end='')

                            if strict_carried == 0:
                                #print(f"  余り解消")
                                print(f"(繰り返し)", end='')
                                break

                            # 繰り上がり込み先手勝率点
                            carryover_strict_p_time = strict_p_time + strict_carried
                            #print(f"  繰り上がり込み先手勝率点{carryover_strict_p_time}")

                    countdown -= 1

            # 繰り上がりがある場合
            if strict_carried != 0:
                #print(f"  （計算未完了）", end='')
                print(f"(計算未完了)", end='')

            print() # 改行

            LeapRoundCalculate(
                    # 表が出る確率
                    p=p,
                    # 先手勝率の厳密な整数比
                    strict_p_time=strict_p_time,
                    # 後手勝率の厳密な整数比
                    strict_q_time=strict_q_time,
                    # 先手勝率の実用的な整数比
                    practical_p_time=practical_p_time,
                    # 後手勝率の実用的な整数比
                    practical_q_time=practical_q_time)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
