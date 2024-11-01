#
# python o2o5o0_play_unfair_coin_toss.py
#
#   アンフェアコイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, FROZEN_TURN, Converter, Specification
from library_for_game import GamePlan, Paragraphs, choice_game_plan
from library_for_game.data import exactly_unfair_list_of_game_plan


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
            game_plan = choice_game_plan(exactly_unfair_list_of_game_plan)

            # 例：　先住民が持っているコインは、～確率うんぬん～ フェア？コインだ
            Paragraphs.coins_that_people_had(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　「表とｳﾗ、どっちが出る方に張る？」「じゃあ　ｳﾗで」
            your_choice = Paragraphs.do_you_choice_head_or_tail(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　ピンッ　バシッ　「表が出た」
            face_of_coin = Paragraphs.toss_a_coin(msg_spd=msg_spd, game_plan=game_plan)


            if your_choice == face_of_coin:
                print()
                print(f"「やったぜ！　当たった！」")
                time.sleep(msg_spd)

            else:
                print()
                print(f"「ハズレかあ」")
                time.sleep(msg_spd)


            print()
            print(f"こうして、コイントスは終わった。")
            time.sleep(msg_spd)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
