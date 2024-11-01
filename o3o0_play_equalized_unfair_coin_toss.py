#
# python o3o0_play_equalized_unfair_coin_toss.py
#
#   イコーライズド・アンフェア・コイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, FROZEN_TURN, Converter, Specification
from library_for_game import GamePlan, SeriesStatus, Paragraphs, choice_game_plan


list_of_game_plan = [
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.7),
            h_step=1,
            t_step=2,
            span=2,
            a_victory_rate=0.49,
            b_victory_rate=0.51,
            no_victory_rate=0.0)
]


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        #msg_spd = 2
        msg_spd = 0.02


        for demo_th in range(1, 2): # ループ無し

            # プロローグ
            print()
            print(f"きふわらべ王国の国民は言った。")
            time.sleep(msg_spd)

            print()
            print(f"「コイントスしようぜ？」")
            time.sleep(msg_spd)

            # ゲーム企画
            game_plan = choice_game_plan(list_of_game_plan)

            # 例：　先住民が持っているコインは、～確率うんぬん～ フェア？コインだ
            Paragraphs.coins_that_people_had(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　ここでコインを投げて、～うんぬん～　点先取した方が優勝とする
            Paragraphs.explain_series_rule(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　「表とｳﾗ、どっちが出る方に張る？」「じゃあ　ｳﾗで」
            your_choice = Paragraphs.do_you_choice_head_or_tail(msg_spd=msg_spd, game_plan=game_plan)

            # リセット
            series_status = SeriesStatus()

            for round_th in range(1, 100_000_001):

                print()
                print(f"国民「 {round_th} 投目」")
                time.sleep(msg_spd)

                # 例：　ピンッ　バシッ　「表が出た」
                face_of_coin = Paragraphs.toss_a_coin(msg_spd=msg_spd, game_plan=game_plan)

                # 例：　「やったぜ！　当たった！」　～うんぬん～　「優勝だな」
                victory_occurred = Paragraphs.open_face_of_coin(msg_spd=msg_spd, game_plan=game_plan, series_status=series_status, your_choice=your_choice, face_of_coin=face_of_coin)

                # どちらかが優勝したらループを抜ける
                if victory_occurred:
                    break


            # 優勝 or 敗退後
            # -------------

            print()
            print(f"こうして、コイントスは終わった。")
            time.sleep(msg_spd)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
