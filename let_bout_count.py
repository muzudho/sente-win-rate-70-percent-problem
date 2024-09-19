# 対局数を算出
# python let_bout_count.py

import traceback
import datetime
import math

from library import PointsConfiguration


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for span in range(1,101):
            for b_step in range(1, span):
                for w_step in range(1, b_step):
                    points_configuration = PointsConfiguration(
                        b_step=b_step,
                        w_step=w_step,
                        span_when_frozen_turn=span)

                    # 対局数
                    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
                    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()
                    seg_3c = points_configuration.let_number_of_shortest_bout_when_alternating_turn()
                    seg_3d = points_configuration.let_number_of_longest_bout_when_alternating_turn()

                    seg_4a = b_step
                    seg_4b = w_step
                    seg_4c = span
                    print(f"対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交代制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
