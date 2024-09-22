import datetime
import re

from library import PointsConfiguration


def parse_process_element(process_element):
    result = re.match(r'([0-9.-]+) (\d+)黒 (\d+)白 (\d+)目 (\d+)～(\d+)局', process_element)
    if result:
        p_error = float(result.group(1))
        black = int(result.group(2))
        white = int(result.group(3))
        span = int(result.group(4))
        shortest = int(result.group(5))
        longest = int(result.group(6))

        return p_error, black, white, span, shortest, longest

    return None, None, None, None, None, None


def stringify_report_muzudho_recommends_points_at(p, number_of_series, latest_theoretical_p, specified_points_configuration, presentable, process):
    """［先後交互制］での、むずでょが推奨する［かくきんシステムのｐの構成］

    Parameters
    ----------
    presentable : str
        表示用の説明文
    """

    # ［表が出る確率（％）］
    seg_1 = p * 100

    # 表示用の説明文
    if isinstance(presentable, str):    # float NaN が入っていることがある
        seg_10 = f"    {presentable}"
    else:
        seg_10 = ''

    # NOTE ［先後交互制］では、理論値を出すのが難しいので、理論値ではなく、実際値を出力する
    #
    # ［計算過程］
    process_list = process[1:-1].split('] [')
    for process_element in process_list:
        p_error, b_step, w_step, span, shortest, longest = parse_process_element(process_element)
        if p_error is not None:
            if b_step == specified_points_configuration.b_step and w_step == specified_points_configuration.w_step and span == specified_points_configuration.span:

                # ［調整後の表が出る確率（％）］
                seg_2 = p_error*100+50

                # 誤差（％）
                seg_3 = p_error*100

                # ［黒勝ち１つの点数］
                seg_4 = b_step

                # ［白勝ち１つの点数］
                seg_5 = w_step

                # ［目標の点数］
                seg_6 = span

                # ［先後交互制］での［最短対局数］
                seg_7 = shortest

                # ［先後交互制］での［最長対局数］
                seg_8 = longest

                # ［試行回数］
                seg_9 = number_of_series

                return f"先手勝率 {seg_1:2.0f} ％ --試行後--> {seg_2:7.4f} ％（{seg_3:+8.4f}）   先手勝ち{seg_4:>3}点、後手勝ち{seg_5:>3}点、目標{seg_6:>3}点    {seg_7:>3}～{seg_8:>3}局（先後交互制）    試行{seg_9}回{seg_10}"


    return f"先手勝率 {seg_1:2.0f} ％ --試行後--> （該当なし）{seg_10}"


def stringify_report_muzudho_recommends_points_ft(p, latest_theoretical_p, specified_points_configuration, presentable, process):
    """［先後固定制］での、むずでょが推奨する［かくきんシステムのｐの構成］

    Parameters
    ----------
    presentable : str
        表示用の説明文
    """

    # ［表が出る確率（％）］
    seg_1 = p * 100

    # ［調整後の表が出る確率（％）］    NOTE ［先後固定制］では、理論値が出せるので、実際値ではなく、理論値を出力する
    seg_2 = latest_theoretical_p * 100

    # 誤差（％）
    seg_3 = (latest_theoretical_p - 0.5) * 100

    # ［黒勝ち１つの点数］
    seg_4 = specified_points_configuration.b_step

    # ［白勝ち１つの点数］
    seg_5 = specified_points_configuration.w_step

    # ［目標の点数］
    seg_6 = specified_points_configuration.span

    # ［先後交互制］での［最短対局数］
    seg_7 = specified_points_configuration.count_shortest_time_when_alternating_turn()

    # ［先後交互制］での［最長対局数］
    seg_8 = specified_points_configuration.count_longest_time_when_alternating_turn()

    # 表示用の説明文
    if isinstance(presentable, str):    # float NaN が入っていることがある
        seg_9 = f"    {presentable}"
    else:
        seg_9 = ''

    return f"先手勝率 {seg_1:2.0f} ％ --理論値--> {seg_2:7.4f} ％（{seg_3:+8.4f}）   先手勝ち{seg_4:>3}点、後手勝ち{seg_5:>3}点、目標{seg_6:>3}点    {seg_7:>3}～{seg_8:>3}局（先後固定制）{seg_9}"


# def stringify_when_report_evenizing_system(p, specified_p, specified_p_error, points_configuration):
#     """文言の作成"""

#     # ［かくきんシステムのｐの構成］
#     points_configuration = PointsConfiguration.let_points_from_repeat(
#             b_time=b_time,
#             w_time=w_time)

#     # ［表が出る確率（％）］
#     seg_1 = p*100

#     # ［調整後の表が出る確率（％）］
#     seg_2 = specified_p*100

#     # ［調整後の表が出る確率（％）と 0.5 との誤差］
#     seg_2b = specified_p_error*100

#     # 対局数
#     seg_3a = points_configuration.count_shortest_time_when_frozen_turn()
#     seg_3b = points_configuration.count_longest_time_when_frozen_turn()
#     seg_3c = points_configuration.count_shortest_time_when_alternating_turn()
#     seg_3d = points_configuration.count_longest_time_when_alternating_turn()

#     # ［白勝ち１つの点数］
#     seg_4a = points_configuration.b_step

#     # ［黒勝ち１つの点数］
#     seg_4b = points_configuration.w_step

#     # ［目標の点数］
#     seg_4c = points_configuration.span

#     text = ""
#     #text += f"[{datetime.datetime.now()}]  " # タイムスタンプ
#     text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_2:6.4f} ％ （± {seg_2b:>7.4f}）    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点"
#     return text


def stringify_when_let_calculate_probability(p, b_time, w_time, best_p, best_p_error):
    """文言の作成"""

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p

    # ［黒勝ちだけでの対局数］
    seg_2 = b_time

    # ［白勝ちだけでの対局数］
    seg_3 = w_time

    # # 計算過程を追加する場合
    # text += f"  {''.join(process_list)}"

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {best_p_error:7.4f}）    先後固定制での回数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def stringify_when_generate_b_w_time_strict(p, best_p, best_p_error, points_configuration, process_list):

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error*100

    # 対局数
    seg_3a = points_configuration.count_shortest_time_when_frozen_turn()
    seg_3b = points_configuration.count_longest_time_when_frozen_turn()
    seg_3c = points_configuration.count_shortest_time_when_alternating_turn()
    seg_3d = points_configuration.count_longest_time_when_alternating_turn()

    # ［黒勝ち１つの点数］
    seg_4a = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = points_configuration.w_step

    # ［目標の点数］
    seg_4c = points_configuration.span

    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {seg_1c:>7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
    return text


def print_when_generate_even_when_alternating_turn(p, best_p, best_p_error, best_number_of_series, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error * 100

    # 対局数
    seg_3a = points_configuration.count_shortest_time_when_frozen_turn()
    seg_3b = points_configuration.count_longest_time_when_frozen_turn()
    seg_3c = points_configuration.count_shortest_time_when_alternating_turn()
    seg_3d = points_configuration.count_longest_time_when_alternating_turn()

    # ［黒勝ち１つの点数］
    seg_4a = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = points_configuration.w_step

    # ［目標の点数］
    seg_4c = points_configuration.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{best_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def print_when_generate_when_frozen_turn(p, specified_p, specified_p_error, specified_number_of_series, specified_points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = specified_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = specified_p_error * 100

    # 対局数
    seg_3a = specified_points_configuration.count_shortest_time_when_frozen_turn()
    seg_3b = specified_points_configuration.count_longest_time_when_frozen_turn()
    seg_3c = specified_points_configuration.count_shortest_time_when_alternating_turn()
    seg_3d = specified_points_configuration.count_longest_time_when_alternating_turn()

    # ［黒勝ち１つの点数］
    seg_4a = specified_points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = specified_points_configuration.w_step

    # ［目標の点数］
    seg_4c = specified_points_configuration.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{specified_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def stringify_simulation_log(
        p, draw_rate, points_configuration, simulation_result, title):
    """シミュレーションのログの文言作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    draw_rate : float
        ［引き分ける確率］
    points_configuration : PointsConfiguration
        ［かくきんシステムのｐの構成］
    simulation_result : SimulationResult
        シミュレーションの結果
    title : str
        タイトル
    """

    # ヘッダー
    # --------
    time1 = datetime.datetime.now() # ［タイムスタンプ］
    ti1 = title                     # タイトル

    # ［将棋の先手勝率］
    # -----------------
    shw1 = p * 100                                                             # ［将棋の先手勝率（％）］指定値
    shw2 = simulation_result.trial_black_win_rate_without_draw * 100           # ［将棋の先手勝率（％）］実践値
    shw2e = simulation_result.trial_black_win_rate_error_without_draw * 100    # ［将棋の先手勝率（％）と 0.5 との誤差］実践値

    # ［Ａさんの勝率］
    # ---------------
    aw1 = simulation_result.trial_alice_win_rate_without_draw * 100           # ［Ａさんが勝つ確率（％）］実践値
    aw1e = simulation_result.trial_alice_win_rate_error_without_draw * 100    # ［Ａさんが勝つ確率（％）と 0.5 との誤差］実践値

    # 将棋の引分け
    # ------------
    d1 = draw_rate * 100
    d2 = simulation_result.trial_draw_rate_ft * 100
    d2e = d2 - d1

    # 引分け率
    # --------
    d1 = draw_rate * 100    # ［将棋の引分け率］指定値
    d2 = (simulation_result.number_of_draw_series_ft / simulation_result.number_of_series) * 100     # ［将棋の引分け率］実践値

    # 対局数
    # ------
    tm10 = points_configuration.count_shortest_time_when_frozen_turn()  # ［最短対局数］理論値
    tm11 = points_configuration.count_longest_time_when_frozen_turn()   # ［最長対局数］
    tm20 = simulation_result.shortest_time_th    # ［最短対局数］実践値
    tm21 = simulation_result.longest_time_th     # ［最長対局数］

    # シリーズ数
    # ---------
    sr0 = simulation_result.number_of_series             # 全
    sr1 = simulation_result.number_of_black_fully_wons   # 先手勝ち
    sr2 = simulation_result.number_of_black_points_wons  # 先手判定勝ち（引分けがなければ零です）

    # 勝ち点構成
    # ---------
    pt1 = points_configuration.b_step    # ［黒勝ち１つの点数］
    pt2 = points_configuration.w_step    # ［白勝ち１つの点数］
    pt3 = points_configuration.span      # ［目標の点数］


    return f"""\
[{time1                   }] {ti1}
                                    将棋の先手勝ち  将棋の引分け  Ａさんの勝ち     シリーズ         対局数      | 勝ち点設定
                              指定   |   {shw1:2.0f} ％                        {d1:2.0f} ％          {sr0:>7}全      {tm10:>2}～{tm11:>2} 局    | {pt1:3.0f}黒
                              試行後 |  {   shw2:8.4f} ％    {d2       :8.4f} ％   {aw1:8.4f} ％     {      sr1:>7}先満勝  {tm20:>2}～{tm21:>2} 局    | {pt2:3.0f}白
                                      （ {shw2e:7.4f}）   （ {d2e   :7.4f}）  （ {aw1e:7.4f}）      {    sr2:>7}先判勝               | {pt3:3.0f}目
"""


# TODO 廃止予定
def stringify_log_when_simulation_series_with_draw_when_frozen_turn(
        p, draw_rate, points_configuration, simulation_result, title):
    """［先後固定制］で［引き分けを１局として数えるケース］での［シリーズ］での結果の文言を作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    draw_rate : float
        ［引き分ける確率］
    points_configuration : PointsConfiguration
        ［かくきんシステムのｐの構成］
    simulation_result : SimulationResult
        シミュレーションの結果
    title : str
        タイトル
    """

    # 引分け率（％） 実際値
    seg_7b = (simulation_result.number_of_draw_series_ft / simulation_result.number_of_series) * 100

    # ［勝ち点差黒勝率（％）］
    if simulation_result.number_of_black_points_wons == 0:
        seg_8 = "なし"
    else:
        seg_8 = f"{(simulation_result.number_of_black_points_wons / simulation_result.number_of_black_points_wons) * 100:8.4f} ％"

    # 引分けシリーズ数
    seg_10 = simulation_result.number_of_draw_series_ft

    # 黒勝ち数
    seg_11 = simulation_result.number_of_black_all_wons

    return f"""\
  引分け率        対局数（先後固定制）
       先手勝ち数{seg_11:>7}，引分{seg_10:>7}（詳細{simulation_result.number_of_draw_times:>7}），
        {                seg_7b     :8.4f} ％   勝ち点差黒勝率 {seg_8}

"""
