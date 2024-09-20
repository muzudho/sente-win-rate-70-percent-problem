import datetime

from library import PointsConfiguration


def stringify_when_generate_takahashi_satoshi_system(p, best_new_p, best_new_p_error, best_b_time, best_w_time):
    """文言の作成"""

    # ［勝ち点ルール］の構成
    points_configuration = PointsConfiguration.let_points_from_repeat(
            b_time=best_b_time,
            w_time=best_w_time)

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_2 = best_new_p*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_2b = best_new_p_error*100

    # 対局数
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()
    seg_3c = points_configuration.let_number_of_shortest_bout_when_alternating_turn()
    seg_3d = points_configuration.let_number_of_longest_bout_when_alternating_turn()

    # ［白勝ち１つの点数］
    seg_4 = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_5 = points_configuration.w_step

    # ［目標の点数］
    seg_6 = points_configuration.span

    text = ""
    #text += f"[{datetime.datetime.now()}]  " # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_2:6.4f} ％ （± {seg_2b:>7.4f}）    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4:2.0f}点、後手勝ち{seg_5:2.0f}点　目標{seg_6:3.0f}点（先後固定制）"
    return text


def stringify_when_let_calculate_probability(p, b_time, w_time, new_p, new_p_error):
    """文言の作成"""

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = new_p

    # ［黒勝ちだけでの対局数］
    seg_2 = b_time

    # ［白勝ちだけでの対局数］
    seg_3 = w_time

    # # 計算過程を追加する場合
    # text += f"  {''.join(process_list)}"

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {new_p_error:7.4f}）    先後固定制での回数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def stringify_when_generate_b_w_time_strict(p, best_new_p, best_new_p_error, points_configuration, process_list):

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_new_p*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_new_p_error*100

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


def print_when_generate_even_when_alternating_turn(p, best_new_p, best_new_p_error, round_count, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_new_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_new_p_error * 100

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

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{round_count:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def print_when_generate_when_frozen_turn(p, best_new_p, best_new_p_error, round_count, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_new_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_new_p_error * 100

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

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{round_count:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def stringify_log_when_simulation_coin_toss_when_frozen_turn(output_file_path, p, round_total,
        black_wons, expected_shortest_bout_th_when_frozen_turn, actual_shortest_bout_th_when_frozen_turn, expected_longest_bout_th_when_frozen_turn, actual_longest_bout_th_when_frozen_turn,
        alice_wons, expected_shortest_bout_th_when_alternating_turn, actual_shortest_bout_th_when_alternating_turn, expected_longest_bout_th_when_alternating_turn, actual_longest_bout_th_when_alternating_turn,
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

    alice_wons : int
        ［先後交互制］で、Ａさんが勝った回数
    expected_shortest_bout_th_when_alternating_turn : int

    actual_shortest_bout_th_when_alternating_turn : int

    expected_longest_bout_th_when_alternating_turn : int

    actual_longest_bout_th_when_alternating_turn : int

    points_configuration : PointsConfiguration
        ［勝ち点ルール］の構成
    comment : str
        コメント
    """

    # ［最長対局数（先後固定制）］
    #
    #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
    #

    # ［先後固定制］で、黒の勝率
    new_p_when_frozen_turn = black_wons / round_total
    new_p_when_alternating_turn = alice_wons / round_total

    # ［先後固定制］で、黒の勝率と、五分五分との誤差
    new_p_error_when_frozen_turn = abs(new_p_when_frozen_turn - 0.5)
    new_p_error_when_alternating_turn = abs(new_p_when_alternating_turn - 0.5)

    # ［タイムスタンプ］
    seg_0a = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_0b = p*100

    # ［調整後の表が出る確率（％）］
    seg_1_1a = new_p_when_frozen_turn*100
    seg_2_1a = new_p_when_alternating_turn*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1_1b = new_p_error_when_frozen_turn*100
    seg_2_1b = new_p_error_when_alternating_turn*100

    # 対局数（理論値と実際値）
    seg_1_3a = expected_shortest_bout_th_when_frozen_turn
    seg_1_3b = expected_longest_bout_th_when_frozen_turn
    seg_2_3a = actual_shortest_bout_th_when_frozen_turn
    seg_2_3b = actual_longest_bout_th_when_frozen_turn
    seg_3_3a = expected_shortest_bout_th_when_alternating_turn
    seg_3_3b = expected_longest_bout_th_when_alternating_turn
    seg_4_3a = actual_shortest_bout_th_when_alternating_turn
    seg_4_3b = actual_longest_bout_th_when_alternating_turn


    # ［黒勝ち１つの点数］
    seg_4a = points_configuration.b_step

    # ［黒勝ち１つの点数］
    seg_4b = points_configuration.w_step

    # ［目標の点数］
    seg_4c = points_configuration.span

    # コメント
    seg_5 = comment

    return f"""\
[{seg_0a                  }]  先手勝率 {seg_0b:2.0f} ％ --先後固定制--> {seg_1_1a:8.4f} ％（± {seg_1_1b:7.4f}）    先手勝ち数{black_wons:7}／{round_total:7}対局試行    対局数 {seg_1_3a:>2}～{seg_1_3b:>2}  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点    {seg_5}
                                                                                                                               実際   {seg_2_3a:>2}～{seg_2_3b:>2}
                                             --先後交互制--> {          seg_2_1a:8.4f} ％（± {seg_2_1b:7.4f}）    Ａ氏勝ち数{alice_wons:7}／{round_total:7}対局試行    対局数 {seg_3_3a:>2}～{seg_3_3b:>2}
                                                                                                                               実際   {seg_4_3a:>2}～{seg_4_3b:>2}
"""
    #                                        --


def stringify_log_when_simulation_coin_toss_when_alternating_turn(p, alice_won_rate, new_p_error, b_time, round_total):

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1a = p*100

    # Ａさんが勝った確率
    seg_2 = alice_won_rate*100

    # 誤差
    seg_2b = new_p_error*100

    # # ｎ本勝負
    # seg_3 = b_time

    # 対局試行
    seg_4 = round_total

    return f"[{seg_0}]  先手勝率 {seg_1a:2.0f} ％ --調整--> {seg_2:8.4f} ％（± {seg_2b:7.4f}）（先後交互制でＡさんが勝った確率）  コイントス{seg_4:7}回試行"
