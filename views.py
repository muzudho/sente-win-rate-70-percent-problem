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
    text += f"先手勝率 {seg_1:2.0f} ％ --調整後--> {seg_2:6.4f} ％ （± {best_error*100:>7.4f}）    対局数 {seg_3a:>2}～{seg_3b:>2}    先手勝ち{seg_4:2.0f}点、後手勝ち{seg_5:2.0f}点　目標{seg_6:3.0f}点（先後固定制）"
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

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整後--> {seg_1b:6.4f} ％ （± {error:7.4f}）    先後固定制での反復数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def print_when_generate_b_w_repeat_strict(p, best_balanced_black_win_rate, best_error, max_number_of_bout_when_frozen_turn, points_configuration):
    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {p*100:2.0f} ％ --調整後--> {best_balanced_black_win_rate*100:6.4f} ％ （± {best_error*100:>7.4f}）  対局数ｍ～{max_number_of_bout_when_frozen_turn:>3}  先手勝ち{points_configuration.b_step:2.0f}点、後手勝ち{points_configuration.w_step:2.0f}点　目標{points_configuration.span_when_frozen_turn:3.0f}点（先後固定制）"
    print(text) # 表示


def print_when_generate_even_when_alternating_turn(is_automatic, p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, points_configuration):
    if is_automatic:
        tail = f"  （自動計算満了）"
    else:
        tail = f"  （対象外。誤差十分）"

    print(f"先手勝率：{p*100:2.0f} ％ --調整後--> {best_new_p * 100:>7.04f} ％（± {best_new_p_error * 100:>7.04f}）  最長対局数{best_max_bout_count:2} {best_round_count:6}回  先手勝ち{points_configuration.b_step:2.0f}点、後手勝ち{points_configuration.w_step:2.0f}点　目標{points_configuration.span_when_frozen_turn:3.0f}点（先後固定制）{tail}")


def print_when_generate_when_frozen_turn(is_automatic, p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, points_configuration):
    if is_automatic:
        tail = f"  （自動計算満了）"
    else:
        tail = f"  （対象外。誤差十分）"

    print(f"先手勝率：{p*100:2.0f} ％ --調整後--> {best_new_p * 100:>7.04f} ％（± {best_new_p_error * 100:>7.04f}）  最長対局数{best_max_bout_count:2} {best_round_count:6}回  先手勝ち{points_configuration.b_step:2.0f}点、後手勝ち{points_configuration.w_step:2.0f}点　目標{points_configuration.span_when_frozen_turn:3.0f}点（先後固定制）{tail}", end='')


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
    with open(output_file_path, 'a', encoding='utf8') as f:

        # ［最長対局数（先後固定制）］
        #
        #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
        #
        max_number_of_bout_when_frozen_turn = (b_repeat_when_frozen_turn-1) + (w_repeat_when_frozen_turn-1) + 1

        # 黒が勝った確率
        black_won_rate = black_wons / round_total

        # 均等からの誤差
        error = abs(black_won_rate - 0.5)

        text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％ --調整後--> 先手が勝った確率{black_won_rate*100:8.4f} ％（± {error*100:7.4f}）  {max_number_of_bout_when_frozen_turn:2}本勝負（ただし、{b_repeat_when_frozen_turn:>3}本先取制）  先手勝ち数{black_wons:7}／{round_total:7}対局試行"
        print(text) # 表示
        f.write(f"{text}\n")    # ファイルへ出力
