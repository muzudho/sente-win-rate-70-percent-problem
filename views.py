import datetime
import re

from library import HEAD, TAIL, ALICE, BOB, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, COIN_HEAD_AND_TAIL, PLAYER_A_AND_B, PointsConfiguration


def parse_process_element(process_element):
    result = re.match(r'([0-9.-]+) (\d+)表 (\d+)裏 (\d+)目 (\d+)～(\d+)局', process_element)
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

                # ［表勝ち１つの点数］
                seg_4 = b_step

                # ［裏勝ち１つの点数］
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

    # ［表勝ち１つの点数］
    seg_4 = specified_points_configuration.b_step

    # ［裏勝ち１つの点数］
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


def stringify_when_let_calculate_probability(p, b_time, w_time, best_p, best_p_error):
    """文言の作成"""

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p

    # ［表勝ちだけでの対局数］
    seg_2 = b_time

    # ［裏勝ちだけでの対局数］
    seg_3 = w_time

    # # 計算過程を追加する場合
    # text += f"  {''.join(process_list)}"

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {best_p_error:7.4f}）    先後固定制での回数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def stringify_when_generate_b_w_time_strict(p, best_p, best_p_error, pts_conf, process_list):

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error*100

    # 対局数
    seg_3a = pts_conf.number_shortest_time_when_frozen_turn
    seg_3b = pts_conf.number_longest_time_when_frozen_turn
    seg_3c = pts_conf.count_shortest_time_when_alternating_turn()
    seg_3d = pts_conf.count_longest_time_when_alternating_turn()

    # ［表勝ち１つの点数］
    seg_4a = pts_conf.b_step

    # ［表勝ち１つの点数］
    seg_4b = pts_conf.w_step

    # ［目標の点数］
    seg_4c = pts_conf.span

    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {seg_1c:>7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
    return text


def print_when_generate_even_when_alternating_turn(p, best_p, best_p_error, best_number_of_series, pts_conf):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error * 100

    # 対局数
    seg_3a = pts_conf.number_shortest_time_when_frozen_turn
    seg_3b = pts_conf.number_longest_time_when_frozen_turn
    seg_3c = pts_conf.count_shortest_time_when_alternating_turn()
    seg_3d = pts_conf.count_longest_time_when_alternating_turn()

    # ［表勝ち１つの点数］
    seg_4a = pts_conf.b_step

    # ［表勝ち１つの点数］
    seg_4b = pts_conf.w_step

    # ［目標の点数］
    seg_4c = pts_conf.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{best_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def print_when_generate_when_frozen_turn(p, specified_p, specified_p_error, specified_number_of_series, specified_points_configuration):

    # ［表が出る確率（％）］
    seg_1a = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = specified_p * 100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = specified_p_error * 100

    # 対局数
    seg_3a = specified_points_configuration.number_shortest_time_when_frozen_turn
    seg_3b = specified_points_configuration.number_longest_time_when_frozen_turn
    seg_3c = specified_points_configuration.count_shortest_time_when_alternating_turn()
    seg_3d = specified_points_configuration.count_longest_time_when_alternating_turn()

    # ［表勝ち１つの点数］
    seg_4a = specified_points_configuration.b_step

    # ［表勝ち１つの点数］
    seg_4b = specified_points_configuration.w_step

    # ［目標の点数］
    seg_4c = specified_points_configuration.span

    print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{specified_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（先後固定制）  {seg_3c:>2}～{seg_3d:>2}（先後交互制）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)


def stringify_series_log(
        p, failure_rate, pts_conf, series_result, title):
    """シリーズのログの文言作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    failure_rate : float
        ［引き分ける確率］
    pts_conf : PointsConfiguration
        ［かくきんシステムのｐの構成］
    series_result : SeriesResult
        シリーズの結果
    title : str
        タイトル
    """

    b_step = pts_conf.b_step
    w_step = pts_conf.w_step
    span = pts_conf.span
    b_rest = span
    w_rest = span
    line_1_list = ['   S']
    line_2_list = [f'{b_rest:>4}']
    line_3_list = [f'{w_rest:>4}']

    for winner_color in series_result.pseudo_series_result.successful_color_list:
        # 表石        
        if winner_color == HEAD:
            line_1_list.append('   x')
            b_rest -= b_step
        
        # 裏石
        elif winner_color == TAIL:
            line_1_list.append('   o')
            w_rest -= w_step
        
        # 勝者なし
        else:
            line_1_list.append('   .')

        line_2_list.append(f'{b_rest:>4}')
        line_3_list.append(f'{w_rest:>4}')

    print() # 改行
    print(' '.join(line_1_list))
    print(' '.join(line_2_list))
    print(' '.join(line_3_list))


    # ヘッダー
    # --------
    time1 = datetime.datetime.now() # ［タイムスタンプ］
    ti1 = title                     # タイトル

    # ［将棋の先手勝率］
    # -----------------
    shw1 = p * 100                                                             # ［将棋の先手勝率（％）］指定値
    if series_result.is_won(winner=HEAD, loser=TAIL):
        shw2 = "表"
    elif series_result.is_won(winner=TAIL, loser=HEAD):
        shw2 = "裏"
    else:
        shw2 = "引"

    # ［Ａさんの勝率］
    # ---------------
    if series_result.is_won(winner=HEAD, loser=TAIL):
        aw1 = "Ａさん"
    elif series_result.is_won(winner=TAIL, loser=HEAD):
        aw1 = "Ｂさん"
    else:
        aw1 = "引"

    # 将棋の引分け
    # ------------
    d1 = failure_rate * 100    # ［将棋の引分け率］指定値

    # 対局数
    # ------
    tm10 = pts_conf.number_shortest_time_when_frozen_turn  # ［最短対局数］理論値
    tm11 = pts_conf.number_longest_time_when_frozen_turn   # ［最長対局数］
    tm20 = series_result.number_of_all_times    # ［対局数］実践値

    # 勝ち点構成
    # ---------
    pt1 = pts_conf.b_step    # ［表勝ち１つの点数］
    pt2 = pts_conf.w_step    # ［裏勝ち１つの点数］
    pt3 = pts_conf.span      # ［目標の点数］


    return f"""\
[{time1                   }] １シリーズ    {ti1}
                                    将棋の先手勝ち  将棋の引分け  プレイヤー勝敗   シリーズ     | 勝ち点設定
                              指定   |    {shw1:2.0f} ％        {d1:2.0f} ％                        {tm10:>2}～{tm11:>2} 局   | {pt1:3.0f}表
                              試行後 |   {shw2}勝ち                   {aw1}勝ち        {tm20:>2}     局   | {pt2:3.0f}裏
                                                                                                | {pt3:3.0f}目
"""


def stringify_simulation_log(
        p, failure_rate, turn_system, pts_conf, large_series_trial_summary, title):
    """シミュレーションのログの文言作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    failure_rate : float
        ［引き分ける確率］
    turn_system : int
        ［先後運用制度］
    pts_conf : PointsConfiguration
        ［かくきんシステムのｐの構成］
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーションの結果
    title : str
        タイトル
    """

    # 変数名を短くする
    S = large_series_trial_summary  # Summary

    # 試行した結果、［引き分けた率］
    trial_failure_rate = S.failure_rate(turn_system=turn_system)

    # 試行した結果、［決着が付いた率］
    trial_successful_rate = 1 - trial_failure_rate


    # ヘッダー
    # --------
    time1 = datetime.datetime.now()     # ［タイムスタンプ］
    ti1 = title                         # タイトル

    trial_p = S.win_rate_without_draw(winner=HEAD, loser=TAIL, turn_system=turn_system)                     # 引分けを除いた［表が出る確率］
    trial_p_error = S.win_rate_error_without_draw(winner=HEAD, loser=TAIL, turn_system=turn_system)         # 引分けを除いた［表が出る確率］の誤差

    trial_q = S.win_rate_without_draw(winner=TAIL, loser=HEAD, turn_system=turn_system)                     # 引分けを除いた［裏が出る確率］
    trial_q_error = S.win_rate_error_without_draw(winner=TAIL, loser=HEAD, turn_system=turn_system)         # 引分けを除いた［裏が出る確率］の誤差


    # ［以下、指定したもの］
    # ---------------------
    a_shw1 = p * 100                # ［将棋の先手勝率（％）］指定値
    a_d1 = failure_rate * 100       # ［将棋の引分け率］指定値
    a_shl1 = (1 - p) * 100          # ［将棋の後手勝率（％）］指定値
    a_sr0 = S.number_of_series      # 全シリーズ数

    # 全角文字の横幅は文字数を揃えること。全角文字の幅が半角のちょうど2倍ではないのでずれるので、書式設定の桁数を指定してもずれるから。
    if turn_system == WHEN_FROZEN_TURN:
        a_trn = "［先後固定制］上手と下手のように、Ａさんはずっと先手、Ｂさんはずっと後手"
    elif turn_system == WHEN_ALTERNATING_TURN:
        a_trn = "［先後交互制］Ａさんの先手、Ｂさんの後手で始まり、１局毎に先後を入替える"
    else:
        raise ValueError(f"{turn_system=}")


    # ［以下、［かくきんシステム］が算出した設定］
    # -----------------------------------------
    b_tm10 = pts_conf.number_shortest_time_when_frozen_turn  # ［最短対局数］理論値
    b_tm11 = pts_conf.number_longest_time_when_frozen_turn   # ［最長対局数］
    # 勝ち点構成
    b_pt1 = pts_conf.b_step             # ［表勝ち１つの点数］
    b_pt2 = pts_conf.w_step             # ［裏勝ち１つの点数］
    b_pt3 = pts_conf.span               # ［目標の点数］
    b_pt4 = pts_conf.b_step_when_draw   # ［表勝ち１つの点数］
    b_pt5 = pts_conf.w_step_when_draw   # ［裏勝ち１つの点数］


    # ［以下、［かくきんシステム］を使って試行］１ブロック目（色、引分除く）
    # ---------------------------------------------
    c1_shw = trial_p * 100           # 引分けを除いた［将棋の先手勝率（％）］実践値（引分除く）
    c1_shwe = trial_p_error * 100    # 引分けを除いた［将棋の先手勝率（％）と 0.5 との誤差］実践値（引分除く）
    c1_shl = trial_q * 100           # 引分けを除いた［将棋の後手勝率（％）］実践値（引分除く）
    c1_shle = trial_q_error * 100    # 引分けを除いた［将棋の後手勝率（％）と 0.5 との誤差］実践値


    # ［以下、［かくきんシステム］を使って試行］２ブロック目（色、引分込み）
    # ---------------------------------------------
    c2_shw = trial_successful_rate * trial_p * 100              # 引分けを含んだ［将棋の先手勝率］
    c2_shwe = trial_successful_rate * trial_p_error * 100       # 引分けを含んだ［将棋の先手勝率］誤差
    c2_d = trial_failure_rate * 100                             # 引分けを含んだ［将棋の引分け率］実践値
    c2_de = (trial_failure_rate - failure_rate) * 100           # 引分けを含んだ［将棋の引分け率］実践値と指定値の誤差
    c2_shl = trial_successful_rate * trial_q * 100              # 引分けを含んだ［将棋の後手勝率］
    c2_shle = trial_successful_rate * trial_q_error * 100       # 引分けを含んだ［将棋の後手勝率］誤差


    # ［以下、［かくきんシステム］を使って試行］３ブロック目（プレイヤー、引分除く）
    # ---------------------------------------------
    trial_a = S.win_rate_without_draw(winner=ALICE, loser=BOB, turn_system=turn_system)             # 引分けを除いた［Ａさんが勝つ確率］実践値
    trial_ae = S.win_rate_error_without_draw(winner=ALICE, loser=BOB, turn_system=turn_system)      # 引分けを除いた［Ａさんが勝つ確率と 0.5 との誤差］実践値
    trial_b = S.win_rate_without_draw(winner=BOB, loser=ALICE, turn_system=turn_system)             # 引分けを除いた［Ｂさんが勝つ確率］実践値
    trial_be = S.win_rate_error_without_draw(winner=BOB, loser=ALICE, turn_system=turn_system)      # 引分けを除いた［Ｂさんが勝つ確率と 0.5 との誤差］実践値

    c3_aw = trial_a * 100           # 引分けを除いた［Ａさんが勝つ確率（％）］実践値
    c3_awe = trial_ae * 100         # 引分けを除いた［Ａさんが勝つ確率（％）と 0.5 との誤差］実践値
    c3_bw = trial_b * 100           # 引分けを除いた［Ｂさんが勝つ確率（％）］実践値
    c3_bwe = trial_be * 100         # 引分けを除いた［Ｂさんが勝つ確率（％）と 0.5 との誤差］実践値


    # ［以下、［かくきんシステム］を使って試行］４ブロック目（プレイヤー、引分含む）
    # ---------------------------------------------
    c4_aw = trial_successful_rate * trial_a * 100           # 引分けを含んだ［Ａさんが勝つ確率（％）］実践値
    c4_awe = trial_successful_rate * trial_ae * 100         # 引分けを含んだ［Ａさんが勝つ確率（％）と 0.5 との誤差］実践値
    c4_d = trial_failure_rate * 100                         # ［将棋の引分け率］実践値            　［先後交互制］
    c4_de = (trial_failure_rate - failure_rate) * 100       # ［将棋の引分け率］実践値と指定値の誤差 ［先後交互制］
    c4_bw = trial_successful_rate * trial_b * 100           # 引分けを含んだ［Ｂさんが勝つ確率（％）］実践値
    c4_bwe = trial_successful_rate * trial_be * 100         # 引分けを含んだ［Ｂさんが勝つ確率（％）と 0.5 との誤差］実践値


    # シリーズ数
    # ---------
    sr1 = S.number_of_no_wons(opponent_pair=COIN_HEAD_AND_TAIL)     # コインの表も裏も出なかった
    sr2 = S.number_of_fully_wons(HEAD)                              # 先手満点勝ち
    sr3 = S.number_of_fully_wons(TAIL)                              # 後手満点勝ち
    sr4 = S.number_of_points_wons(winner=HEAD, loser=TAIL)          # 先手判定勝ち（引分けがなければ零です）
    sr5 = S.number_of_points_wons(winner=TAIL, loser=HEAD)          # 後手判定勝ち（引分けがなければ零です）
    sr6 = S.number_of_no_wons(opponent_pair=PLAYER_A_AND_B)         # ＡさんもＢさんも勝ちではなかった
    sr7 = S.number_of_fully_wons(ALICE)                             # Ａさん満点勝ち
    sr8 = S.number_of_fully_wons(BOB)                               # Ｂさん満点勝ち
    sr9 = S.number_of_points_wons(winner=ALICE, loser=BOB)          # Ａさん判定勝ち（引分けがなければ零です）
    sr10 = S.number_of_points_wons(winner=BOB, loser=ALICE)         # Ｂさん判定勝ち（引分けがなければ零です）


    # 対局数
    # ------
    tm20 = S.shortest_time_th    # ［最短対局数］実践値
    tm21 = S.longest_time_th     # ［最長対局数］

    # FIXME 勝ちの内訳を［満点勝ち］［判定勝ち］で表示したい
    # FIXME ［引分除く］［引分込み］でも表示したい

    #                                                                                              1         1         1
    #    1         2         3         4         5         6         7         8         9         0         1         2
    # 7  0         0         0         0         0         0         0         0         0         0         0         0
    return f"""\
[{time1                   }] {ti1}
              +------------------------------------------------------------------------------------------------------------+
              | 以下、指定したもの                                                                                         |
              | 将棋の先手勝ち  将棋の引分け  将棋の後手勝ち   .                  シリーズ                                 |
              |      {  a_shw1:8.4f} ％  {a_d1:8.4f} ％   {  a_shl1:8.4f} ％    .            試行{a_sr0:>8}回                                 |
              | {a_trn:71}|
              +------------------------------------------------------------------------------------------------------------+
              | 以下、［かくきんシステム］が算出した設定                                                                   |
              |                                                                              対局数    勝ち点  引分け時    |
              |                                                                             {b_tm10:>2}～{b_tm11:>2} 局   {b_pt1:3.0f}表  {b_pt4:8.4f}表  |
              |                                                                                         {b_pt2:3.0f}裏  {b_pt5:8.4f}裏  |
              |                                                                                         {b_pt3:3.0f}目              |
              +------------------------------------------------------------------------------------------------------------+
              | 以下、［かくきんシステム］を使って試行                                                                     |
              |       先手勝ち     引分け        後手勝ち      .            引分{sr1:>8}回   対局数                        |
    引分除く  |      {  c1_shw:8.4f} ％                {  c1_shl:8.4f} ％    .  先手  満点勝ち{sr2:>8}回  {tm20:>2}～{tm21:>2} 局                      |
              |   （{c1_shwe:+9.4f}）              （{c1_shle:+9.4f}）     .  後手  満点勝ち{sr3:>8}回                                 |
    引分込み  |      {  c2_shw:8.4f} ％  {c2_d:8.4f} ％   {  c2_shl:8.4f} ％    .  先手  判定勝ち{sr4:>8}回                                 |
              |   （{c2_shwe:+9.4f}）（{c2_de:+9.4f}） （{c2_shle:+9.4f}）     .  後手  判定勝ち{sr5:>8}回                                 |
              |       Ａさんの勝ち               Ｂさんの勝ち  .            引分{sr6:>8}回                                 |
    引分除く  |      {c3_aw:8.4f} ％                {c3_bw:8.4f} ％    .  Ａさん満点勝ち{sr7:>8}回                                 |
              |   （{c3_awe:+9.4f}）              （{c3_bwe:+9.4f}）     .  Ｂさん満点勝ち{sr8:>8}回                                 |
    引分込み  |      {  c4_aw:8.4f} ％  {c4_d       :8.4f} ％   {  c4_bw:8.4f} ％    .  Ａさん判定勝ち{sr9:>8}回                                 |
              |   （{c4_awe:+9.4f}）（{c4_de   :+9.4f}） （{c4_bwe:+9.4f}）     .  Ｂさん判定勝ち{sr10:>8}回                                 |
              +------------------------------------------------------------------------------------------------------------+
"""


def stringify_analysis_series_when_frozen_turn(p, failure_rate, series_result_list):
    """シリーズ分析中のログ"""

    # 集計
    black_wons = 0
    no_wons_color = 0
    white_wons = 0
    for series_result in series_result_list:
        if series_result.is_won(winner=HEAD, loser=TAIL):
            black_wons += 1
        elif series_result.is_won(winner=TAIL, loser=HEAD):
            white_wons += 1
        elif series_result.is_no_won(opponent_pair=COIN_HEAD_AND_TAIL):
            no_wons_color += 1
    
    # 結果としての表の勝率
    result_black_wons_without_draw = black_wons / (len(series_result_list) - no_wons_color)
    result_black_wons_with_draw = black_wons / len(series_result_list)

    # 結果としての引分け率
    result_no_wons_color_with_draw = no_wons_color / len(series_result_list)

    # 結果としての裏の勝率
    result_white_wons_without_draw = white_wons / (len(series_result_list) - no_wons_color)
    result_white_wons_with_draw = white_wons / len(series_result_list)

    # 将棋の先手勝率など
    shw1 = p * 100
    shd1 = failure_rate
    shl1 = (1 - p) * 100

    bw1 = result_black_wons_without_draw * 100
    bw2 = result_black_wons_with_draw * 100

    bd2 = result_no_wons_color_with_draw * 100

    ww1 = result_white_wons_without_draw * 100
    ww2 = result_white_wons_with_draw * 100

    print(f"""\
         +--------------------------------------------------------------+
         | 以下、指定したもの                                           |
         |  将棋の先手勝率        将棋の引分け率        将棋の後手勝率  |
         |  {shw1:8.4f} ％           {shd1:8.4f} ％           {shl1:8.4f} ％     |
         +--------------------------------------------------------------+
         | 以下、［かくきんシステム］が設定したハンディキャップ         |
         |  先手勝率              引分け率              後手勝率        |
引分除く |  {bw1:8.4f} ％                                 {  ww1:8.4f} ％     |
引分込み |  {bw2:8.4f} ％           {bd2:8.4f} ％           {ww2:8.4f} ％     |
         +--------------------------------------------------------------+
""")
