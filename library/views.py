import datetime
import re

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, FACE_OF_COIN, PLAYERS, SeriesRule, Candidate


def stringify_report_selection_series_rule(p, number_of_series, latest_theoretical_p, specified_series_rule, presentable, candidates, turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
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
        # ［シリーズ・ルール候補］
        candidate_list = candidates[1:-1].split('] [')
        for candidate_element in candidate_list:
            candidate_obj = Candidate.parse_candidate(candidate_element)
            if candidate_obj.p_error is not None:
                if candidate_obj.p_step == specified_series_rule.p_step and candidate_obj.q_step == specified_series_rule.q_step and candidate_obj.span == specified_series_rule.step_table.span:

                    # ［調整後の表が出る確率（％）］
                    seg_2 = candidate_obj.p_error * 100 + 50

                    # 誤差（％）
                    seg_3 = candidate_obj.p_error * 100

                    # ［表勝ち１つの点数］
                    seg_4 = candidate_obj.p_step

                    # ［裏勝ち１つの点数］
                    seg_5 = candidate_obj.q_step

                    # ［目標の点数］
                    seg_6 = candidate_obj.span

                    # ［先後交互制］での［最短対局数］
                    seg_7 = candidate_obj.number_of_shortest_time

                    # ［先後交互制］での［最長対局数］
                    seg_8 = candidate_obj.number_of_longest_time

                    # ［試行回数］
                    seg_9 = number_of_series

                    return f"先手勝率 {seg_1:2.0f} ％ --試行後--> {seg_2:7.4f} ％（{seg_3:+8.4f}）   先手勝ち{seg_4:>3}点、後手勝ち{seg_5:>3}点、目標{seg_6:>3}点    {seg_7:>3}～{seg_8:>3}局（先後交互制）    試行{seg_9}回{seg_10}"


        return f"先手勝率 {seg_1:2.0f} ％ --試行後--> （該当なし）{seg_10}"


    if turn_system == WHEN_FROZEN_TURN:
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
        seg_4 = specified_series_rule.p_step

        # ［裏勝ち１つの点数］
        seg_5 = specified_series_rule.q_step

        # ［目標の点数］
        seg_6 = specified_series_rule.step_table.span

        # ［最短対局数］
        seg_7 = specified_series_rule.number_of_shortest_time

        # ［最長対局数］
        seg_8 = specified_series_rule.number_of_longest_time

        # ［試行回数］
        seg_9 = number_of_series

        # 表示用の説明文
        if isinstance(presentable, str):    # float NaN が入っていることがある
            seg_10 = f"    {presentable}"
        else:
            seg_10 = ''

        return f"先手勝率 {seg_1:2.0f} ％ --理論値--> {seg_2:7.4f} ％（{seg_3:+8.4f}）   先手勝ち{seg_4:>3}点、後手勝ち{seg_5:>3}点、目標{seg_6:>3}点    {seg_7:>3}～{seg_8:>3}局（先後固定制）    試行{seg_9}回{seg_10}"


    raise ValueError(f"{turn_system=}")


def stringify_calculate_probability(p, p_time, q_time, best_p, best_p_error):
    """文言の作成"""

    # ［タイムスタンプ］
    seg_0 = datetime.datetime.now()

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p

    # ［表勝ちだけでの対局数］
    seg_2 = p_time

    # ［裏勝ちだけでの対局数］
    seg_3 = q_time

    # # 計算過程を追加する場合
    # text += f"  {''.join(candidate_list)}"

    text = f"[{seg_0}]  先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {best_p_error:7.4f}）    先後固定制での回数　先手だけ：後手だけ＝{seg_2:>2}：{seg_3:>2}"
    return text


def stringify_p_q_time_strict(p, best_p, best_p_error, series_rule, candidate_list):

    # ［表が出る確率（％）］
    seg_1 = p*100

    # ［調整後の表が出る確率（％）］
    seg_1b = best_p*100

    # ［調整後の表が出る確率（％）と 0.5 との誤差］
    seg_1c = best_p_error*100

    # 対局数

    if series_rule.turn_system == WHEN_FROZEN_TURN:
        ts = '先後固定制'
    elif series_rule.turn_system == WHEN_ALTERNATING_TURN:
        ts = '先後交互制'
    else:
        raise ValueError(f"{series_rule.turn_system=}")

    seg_3a = series_rule.number_of_shortest_time
    seg_3b = series_rule.number_of_longest_time

    seg_4a = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
    seg_4b = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

    # ［目標の点数］
    seg_4c = series_rule.step_table.span

    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {seg_1c:>7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
    return text


def print_even_series_rule(p, best_p, best_p_error, best_number_of_series, series_rule):

    # 対局数
    if series_rule.turn_system == WHEN_FROZEN_TURN:
        ts = '先後固定制'
    elif series_rule.turn_system == WHEN_ALTERNATING_TURN:
        ts = '先後交互制'
    else:
        raise ValueError(f'{series_rule.turn_system=}')

    if series_rule.turn_system == WHEN_ALTERNATING_TURN:
        # ［表が出る確率（％）］
        seg_1a = p*100

        # ［調整後の表が出る確率（％）］
        seg_1b = best_p * 100

        # ［調整後の表が出る確率（％）と 0.5 との誤差］
        seg_1c = best_p_error * 100
        
        seg_3a = series_rule.number_of_shortest_time
        seg_3b = series_rule.number_of_longest_time

        seg_4a = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
        seg_4b = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

        # ［目標の点数］
        seg_4c = series_rule.step_table.span

        print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{best_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)
        return

    if series_rule.turn_system == WHEN_FROZEN_TURN:
        # ［表が出る確率（％）］
        seg_1a = p*100

        # ［調整後の表が出る確率（％）］
        seg_1b = best_p * 100

        # ［調整後の表が出る確率（％）と 0.5 との誤差］
        seg_1c = best_p_error * 100

        # 対局数
        seg_3a = series_rule.number_of_shortest_time
        seg_3b = series_rule.number_of_longest_time

        seg_4a = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
        seg_4b = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

        # ［目標の点数］
        seg_4c = series_rule.step_table.span

        print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{best_number_of_series:6}回    対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)
        return


    raise ValueError(f"{turn_system=}")


def stringify_series_log(
        p, failure_rate, series_rule, trial_results_for_one_series, title, turn_system):
    """シリーズのログの文言作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    failure_rate : float
        ［引き分ける確率］
    series_rule : SeriesRule
        ［シリーズ・ルール］
    trial_results_for_one_series : TrialResultsForOneSeries
        ［シリーズ１つ分の試行結果］
    title : str
        タイトル
    """

    p_step = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
    q_step = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］
    span = series_rule.step_table.span
    b_rest = span
    w_rest = span
    line_1_list = ['   S']
    line_2_list = [f'{b_rest:>4}']
    line_3_list = [f'{w_rest:>4}']

    for winner_color in trial_results_for_one_series.list_of_face_of_coin:
        # 表石        
        if winner_color == HEAD:
            line_1_list.append('   x')
            b_rest -= p_step
        
        # 裏石
        elif winner_color == TAIL:
            line_1_list.append('   o')
            w_rest -= q_step
        
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
    if trial_results_for_one_series.is_won(winner=HEAD, loser=TAIL):
        shw2 = "表"
    elif trial_results_for_one_series.is_won(winner=TAIL, loser=HEAD):
        shw2 = "裏"
    else:
        shw2 = "引"

    # ［Ａさんの勝率］
    # ---------------
    if trial_results_for_one_series.is_won(winner=HEAD, loser=TAIL):
        aw1 = "Ａさん"
    elif trial_results_for_one_series.is_won(winner=TAIL, loser=HEAD):
        aw1 = "Ｂさん"
    else:
        aw1 = "引"

    # 将棋の引分け
    # ------------
    d1 = failure_rate * 100    # ［将棋の引分け率］指定値

    # 対局数
    # ------
    tm10 = series_rule.number_of_shortest_time  # ［最短対局数］理論値
    tm11 = series_rule.number_of_longest_time   # ［最長対局数］
    tm20 = trial_results_for_one_series.number_of_times                            # ［対局数］実践値

    # 勝ち点構成
    # ---------
    pt1 = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)    # ［コインの表が出たときの勝ち点］
    pt2 = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)    # ［コインの裏が出たときの勝ち点］
    pt3 = series_rule.step_table.span      # ［目標の点数］


    return f"""\
[{time1                   }] １シリーズ    {ti1}
                                    将棋の先手勝ち  将棋の引分け  プレイヤー勝敗   シリーズ     | 勝ち点設定
                              指定   |    {shw1:2.0f} ％        {d1:2.0f} ％                        {tm10:>2}～{tm11:>2} 局   | {pt1:3.0f}表
                              試行後 |   {shw2}勝ち                   {aw1}勝ち        {tm20:>2}     局   | {pt2:3.0f}裏
                                                                                                | {pt3:3.0f}目
"""


def stringify_simulation_log(
        p, failure_rate, turn_system, series_rule, large_series_trial_summary, title):
    """シミュレーションのログの文言作成
    
    Parameters
    ----------
    p : float
        ［表が出る確率］（先手勝率）
    failure_rate : float
        ［引き分ける確率］
    turn_system : int
        ［先後運用制度］
    series_rule : SeriesRule
        ［シリーズ・ルール］
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーションの結果
    title : str
        タイトル
    """

    # 変数名を短くする
    S = large_series_trial_summary  # Summary

    
    no_won_series_rate_ht = S.trial_no_won_series_rate(opponent_pair=FACE_OF_COIN)  # 試行した結果、［勝敗付かず］で終わったシリーズの割合
    no_won_series_rate_ab = S.trial_no_won_series_rate(opponent_pair=PLAYERS)       # 試行した結果、［勝敗付かず］で終わったシリーズの割合
    succ_series_rate_ht = 1 - no_won_series_rate_ht                                 # 試行した結果、［勝敗が付いた］シリーズの割合
    succ_series_rate_ab = 1 - no_won_series_rate_ab                                 # 試行した結果、［勝敗が付いた］シリーズの割合


    # ヘッダー
    # --------
    time1 = datetime.datetime.now()     # ［タイムスタンプ］
    ti1 = title                         # タイトル

    succ_p = S.won_rate(success_rate=1, winner=HEAD)            # 試行した結果、引分けを含まない割合で［表番が勝つ確率］
    succ_pe = S.won_rate_error(success_rate=1, winner=HEAD)     # その誤差
    succ_q = S.won_rate(success_rate=1, winner=TAIL)            # 試行した結果、引分けを含まない割合で［裏番が勝つ確率］
    succ_qe = S.won_rate_error(success_rate=1, winner=TAIL)     # その誤差


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


    # ［以下、［かくきんシステム］が算出したシリーズ・ルール］
    # ---------------------------------------------------
    b_pt1 = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)    # ［コインの表が出たときの勝ち点］
    b_pt2 = series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)    # ［コインの裏が出たときの勝ち点］
    b_pt3 = series_rule.step_table.span                                                     # ［目標の点数］
    b_pt4 = series_rule.step_table.get_step_by(challenged=FAILED, face_of_coin=HEAD)        # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
    b_pt5 = series_rule.step_table.get_step_by(challenged=FAILED, face_of_coin=TAIL)        # ［コインの表も裏も出なかったときの、表番の方の勝ち点］
    b_tm10 = series_rule.number_of_shortest_time                                            # ［最短対局数］
    b_tm11 = series_rule.number_of_longest_time                                             # ［最長対局数］


    # コインの表裏の回数
    # -----------------
    succ_a = S.won_rate(success_rate=1, winner=ALICE)             # 引分けを除いた［Ａさんが勝つ確率］実践値
    succ_ae = S.won_rate_error(success_rate=1, winner=ALICE)      # 引分けを除いた［Ａさんが勝つ確率と 0.5 との誤差］実践値
    succ_b = S.won_rate(success_rate=1, winner=BOB)             # 引分けを除いた［Ｂさんが勝つ確率］実践値
    succ_be = S.won_rate_error(success_rate=1, winner=BOB)      # 引分けを除いた［Ｂさんが勝つ確率と 0.5 との誤差］実践値

    h_wins = S.number_of_wins(winner=HEAD)
    t_wins = S.number_of_wins(winner=TAIL)
    ht_total_wins = h_wins + t_wins
    ht_total_fully_wins = S.number_of_fully_wins(elementary_event=HEAD) + S.number_of_fully_wins(elementary_event=TAIL)
    ht_total_points_wins = S.number_of_points_wins(winner=HEAD) + S.number_of_points_wins(winner=TAIL)
    ht_no_wins = S.number_of_no_wins(opponent_pair=FACE_OF_COIN)
    ht_total = ht_total_wins + ht_no_wins

    h_fully_wins = S.number_of_fully_wins(elementary_event=HEAD)
    t_fully_wins = S.number_of_fully_wins(elementary_event=TAIL)
    h_points_wins = S.number_of_points_wins(winner=HEAD)
    t_points_wins = S.number_of_points_wins(winner=TAIL)

    ht152 = ht_total                                # 全シリーズ計
    ht154 = ht_total_fully_wins                     # 引分け無しのシリーズ
    ht157 = ht_total_points_wins + ht_no_wins       # 引分けを含んだシリーズ

    ht162 = ht_total / ht_total * 100
    ht164 = ht_total_fully_wins / ht_total * 100
    ht167 = (ht_total_points_wins + ht_no_wins) / ht_total * 100

    c13 = h_fully_wins                              # 先手満点勝ち
    c14 = t_fully_wins                              # 後手満点勝ち
    c15 = h_points_wins              # 先手判定勝ち（引分けがなければ零です）
    c16 = t_points_wins              # 後手判定勝ち（引分けがなければ零です）
    c17 = ht_no_wins     # コインの表も裏も出なかった
    c11 = c13 + c15
    c12 = c14 + c16

    ht71 = h_wins / ht_total_wins * 100           # 引分けを除いた［将棋の先手勝率（％）］実践値（引分除く）
    ht72 = t_wins / ht_total_wins * 100           # 引分けを除いた［将棋の後手勝率（％）］実践値（引分除く）
    ht81 = (h_wins / ht_total_wins - 0.5) * 100    # 引分けを除いた［将棋の先手勝率（％）と 0.5 との誤差］実践値（引分除く）
    ht82 = (t_wins / ht_total_wins - 0.5) * 100    # 引分けを除いた［将棋の後手勝率（％）と 0.5 との誤差］実践値

    ht41 = h_wins / ht_total * 100              # 引分けを含んだ［将棋の先手勝率］
    ht42 = t_wins / ht_total * 100              # 引分けを含んだ［将棋の後手勝率］
    ht47 = ht_no_wins / ht_total * 100                             # 引分けを含んだ［将棋の引分け率］実践値
    ht51 = (h_wins / ht_total - 0.5) * 100       # 引分けを含んだ［将棋の先手勝率］誤差
    ht52 = (t_wins / ht_total - 0.5) * 100       # 引分けを含んだ［将棋の後手勝率］誤差
    ht57 = (ht_no_wins / ht_total - 0.5) * 100           # 引分けを含んだ［将棋の引分け率］実践値と指定値の誤差


    # プレイヤーの勝敗数
    # -----------------
    a_wins = S.number_of_wins(winner=ALICE)
    b_wins = S.number_of_wins(winner=BOB)
    ab_no_wins = S.number_of_no_wins(opponent_pair=PLAYERS)
    ab_total_wins = a_wins + b_wins
    ab_total_fully_wins = S.number_of_fully_wins(elementary_event=ALICE) + S.number_of_fully_wins(elementary_event=BOB)
    ab_total_points_wins = S.number_of_points_wins(winner=ALICE) + S.number_of_points_wins(winner=BOB)
    ab_total = ab_total_wins + ab_no_wins

    ab152 = ab_total   # 全シリーズ計
    ab154 = ab_total_fully_wins   # 引分け無しのシリーズ
    ab157 = ab_total_points_wins + ab_no_wins     # 引分けを含んだシリーズ

    ab162 = ab_total / ab_total * 100
    ab164 = ab_total_fully_wins / ab_total * 100
    ab167 = (ab_total_points_wins + ab_no_wins) / ab_total * 100

    c101 = S.number_of_wins(winner=ALICE)                       # Ａさんの勝ちの総数
    c102 = S.number_of_wins(winner=BOB)                         # Ｂさんの勝ちの総数
    c103 = S.number_of_fully_wins(elementary_event=ALICE)       # Ａさん満点勝ち
    c104 = S.number_of_fully_wins(elementary_event=BOB)         # Ｂさん満点勝ち
    c105 = S.number_of_points_wins(winner=ALICE)     # Ａさん判定勝ち（引分けがなければ零です）
    c106 = S.number_of_points_wins(winner=BOB)     # Ｂさん判定勝ち（引分けがなければ零です）
    c107 = ab_no_wins           # ＡさんもＢさんも勝ちではなかった

    ab71 = a_wins / ab_total_wins * 100           # 引分けを除いた［Ａさんが勝つ確率（％）］実践値
    ab72 = b_wins / ab_total_wins * 100           # 引分けを除いた［Ｂさんが勝つ確率（％）］実践値
    ab81 = (a_wins / ab_total_wins - 0.5) * 100         # 引分けを除いた［Ａさんが勝つ確率（％）と 0.5 との誤差］実践値
    ab82 = (b_wins / ab_total_wins - 0.5) * 100         # 引分けを除いた［Ｂさんが勝つ確率（％）と 0.5 との誤差］実践値

    ab41 = a_wins / ab_total * 100                    # ［表も裏も出なかった確率］も含んだ割合で、［Ａさんが勝つ確率］実践値（％）
    ab42 = b_wins / ab_total * 100                    # ［表も裏も出なかった確率］も含んだ割合で、［Ｂさんが勝つ確率］実践値（％）
    ab47 = ab_no_wins / ab_total * 100                             # ［表も裏も出なかった確率］実践値（％）
    ab51 = (a_wins / ab_total - 0.5) * 100                   # 茣蓙の実践値（％）
    ab52 = (b_wins / ab_total - 0.5) * 100                   # 茣蓙の実践値（％）
    ab57 = (ab_no_wins / ab_total - 0.5) * 100            # 茣蓙の実践値（％）

    # 対局数
    # ------
    tm_s = S.shortest_time_th    # ［最短対局数］実践値
    tm_l = S.longest_time_th     # ［最長対局数］

    #                                                                                              1         1         1
    #    1         2         3         4         5         6         7         8         9         0         1         2
    # 7  0         0         0         0         0         0         0         0         0         0         0         0
    return f"""\
[{time1                   }] {ti1}
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
              | 以下、指定したもの                                                                                                            |
              | 将棋の先手勝ち| 将棋の引分け  | 将棋の後手勝ち| シリーズ試行  |                                                               |
              |   {a_shw1:8.4f} ％      {a_d1:8.4f} ％     {a_shl1:8.4f} ％    {a_sr0:>8} 回                                                                 |
              | {a_trn:90}|
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
              | 以下、［かくきんシステム］が算出したシリーズ・ルール                                                                          |
              |                                                                        勝ち点          決着時        引分け時 | 対局数        |
              |                                                                            表          {b_pt1:4.0f}点      {b_pt4:8.4f}点 |{b_tm10:>4} ～{b_tm11:>4} 局 |
              |                                                                            裏          {b_pt2:4.0f}点      {b_pt5:8.4f}点 |               |
              |                                                                          目標          {b_pt3:4.0f}点                 |               |
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
              | 以下、［かくきんシステム］を使って試行                                                                                        |
              | 全シリーズ計                  | 引分け無しのシリーズ          | 引分けを含んだシリーズ                        | 対局数        |
              |                   {ht152:>8} 回 |                   {ht154:>8} 回 |                                   {ht157:>8} 回 |{tm_s:>4} ～{tm_l:>4} 局 |
              |                   {ht162:>8.4f} ％ |                   {ht164:>8.4f} ％ |                                   {ht167:>8.4f} ％ |               |
              |                               |                               |                                               |               |
              | 先手勝ち      | 後手勝ち      |///////////////|///////////////|///////////////|///////////////| 勝敗付かず    |               |
              |   { c11:>8} 回 |   { c12:>8} 回 |///////////////|///////////////|///////////////|///////////////|   {c17:>8} 回 |               |
              |               |               | 先手満点勝ち  | 後手満点勝ち  | 先手点数勝ち  | 後手点数勝ち  |               | 対局数        |
              |               |               |   {c13:>8} 回 |   {c14:>8} 回 |   {c15:>8} 回 |   {c16:>8} 回 |               |               |
              |                                                                                                               |               |
    引分除く  |   {ht71:8.4f} ％     {ht72:8.4f} ％                                                                                 |               |
              |（{ht81:+9.4f}）   （{ht82:+9.4f}）                                                                                  |               |
              |                                                                                                               |               |
    引分込み  |   {ht41:8.4f} ％     {ht42:8.4f} ％                                                                     {ht47:8.4f} ％ |               |
              |（{ht51:+9.4f}）   （{ht52:+9.4f}）                                                                   （{ht57:+9.4f}）  |               |
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+               |
              | 全シリーズ計                  | 引分け無しのシリーズ          | 引分けを含んだシリーズ                        |               |
              |                   {ab152:>8} 回 |                   {ab154:>8} 回 |                                   {ab157:>8} 回 |               |
              |                   {ab162:>8.4f} ％ |                   {ab164:>8.4f} ％ |                                   {ab167:>8.4f} ％ |               |
              |                               |                               |                                               |               |
              | Ａさん勝ち    | Ｂさん勝ち    |///////////////|///////////////|///////////////|///////////////| 勝敗付かず    |               |
              |   {c101:>8} 回 |   {c102:>8} 回 |///////////////|///////////////|///////////////|///////////////|   {c107:>8} 回 |               |
              |               |               | Ａさん満点勝ち| Ｂさん満点勝ち| Ａさん点数勝ち| Ｂさん点数勝ち|               |               |
              |               |               |   {c103:>8} 回 |   {c104:>8} 回 |   {c105:>8} 回 |   {c106:>8} 回 |               |               |
              |                                                                                                               |               |
    引分除く  |   { ab71:8.4f} ％     { ab72:8.4f} ％                                                                                 |               |
              |（{ ab81:+9.4f}）   （{ ab82:+9.4f}）                                                                                  |               |
              |                                                                                                               |               |
    引分込み  |   {ab41:8.4f} ％     {ab42:8.4f} ％                                                                     {ab47:8.4f} ％ |               |
              |（{ab51:+9.4f}）   （{ab52:+9.4f}）                                                                   （{ab57:+9.4f}）  |               |
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
"""


def stringify_analysis_series(p, failure_rate, series_result_list, turn_system):
    if turn_system == WHEN_FROZEN_TURN:
        """シリーズ分析中のログ"""

        # 集計
        head_wons = 0
        no_wons_color = 0
        tail_wons = 0
        for trial_results_for_one_series in series_result_list:
            if trial_results_for_one_series.is_won(winner=HEAD, loser=TAIL):
                head_wons += 1
            elif trial_results_for_one_series.is_won(winner=TAIL, loser=HEAD):
                tail_wons += 1
            elif trial_results_for_one_series.is_no_won(opponent_pair=FACE_OF_COIN):
                no_wons_color += 1
        
        # 結果としての表の勝率
        result_head_wons_without_failure = head_wons / (len(series_result_list) - no_wons_color)
        result_head_wons_with_failure = head_wons / len(series_result_list)

        # 結果としての引分け率
        result_no_wons_color_with_failure = no_wons_color / len(series_result_list)

        # 結果としての裏の勝率
        result_tail_wons_without_failure = tail_wons / (len(series_result_list) - no_wons_color)
        result_tail_wons_with_failure = tail_wons / len(series_result_list)

        # 将棋の先手勝率など
        shw1 = p * 100
        shd1 = failure_rate
        shl1 = (1 - p) * 100

        bw1 = result_head_wons_without_failure * 100
        bw2 = result_head_wons_with_failure * 100

        bd2 = result_no_wons_color_with_failure * 100

        ww1 = result_tail_wons_without_failure * 100
        ww2 = result_tail_wons_with_failure * 100

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

        return


    raise ValueError(f"{turn_system=}")
