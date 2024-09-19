import datetime

from library import PointsConfiguration


def stringify_when_generate_takahashi_satoshi_system(p, best_balanced_black_win_rate, best_error, best_b_repeat_when_frozen_turn, best_w_repeat_when_frozen_turn):
    """文言の作成"""

    # ［勝ち点ルール］の構成
    points_configuration = PointsConfiguration.let_points_from_require(best_b_repeat_when_frozen_turn, best_w_repeat_when_frozen_turn)

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_2 = best_balanced_black_win_rate*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_2b = best_error*100

    # ［最長対局数（先後固定制）］
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()

    # ［白勝ちの価値］
    seg_4 = points_configuration.b_step

    # ［黒勝ちの価値］
    seg_5 = points_configuration.w_step

    # ［目標の点］
    seg_6 = points_configuration.span_when_frozen_turn

    text = ""
    #text += f"[{datetime.datetime.now()}]  " # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整後--> {seg_2:6.4f} ％ （± {seg_2b:>7.4f}）    対局数 {seg_3a:>2}～{seg_3b:>2}    先手勝ち{seg_4:2.0f}点、後手勝ち{seg_5:2.0f}点　目標{seg_6:3.0f}点（先後固定制）"
    return text


def stringify_when_let_calculate_probability(p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn, balanced_black_win_rate, error):
    """文言の作成"""

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = balanced_black_win_rate

    # ［黒だけでの反復数］
    seg_2 = b_repeat_when_frozen_turn

    # ［白だけでの反復数］
    seg_3 = w_repeat_when_frozen_turn

    # # 計算過程を追加する場合
    # text += f"  {''.join(process_list)}"

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整後--> {seg_1b:6.4f} ％ （± {error:7.4f}）    先後固定制での反復数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def stringify_when_generate_b_w_repeat_strict(p, best_balanced_black_win_rate, best_error, points_configuration, process_list):

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_balanced_black_win_rate*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_error*100

    # ［最長対局数（先後固定制）］
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()

    # ［黒勝ちの価値］
    seg_4a = points_configuration.b_step

    # ［黒勝ちの価値］
    seg_4b = points_configuration.w_step

    # ［目標の点］
    seg_4c = points_configuration.span_when_frozen_turn

    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整後--> {seg_1b:6.4f} ％ （± {seg_1c:>7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
    return text


def print_when_generate_even_when_alternating_turn(is_automatic, p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_new_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_new_p_error * 100

    # ［最長対局数（先後固定制）］
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()

    if seg_3b != best_max_bout_count:
        raise ValueError(f"実践値と理論値が異なる {seg_3a=}  {best_max_bout_count=}")

    # ［黒勝ちの価値］
    seg_4a = points_configuration.b_step

    # ［黒勝ちの価値］
    seg_4b = points_configuration.w_step

    # ［目標の点］
    seg_4c = points_configuration.span_when_frozen_turn

    if is_automatic:
        seg_5 = f"  （自動計算満了）"
    else:
        seg_5 = f"  （対象外。誤差十分）"

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整後--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  対局数 {seg_3a:>2}～{seg_3b:>2} {best_round_count:6}回  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）{seg_5}")


def print_when_generate_when_frozen_turn(is_automatic, p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_new_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_new_p_error * 100

    # ［最長対局数（先後固定制）］
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()

    if seg_3b != best_max_bout_count:
        raise ValueError(f"実践値と理論値が異なる {seg_3a=}  {best_max_bout_count=}")

    # ［黒勝ちの価値］
    seg_4a = points_configuration.b_step

    # ［黒勝ちの価値］
    seg_4b = points_configuration.w_step

    # ［目標の点］
    seg_4c = points_configuration.span_when_frozen_turn

    if is_automatic:
        seg_5 = f"  （自動計算満了）"
    else:
        seg_5 = f"  （対象外。誤差十分）"

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整後--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  対局数 {seg_3a:>2}～{seg_3b:>2} {best_round_count:6}回  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）{seg_5}")


def write_coin_toss_log(output_file_path, black_win_rate, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn, round_total, black_wons):
    """ログ出力
    
    Parameters
    ----------
    output_file_path : str
        出力先ファイルへのパス
    black_win_rate : float
        黒が出る確率（先手勝率）
    b_repeat_when_frozen_turn : int
        先手の何本先取制
    w_repeat_when_frozen_turn : int
        後手の何本先取制
    round_total : int
        対局数
    black_wons : int
        黒が勝った回数
    """

    # ［最長対局数（先後固定制）］
    #
    #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
    #

    # ［勝ち点ルール］の構成
    points_configuration = PointsConfiguration.let_points_from_require(b_repeat_when_frozen_turn, w_repeat_when_frozen_turn)

    # 黒が勝った確率
    black_won_rate = black_wons / round_total

    # 均等からの誤差
    error = abs(black_won_rate - 0.5)

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1a = black_win_rate*100

    # ［調整後の表が出る確率（％）］
    seg_1b = black_won_rate*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = error*100

    # ［最長対局数（先後固定制）］
    seg_3a = points_configuration.let_number_of_shortest_bout_when_frozen_turn()
    seg_3b = points_configuration.let_number_of_longest_bout_when_frozen_turn()

    # ［黒勝ちの価値］
    seg_4a = points_configuration.b_step

    # ［黒勝ちの価値］
    seg_4b = points_configuration.w_step

    # ［目標の点］
    seg_4c = points_configuration.span_when_frozen_turn


    with open(output_file_path, 'a', encoding='utf8') as f:
        text = f"[{seg_0}]  先手勝率 {seg_1a:2.0f} ％ --実際--> {seg_1b:8.4f} ％（± {seg_1c:7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}  先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）  先手勝ち数{black_wons:7}／{round_total:7}対局試行"
        print(text) # 表示
        f.write(f"{text}\n")    # ファイルへ出力
