#
# python o2o0_play_fair_coin_toss.py
#
#   フェアコイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, FROZEN_TURN, Specification
from library_for_game import GamePlan, Paragraphs


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

            game_plan = GamePlan(
                    spec=Specification.by_three_rates(
                            turn_system_id=FROZEN_TURN,
                            failure_rate=0.0,
                            head_rate=0.5),
                    h_step=1,
                    t_step=1,
                    span=1,
                    a_victory_rate=0.5,
                    b_victory_rate=0.5,
                    no_victory_rate=0.0)

            # 先住民が持っているコインは、～確率うんぬん～ フェア？コインだ
            Paragraphs.coins_that_people_had(msg_spd=msg_spd, game_plan=game_plan)

            print()
            print(f"「表とｳﾗ、どっちが出る方に張る？」")
            time.sleep(msg_spd)

            while True:
                prompt = f"""\

表に張るなら h を、ｳﾗに張るなら t を入力してください
> """
                input_str = input(prompt)

                if input_str in ['h', 't']:
                    break

            if input_str == 'h':
                your_choice = HEAD

                print()
                print(f"「じゃあ　表で」")
                time.sleep(msg_spd)
            
            else:
                your_choice = TAIL

                print()
                print(f"「じゃあ　ｳﾗで」")
                time.sleep(msg_spd)

            print()
            print(f"ピンッ")
            time.sleep(msg_spd / 3)
            print(f"バシッ")
            time.sleep(msg_spd)


            # 0.0 <= X < 1.0
            outcome = random.random()


            if outcome < 0.5:
                face_of_coin = HEAD
                face_of_coin_str = '表'

                print()
                print(f"「{face_of_coin_str}が出た」")
                time.sleep(msg_spd)

            else:
                face_of_coin = TAIL
                face_of_coin_str = 'ｳﾗ'    # 表と裏の字が似すぎているので、変えてみる

                print()
                print(f"　{face_of_coin_str}が出た」")
                time.sleep(msg_spd)


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
