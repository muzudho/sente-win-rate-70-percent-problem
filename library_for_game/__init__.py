import time
import random
from library import HEAD, TAIL, Specification


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


class Paragraphs():
    """各段落"""


    @staticmethod
    def coins_that_people_had(msg_spd, game_plan):
        """国民が持ってたコイン"""

        print()
        print(f"国民が持っているコインは、")
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
