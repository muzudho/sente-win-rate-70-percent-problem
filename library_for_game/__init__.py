import time
import random
from library import HEAD, TAIL, Converter, Specification


def choice_game_plan(list_of_game_plan):
    return list_of_game_plan[random.randint(0, len(list_of_game_plan) - 1)]


class GamePlan():
    """ゲーム企画"""


    def __init__(self, spec, h_step, t_step, span, a_victory_rate, b_victory_rate, no_victory_rate):
        """初期化

        Parameters
        ----------
        p : float
            0.01 単位で 0 ～ 1 を想定
        """

        # ［仕様］
        self._spec = spec

        self._h_step = h_step
        self._t_step = t_step
        self._span = span
        self._a_victory_rate = a_victory_rate
        self._b_victory_rate = b_victory_rate
        self._no_victory_rate = no_victory_rate


    @property
    def spec(self):
        return self._spec


    @property
    def h_step(self):
        return self._h_step


    @property
    def t_step(self):
        return self._t_step


    @property
    def span(self):
        return self._span


    @property
    def a_victory_rate(self):
        return self._a_victory_rate


    @property
    def b_victory_rate(self):
        return self._b_victory_rate


    @property
    def no_victory_rate(self):
        return self._no_victory_rate


class SeriesStatus():


    def __init__(self):
        self._a_pts = 0
        self._b_pts = 0
        self._list_str_of_face_of_coin = ""


    @property
    def a_pts(self):
        """Ａさんの勝ち点の合計"""
        return self._a_pts


    @property
    def b_pts(self):
        return self._b_pts


    @property
    def list_str_of_face_of_coin(self):
        return self._list_str_of_face_of_coin


    def alice_won(self, face_of_coin, h_step):
        self._a_pts += h_step
        self._list_str_of_face_of_coin += Converter.face_of_coin_to_str(face_of_coin)


    def bob_won(self, face_of_coin, t_step):
        self._b_pts += t_step
        self._list_str_of_face_of_coin += Converter.face_of_coin_to_str(face_of_coin)


class Paragraphs():
    """各段落"""


    @staticmethod
    def coins_that_people_had(msg_spd, game_plan):
        """国民が持ってたコイン"""

        print()
        print(f"＜投げ場＞で国民が持っているコインは、")
        time.sleep(msg_spd)

        print()
        print(f"投げて表が出る確率 {game_plan.spec.p * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"投げてｳﾗが出る確率 {(1 - game_plan.spec.p) * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"投げて表もｳﾗも出ない確率 {game_plan.spec.failure_rate * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"の、")
        time.sleep(msg_spd)

        if game_plan.spec.p == 0.5:
            print()
            print(f"フェアコインだ。")
            time.sleep(msg_spd)

        else:
            print()
            print(f"アンフェアコインだ。")
            time.sleep(msg_spd)


    @staticmethod
    def explain_series_rule(msg_spd, game_plan):
        """［シリーズ・ルール］の解説"""

        print()
        print(f"ここで")
        time.sleep(msg_spd / 3)
        print(f"コインを投げて、")
        time.sleep(msg_spd)


        print()
        print(f"表が出たら、表に張った方に勝ち点が {game_plan.h_step} 、")
        time.sleep(msg_spd / 3)
        print(f"ｳﾗが出たら、ｳﾗに張った方に勝ち点が {game_plan.t_step} 、")
        # time.sleep(msg_spd / 3)
        # print(f"表も裏も出なかったら 0 点、")
        time.sleep(msg_spd)

        print()
        print(f"先に勝ち点を {game_plan.span} 取った方を優勝とする。")
        time.sleep(msg_spd / 3)


    @staticmethod
    def do_you_choice_head_or_tail(msg_spd, game_plan):

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
            print()
            print(f"「じゃあ　表で」")
            time.sleep(msg_spd)
            return HEAD
        
        print()
        print(f"「じゃあ　ｳﾗで」")
        time.sleep(msg_spd)
        return TAIL


    @staticmethod
    def toss_a_coin(msg_spd, game_plan):
        print()
        print(f"ピンッ")
        time.sleep(msg_spd / 3)
        print(f"バシッ")
        time.sleep(msg_spd)


        # 0.0 <= X < 1.0
        outcome = random.random()


        if outcome < game_plan.spec.p:
            face_of_coin = HEAD

            print()
            print(f"「{Converter.face_of_coin_to_str(face_of_coin)}が出た」")
            time.sleep(msg_spd)
            return face_of_coin


        face_of_coin = TAIL

        print()
        print(f"　{Converter.face_of_coin_to_str(face_of_coin)}が出た」")
        time.sleep(msg_spd)
        return face_of_coin


    @staticmethod
    def open_face_of_coin(msg_spd, game_plan, series_status, your_choice, face_of_coin):
        """
        Returns
        -------
        victory_occurred : bool
            どちらかが優勝したか？
        """
        if your_choice == face_of_coin:
            print()
            print(f"「やったぜ！　当たった！」")
            time.sleep(msg_spd)

            if your_choice == HEAD:
                series_status.alice_won(face_of_coin=face_of_coin, h_step=game_plan.h_step)

                print()
                print(f"「わたしが勝ち点 {game_plan.h_step} をもらって、")
                time.sleep(msg_spd / 3)
                print(f"　合計 {series_status.a_pts} 点だぜ。")
                time.sleep(msg_spd)

                if game_plan.span <= series_status.a_pts:
                    print()
                    print(f"　{game_plan.span} 点取ったから、")
                    time.sleep(msg_spd / 3)
                    print(f"　わたしの優勝だな」")
                    time.sleep(msg_spd)
                    return True


                print()
                print(f"　{game_plan.span} 点まで")
                time.sleep(msg_spd / 3)
                print(f"　まだ {game_plan.span - series_status.a_pts} 点足りないから、")
                time.sleep(msg_spd / 3)
                print(f"　続行だな」")
                time.sleep(msg_spd)


            elif your_choice == TAIL:
                series_status.bob_won(face_of_coin=face_of_coin, t_step=game_plan.t_step)

                print()
                print(f"「わたしが勝ち点 {game_plan.t_step} をもらって、")
                time.sleep(msg_spd / 3)
                print(f"　合計 {series_status.b_pts} 点だぜ。")
                time.sleep(msg_spd)

                if game_plan.span <= series_status.b_pts:
                    print()
                    print(f"　{game_plan.span} 点取ったから、")
                    time.sleep(msg_spd / 3)
                    print(f"　わたしの優勝だな」")
                    time.sleep(msg_spd)
                    return True


                print()
                print(f"　{game_plan.span} 点まで")
                time.sleep(msg_spd / 3)
                print(f"　まだ {game_plan.span - series_status.b_pts} 点足りないから、")
                time.sleep(msg_spd / 3)
                print(f"　続行だな」")
                time.sleep(msg_spd)


            else:
                raise ValueError(f"{your_choice=}")


        else:
            print()
            print(f"「ハズレかあ」")
            time.sleep(msg_spd)


            if your_choice == TAIL:
                series_status.alice_won(face_of_coin=face_of_coin, h_step=game_plan.h_step)

                print()
                print(f"「相手に勝ち点 {game_plan.h_step} が入って、")
                time.sleep(msg_spd / 3)
                print(f"　合計 {series_status.a_pts} 点だぜ。")
                time.sleep(msg_spd)

                if game_plan.span <= series_status.a_pts:
                    print()
                    print(f"　{game_plan.span} 点取られたから、")
                    time.sleep(msg_spd / 3)
                    print(f"　わたしの敗退だな」")
                    time.sleep(msg_spd)
                    return True


                print()
                print(f"　{game_plan.span} 点まで")
                time.sleep(msg_spd / 3)
                print(f"　まだ {game_plan.span - series_status.a_pts} 点足りないから、")
                time.sleep(msg_spd / 3)
                print(f"　続行だな」")
                time.sleep(msg_spd)


            elif your_choice == HEAD:
                series_status.bob_won(face_of_coin=face_of_coin, t_step=game_plan.t_step)

                print()
                print(f"「相手に勝ち点 {game_plan.t_step} が入って、")
                time.sleep(msg_spd / 3)
                print(f"　合計 {series_status.b_pts} 点だぜ。")
                time.sleep(msg_spd)

                if game_plan.span <= series_status.b_pts:
                    print()
                    print(f"　{game_plan.span} 点取られたから、")
                    time.sleep(msg_spd / 3)
                    print(f"　わたしの敗退だな」")
                    time.sleep(msg_spd)
                    return True


                print()
                print(f"　{game_plan.span} 点まで")
                time.sleep(msg_spd / 3)
                print(f"　まだ {game_plan.span - series_status.b_pts} 点足りないから、")
                time.sleep(msg_spd / 3)
                print(f"　続行だな」")
                time.sleep(msg_spd)


            else:
                raise ValueError(f"{your_choice=}")


    @staticmethod
    def spoilers_from_the_minister_of_mathematics(msg_spd, game_plan):
        """数学大臣によるネタバレ"""

        print()
        print(f"数学大臣「ちなみに、")
        time.sleep(msg_spd / 3)
        print(f"　先手が勝つ確率は、約 {game_plan.a_victory_rate * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"　後手が勝つ確率は、約 {game_plan.b_victory_rate * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"　だったんだぜ」")
        time.sleep(msg_spd)


    @staticmethod
    def announcer(msg_spd, game_plan, series_status, a_choice, a_name="王国兵", b_name="コクミン"):
        """アナウンサー"""

        if a_choice == HEAD:
            your_pts = series_status.a_pts
            your_step = game_plan.h_step
            opponent_pts = series_status.b_pts
            opponent_step = game_plan.t_step

        elif a_choice == TAIL:
            your_pts = series_status.b_pts
            your_step = game_plan.t_step
            opponent_pts = series_status.a_pts
            opponent_step = game_plan.h_step
        
        else:
            raise ValueError(f"{a_choice=}")


        if series_status.list_str_of_face_of_coin == "":
            print()
            print(f"アナウンサー「さあ　コイントスが始まりました！")
            time.sleep(msg_spd / 3)

        else:
            print()
            print(f"アナウンサー「今までのコイントスの結果は")
            time.sleep(msg_spd / 9)
            print(f"　　{series_status.list_str_of_face_of_coin}")
            time.sleep(msg_spd / 9)
            print(f"　　です！")
            time.sleep(msg_spd / 3)


        print()
        print(f"　{a_name}の勝ち点は {your_pts} 点")
        time.sleep(msg_spd / 9)
        print(f"　{b_name}の勝ち点は {opponent_pts} 点")
        time.sleep(msg_spd / 9)
        print(f"　優勝に必要な点は {game_plan.span} 点です！")
        time.sleep(msg_spd / 3)

        print()
        print(f"　{a_name}は {Converter.face_of_coin_to_str(a_choice)} に、")
        time.sleep(msg_spd / 9)
        print(f"　{b_name}は {Converter.face_of_coin_to_str(Converter.opponent(a_choice))} に張っています！")
        time.sleep(msg_spd / 3)

        print()
        print(f"　{Converter.face_of_coin_to_str(a_choice)}が出ると、{a_name}に {your_step} 点が、")
        time.sleep(msg_spd / 9)
        print(f"　{Converter.face_of_coin_to_str(Converter.opponent(a_choice))}が出ると、{b_name}に {opponent_step} 点が入ります！")
        time.sleep(msg_spd / 3)

        print()
        print(f"　しかし、表が出る確率は {game_plan.spec.p * 100:.1f} です！")
        time.sleep(msg_spd / 9)
        print(f"　さあ、どっちが出るか！？」")
        time.sleep(msg_spd / 3)
