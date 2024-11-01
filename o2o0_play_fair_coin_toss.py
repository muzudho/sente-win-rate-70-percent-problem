#
# python o2o0_play_fair_coin_toss.py
#
#   フェアコイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, ALICE, BOB, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import JapaneseDemoFilePaths


DEMO_MONITOR_FILE_PATH = './logs/demo_japanese.log'


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        mspd = 2
        #mspd = 0.02


        for demo_th in range(1, 2): # ループ無し

            # プロローグ
            print()
            print(f"わらべ島の先住民は言った。")
            time.sleep(mspd)

            print()
            print(f"「コイントスしようぜ？」")
            time.sleep(mspd)

            print()
            print(f"先住民が持っているコインは、")
            time.sleep(mspd)

            print()
            print(f"投げて表が出る確率　５０％")
            time.sleep(mspd / 3)
            print(f"投げてｳﾗが出る確率　５０％")
            time.sleep(mspd / 3)
            print(f"投げて表もｳﾗも出ない確率　０％")
            time.sleep(mspd / 3)
            print(f"の、")
            time.sleep(mspd)

            print()
            print(f"フェアコインだ。")
            time.sleep(mspd)

            print()
            print(f"「表とｳﾗ、どっちが出る方に張る？」")
            time.sleep(mspd)

            while True:
                prompt = f"""\

表に貼るなら h を、ｳﾗに貼るなら t を入力してください
> """
                input_str = input(prompt)

                if input_str in ['h', 't']:
                    break

            if input_str == 'h':
                your_choice = HEAD

                print()
                print(f"「じゃあ　表で」")
                time.sleep(mspd)
            
            else:
                your_choice = TAIL

                print()
                print(f"「じゃあ　ｳﾗで」")
                time.sleep(mspd)

            print()
            print(f"ピンッ")
            time.sleep(mspd / 3)
            print(f"バシッ")
            time.sleep(mspd)


            # 0.0 <= X < 1.0
            outcome = random.random()


            if outcome < 0.5:
                face_of_coin = HEAD
                face_of_coin_str = '表'

                print()
                print(f"「{face_of_coin_str}が出た」")
                time.sleep(mspd)

            else:
                face_of_coin = TAIL
                face_of_coin_str = 'ｳﾗ'    # 表と裏の字が似すぎているので、変えてみる

                print()
                print(f"　{face_of_coin_str}が出た」")
                time.sleep(mspd)


            if your_choice == face_of_coin:
                print()
                print(f"「やったぜ！　当たった！」")
                time.sleep(mspd)

            else:
                print()
                print(f"「ハズレかあ」")
                time.sleep(mspd)


            print()
            print(f"こうして、コイントスは終わった。")
            time.sleep(mspd)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
