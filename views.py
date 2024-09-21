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


def stringify_report_muzudho_recommends_points_at(p, round_count, latest_theoretical_p, specified_points_configuration, presentable, process):
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
                seg_9 = round_count

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
    seg_7 = specified_points_configuration.let_number_of_shortest_bout_when_alternating_turn()

    # ［先後交互制］での［最長対局数］
    seg_8 = specified_points_configuration.let_number_of_longest_bout_when_alternating_turn()

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
#     seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
#     seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()
#     seg_3c = points_configuration.let_number_of_shortest_bout_when_alternating_turn()
#     seg_3d = points_configuration.let_number_of_longest_bout_when_alternating_turn()

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
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()
    seg_3c = points_configuration.let_number_of_shortest_bout_when_alternating_turn()
    seg_3d = points_configuration.let_number_of_longest_bout_when_alternating_turn()

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


def print_when_generate_even_when_alternating_turn(p, best_p, best_p_error, best_round_count, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error * 100

    # 対局数
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()
    seg_3c = points_configuration.let_number_of_shortest_bout_when_alternating_turn()
    seg_3d = points_configuration.let_number_of_longest_bout_when_alternating_turn()

    # ［黒勝ち１つの点数］
    seg_4a = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = points_configuration.w_step

    # ［目標の点数］
    seg_4c = points_configuration.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{best_round_count:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def print_when_generate_when_frozen_turn(p, specified_p, specified_p_error, specified_round_count, specified_points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = specified_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = specified_p_error * 100

    # 対局数
    seg_3a = specified_points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = specified_points_configuration.let_number_of_longest_bout_when_frozen_turn()
    seg_3c = specified_points_configuration.let_number_of_shortest_bout_when_alternating_turn()
    seg_3d = specified_points_configuration.let_number_of_longest_bout_when_alternating_turn()

    # ［黒勝ち１つの点数］
    seg_4a = specified_points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = specified_points_configuration.w_step

    # ［目標の点数］
    seg_4c = specified_points_configuration.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{specified_round_count:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def stringify_log_when_simulation_coin_toss_when_alternating_turn(p, alice_won_rate, specified_p_error, b_time, round_total):

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1a = p*100

    # Ａさんが勝った確率
    seg_2 = alice_won_rate*100

    # 誤差
    seg_2b = specified_p_error*100

    # # ｎ本勝負
    # seg_3 = b_time

    # 対局試行
    seg_4 = round_total

    return f"[{seg_0}]  先手勝率 {seg_1a:2.0f} ％ --調整--> {seg_2:8.4f} ％（± {seg_2b:7.4f}）（先後交互制でＡさんが勝った確率）  コイントス{seg_4:7}回試行"


def stringify_log_when_simulation_coin_toss_when_frozen_turn(output_file_path, p, round_total,
        black_wons, expected_shortest_bout_th_when_frozen_turn, actual_shortest_bout_th_when_frozen_turn, expected_longest_bout_th_when_frozen_turn, actual_longest_bout_th_when_frozen_turn,
        points_configuration, comment):
    """ログ出力
    
    Parameters
    ----------
    output_file_path : str
        出力先ファイルへのパス
    p : float
        ［表が出る確率］（先手勝率）
    round_total : int
        対局数
    black_wons : int
        ［先後固定制］で、黒が勝った回数
    expected_shortest_bout_th_when_frozen_turn : int

    actual_shortest_bout_th_when_frozen_turn : int

    expected_longest_bout_th_when_frozen_turn : int

    actual_longest_bout_th_when_frozen_turn : int

    points_configuration : PointsConfiguration
        ［かくきんシステムのｐの構成］
    comment : str
        コメント
    """

    # ［最長対局数（先後固定制）］
    #
    #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
    #

    # ［先後固定制］で、黒の勝率
    specified_p_when_frozen_turn = black_wons / round_total

    # ［先後固定制］で、黒の勝率と、五分五分との誤差
    specified_p_error_when_frozen_turn = abs(specified_p_when_frozen_turn - 0.5)

    # ［タイムスタンプ］
    seg_0a = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_0b = p*100

    # ［調整後の表が出る確率（％）］
    seg_1_1a = specified_p_when_frozen_turn*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1_1b = specified_p_error_when_frozen_turn*100

    # 対局数（理論値と実際値）
    seg_1_3a = expected_shortest_bout_th_when_frozen_turn
    seg_1_3b = expected_longest_bout_th_when_frozen_turn
    seg_2_3a = actual_shortest_bout_th_when_frozen_turn
    seg_2_3b = actual_longest_bout_th_when_frozen_turn


    # ［黒勝ち１つの点数］
    seg_4a = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = points_configuration.w_step

    # ［目標の点数］
    seg_4c = points_configuration.span

    # コメント
    seg_5 = comment

    return f"""\
[{seg_0a                  }]  先手勝率 {seg_0b:2.0f} ％ --試行後--> {seg_1_1a:8.4f} ％（± {seg_1_1b:7.4f}）    先手勝ち数{black_wons:7}／{round_total:7}対局試行    対局数 {seg_1_3a:>2}～{seg_1_3b:>2}  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点    {seg_5}
                                                                                                                       実際   {seg_2_3a:>2}～{seg_2_3b:>2} 局（先後固定制）
"""
