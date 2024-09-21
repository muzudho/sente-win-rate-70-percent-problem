# 対局数を算出
# python let_count_time.py

import traceback
import datetime
import math

from library import PointsConfiguration

LOG_FILE_PATH = 'output/let_count_time.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［目標の点数］
        for span in range(1,101):
            # ［白勝ち１つの点数］
            for w_step in range(1, span):
                # ［黒勝ち１つの点数］
                for b_step in range(1, w_step):
                    points_configuration = PointsConfiguration(
                            b_step=b_step,
                            w_step=w_step,
                            span=span)

                    # ［最短対局数］［最長対局数］
                    seg_3a = points_configuration.count_shortest_time_when_frozen_turn()
                    seg_3b = points_configuration.count_longest_time_when_frozen_turn()
                    seg_3c = points_configuration.count_shortest_time_when_alternating_turn()
                    seg_3d = points_configuration.count_longest_time_when_alternating_turn()

                    seg_4a = b_step
                    seg_4b = w_step
                    seg_4c = span

                    text = f"対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
                    print(text)

                    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                        f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise