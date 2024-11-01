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
from library_for_game.data import fair_list_of_game_plan


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        #msg_spd = 2
        msg_spd = 0.02

        # プロローグ
        print()
        print(f"きふわらべ王国の国民は言った。")
        time.sleep(msg_spd)

        print()
        print(f"「コイントスしようぜ？」")
        time.sleep(msg_spd)


        for demo_th in range(1, 2): # ループ無し

            # ゲーム企画
            game_plan = choice_game_plan(fair_list_of_game_plan)

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

            # 数学大臣「ちなみに、先手が勝つ確率は　～うんぬん～　だったんだぜ」
            Paragraphs.spoilers_from_the_minister_of_mathematics(msg_spd=msg_spd, game_plan=game_plan)


            print()
            print(f"こうして、コイントスは終わった。")
            time.sleep(msg_spd)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
