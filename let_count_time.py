# 対局数を算出
# python let_count_time.py

import traceback
import datetime
import math

from library import SeriesRule

LOG_FILE_PATH = 'output/let_count_time.log'


PROBABILITY = 0.5

# ［将棋の引分け率］
FAILURE_RATE = 0.0


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1

        # ［目標の点数］
        for span in range(1,101):
            # ［裏勝ち１つの点数］
            for t_step in range(1, span):
                # ［表勝ち１つの点数］
                for h_step in range(1, t_step):

                    # ［先後固定制］
                    # 仕様
                    spec_ft = Specification(
                            p=PROBABILITY,
                            failure_rate=FAILURE_RATE,
                            turn_system_id=FROZEN_TURN)

                    series_rule_ft = SeriesRule.make_series_rule_base(
                            spec=spec_ft,
                            h_step=h_step,
                            t_step=t_step,
                            span=span)

                    # ［先後交互制］
                    # 仕様
                    spec_at = Specification(
                            p=PROBABILITY,
                            failure_rate=FAILURE_RATE,
                            turn_system_id=ALTERNATING_TURN)

                    series_rule_at = SeriesRule.make_series_rule_base(
                            spec=spec_at,
                            h_step=h_step,
                            t_step=t_step,
                            span=span)

                    # ［最短対局数］［上限対局数］
                    seg_3a = series_rule_ft.shortest_coins
                    seg_3b = series_rule_ft.upper_limit_coins
                    seg_3c = series_rule_at.shortest_coins
                    seg_3d = series_rule_at.upper_limit_coins

                    seg_4a = h_step
                    seg_4b = t_step
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
