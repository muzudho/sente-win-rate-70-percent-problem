# 対局数を算出
# python let_count_time.py

import traceback
import datetime
import math

from library import PointsConfiguration

LOG_FILE_PATH = 'output/let_count_time.log'


# ［将棋の引分け率］
FAILURE_RATE = 0.0


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［目標の点数］
        for span in range(1,101):
            # ［裏勝ち１つの点数］
            for q_step in range(1, span):
                # ［表勝ち１つの点数］
                for p_step in range(1, q_step):
                    pts_conf_ft = PointsConfiguration(
                            failure_rate=FAILURE_RATE,
                            turn_system=WHEN_FROZEN_TURN,
                            p_step=p_step,
                            q_step=q_step,
                            span=span)

                    pts_conf_at = PointsConfiguration(
                            failure_rate=FAILURE_RATE,
                            turn_system=WHEN_ALTERNATING_TURN,
                            p_step=p_step,
                            q_step=q_step,
                            span=span)

                    # ［最短対局数］［最長対局数］
                    seg_3a = pts_conf_ft.number_of_shortest_time()
                    seg_3b = pts_conf_ft.number_of_longest_time()
                    seg_3c = pts_conf_at.number_of_shortest_time()
                    seg_3d = pts_conf_at.number_of_longest_time()

                    seg_4a = p_step
                    seg_4b = q_step
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
