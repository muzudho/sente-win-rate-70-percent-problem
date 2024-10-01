import datetime
import re

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, FACE_OF_COIN, PLAYERS, IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Converter, SeriesRule, Candidate


def stringify_report_selection_series_rule(p, latest_theoretical_p, specified_series_rule, presentable, candidates, turn_system):
    if turn_system == ALTERNATING_TURN:
        """［先後交互制］での、むずでょが推奨する［かくきんシステムのｐの構成］

        Parameters
        ----------
        specified_series_rule : SeriesRule
            ［シリーズ・ルール］
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
                if candidate_obj.h_step == specified_series_rule.h_step and candidate_obj.t_step == specified_series_rule.t_step and candidate_obj.span == specified_series_rule.step_table.span:

                    # ［調整後の表が出る確率（％）］
                    seg_2 = candidate_obj.p_error * 100 + 50

                    # 誤差（％）
                    seg_3 = candidate_obj.p_error * 100

                    # ［表勝ち１つの点数］
                    seg_4 = candidate_obj.h_step

                    # ［裏勝ち１つの点数］
                    seg_5 = candidate_obj.t_step

                    # ［目標の点数］
                    seg_6 = candidate_obj.span

                    # ［先後交互制］での［最短対局数］
                    seg_7 = candidate_obj.shortest_coins

                    # ［先後交互制］での［上限対局数］
                    seg_8 = candidate_obj.upper_limit_coins

                    # ［試行シリーズ数］
                    seg_9 = specified_series_rule.trials_series

                    return f"先手勝率 {seg_1:2.0f} ％ --試行後--> {seg_2:7.4f} ％（{seg_3:+8.4f}）   先手勝ち{seg_4:>3}点、後手勝ち{seg_5:>3}点、目標{seg_6:>3}点    {seg_7:>3}～{seg_8:>3}局（先後交互制）    試行{seg_9}回{seg_10}"


        return f"先手勝率 {seg_1:2.0f} ％ --試行後--> （該当なし）{seg_10}"


    if turn_system == FROZEN_TURN:
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
        seg_4 = specified_series_rule.h_step

        # ［裏勝ち１つの点数］
        seg_5 = specified_series_rule.t_step

        # ［目標の点数］
        seg_6 = specified_series_rule.step_table.span

        # ［最短対局数］
        seg_7 = specified_series_rule.shortest_coins

        # ［上限対局数］
        seg_8 = specified_series_rule.upper_limit_coins

        # ［試行シリーズ数］
        seg_9 = specified_series_rule.trials_series

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

    if series_rule.turn_system == FROZEN_TURN:
        ts = '先後固定制'
    elif series_rule.turn_system == ALTERNATING_TURN:
        ts = '先後交互制'
    else:
        raise ValueError(f"{series_rule.turn_system=}")

    seg_3a = series_rule.shortest_coins
    seg_3b = series_rule.upper_limit_coins

    seg_4a = series_rule.step_table.get_step_by(face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
    seg_4b = series_rule.step_table.get_step_by(face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

    # ［目標の点数］
    seg_4c = series_rule.step_table.span

    text = ""
    #text += f"[{datetime.datetime.now()}]  "    # タイムスタンプ
    text += f"先手勝率 {seg_1:2.0f} ％ --調整--> {seg_1b:6.4f} ％ （± {seg_1c:>7.4f}）  対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点（先後固定制）"
    return text


def print_even_series_rule(p, best_p, best_p_error, series_rule):

    # 対局数
    if series_rule.turn_system == FROZEN_TURN:
        ts = '先後固定制'
    elif series_rule.turn_system == ALTERNATING_TURN:
        ts = '先後交互制'
    else:
        raise ValueError(f'{series_rule.turn_system=}')

    if series_rule.turn_system == ALTERNATING_TURN:
        # ［表が出る確率（％）］
        seg_1a = p*100

        # ［調整後の表が出る確率（％）］
        seg_1b = best_p * 100

        # ［調整後の表が出る確率（％）と 0.5 との誤差］
        seg_1c = best_p_error * 100
        
        seg_3a = series_rule.shortest_coins
        seg_3b = series_rule.upper_limit_coins

        seg_4a = series_rule.step_table.get_step_by(face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
        seg_4b = series_rule.step_table.get_step_by(face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

        # ［目標の点数］
        seg_4c = series_rule.step_table.span

        print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{series_rule.trials_series:6}シリーズ回    対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)
        return

    if series_rule.turn_system == FROZEN_TURN:
        # ［表が出る確率（％）］
        seg_1a = p*100

        # ［調整後の表が出る確率（％）］
        seg_1b = best_p * 100

        # ［調整後の表が出る確率（％）と 0.5 との誤差］
        seg_1c = best_p_error * 100

        # 対局数
        seg_3a = series_rule.shortest_coins
        seg_3b = series_rule.upper_limit_coins

        seg_4a = series_rule.step_table.get_step_by(face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
        seg_4b = series_rule.step_table.get_step_by(face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］

        # ［目標の点数］
        seg_4c = series_rule.step_table.span

        print(f"先手勝率：{seg_1a:2.0f} ％ --調整--> {seg_1b:>7.04f} ％（± {seg_1c:>7.04f}）  試行{series_rule.trials_series:6}シリーズ回    対局数 {seg_3a:>2}～{seg_3b:>2}（{ts}）    先手勝ち{seg_4a:2.0f}点、後手勝ち{seg_4b:2.0f}点　目標{seg_4c:3.0f}点", flush=True)
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

    h_step = series_rule.step_table.get_step_by(face_of_coin=HEAD)     # ［コインの表が出たときの勝ち点］
    t_step = series_rule.step_table.get_step_by(face_of_coin=TAIL)     # ［コインの裏が出たときの勝ち点］
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
            b_rest -= h_step
        
        # 裏石
        elif winner_color == TAIL:
            line_1_list.append('   o')
            w_rest -= t_step
        
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
    if trial_results_for_one_series.is_won(winner=HEAD):
        shw2 = "表"
    elif trial_results_for_one_series.is_won(winner=TAIL):
        shw2 = "裏"
    else:
        shw2 = "引"

    # ［Ａさんの勝率］
    # ---------------
    if trial_results_for_one_series.is_won(winner=HEAD):
        aw1 = "Ａさん"
    elif trial_results_for_one_series.is_won(winner=TAIL):
        aw1 = "Ｂさん"
    else:
        aw1 = "引"

    # 将棋の引分け
    # ------------
    d1 = failure_rate * 100    # ［将棋の引分け率］指定値

    # 対局数
    # ------
    tm10 = series_rule.shortest_coins  # ［最短対局数］理論値
    tm11 = series_rule.upper_limit_coins   # ［上限対局数］
    tm20 = trial_results_for_one_series.number_of_coins                            # ［対局数］実践値

    # 勝ち点構成
    # ---------
    pt1 = series_rule.step_table.get_step_by(face_of_coin=HEAD)    # ［コインの表が出たときの勝ち点］
    pt2 = series_rule.step_table.get_step_by(face_of_coin=TAIL)    # ［コインの裏が出たときの勝ち点］
    pt3 = series_rule.step_table.span      # ［目標の点数］


    return f"""\
[{time1                   }] １シリーズ    {ti1}
                                    将棋の先手勝ち  将棋の引分け  プレイヤー勝敗   シリーズ     | 勝ち点設定
                              指定   |    {shw1:2.0f} ％        {d1:2.0f} ％                        {tm10:>2}～{tm11:>2} 局   | {pt1:3.0f}表
                              試行後 |   {shw2}勝ち                   {aw1}勝ち        {tm20:>2}     局   | {pt2:3.0f}裏
                                                                                                | {pt3:3.0f}目
"""


def stringify_simulation_log(spec, series_rule, large_series_trial_summary, title):
    """シミュレーションのログの文言作成
    
    Parameters
    ----------
    spec : Specification
        ［仕様］
    series_rule : SeriesRule
        ［シリーズ・ルール］
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーションの結果
    title : str
        タイトル
    """

    # 変数名を短くする
    S = large_series_trial_summary  # Summary

    
    no_win_match_series_rate_ab = S.trial_no_win_match_series_rate()    # 試行した結果、［勝敗付かず］で終わったシリーズの割合
    succ_series_rate_ab = 1 - no_win_match_series_rate_ab               # 試行した結果、［勝敗が付いた］シリーズの割合


    # ヘッダー
    # --------
    time1 = datetime.datetime.now()     # ［タイムスタンプ］
    ti1 = title                         # タイトル


    # ［以下、指定したもの］
    # ---------------------
    a_shw1 = spec.p * 100                # ［将棋の先手勝率（％）］指定値
    a_d1 = spec.failure_rate * 100       # ［将棋の引分け率］指定値
    a_shl1 = (1 - spec.p) * 100          # ［将棋の後手勝率（％）］指定値
    a_sr0 = S.total      # 全シリーズ数

    # 全角文字の横幅は文字数を揃えること。全角文字の幅が半角のちょうど2倍ではないのでずれるので、書式設定の桁数を指定してもずれるから。
    if spec.turn_system == FROZEN_TURN:
        a_trn = "［先後固定制］上手と下手のように、Ａさんはずっと先手、Ｂさんはずっと後手"
    elif spec.turn_system == ALTERNATING_TURN:
        a_trn = "［先後交互制］Ａさんの先手、Ｂさんの後手で始まり、１局毎に先後を入替える"
    else:
        raise ValueError(f"{spec.turn_system=}")


    # ［以下、［かくきんシステム］が算出したシリーズ・ルール］
    # ---------------------------------------------------
    b_pt1 = series_rule.step_table.get_step_by(face_of_coin=HEAD)    # ［コインの表が出たときの勝ち点］
    b_pt2 = series_rule.step_table.get_step_by(face_of_coin=TAIL)    # ［コインの裏が出たときの勝ち点］
    b_pt3 = series_rule.step_table.span                                                     # ［目標の点数］
    b_tm10 = series_rule.shortest_coins                                            # ［最短対局数］
    b_tm11 = series_rule.upper_limit_coins                                             # ［上限対局数］


    # コインの表裏の回数
    # -----------------
    succ_a = S.won_rate(success_rate=1, winner=ALICE)             # 引分けを除いた［Ａさんが勝つ確率］実践値
    succ_ae = S.won_rate_error(success_rate=1, winner=ALICE)      # 引分けを除いた［Ａさんが勝つ確率と 0.5 との誤差］実践値
    succ_b = S.won_rate(success_rate=1, winner=BOB)             # 引分けを除いた［Ｂさんが勝つ確率］実践値
    succ_be = S.won_rate_error(success_rate=1, winner=BOB)      # 引分けを除いた［Ｂさんが勝つ確率と 0.5 との誤差］実践値

    c17 = S.no_wins     # コインの表も裏も出なかった


    # プレイヤーの勝敗数
    # -----------------
    a_wins = S.wins(winner=ALICE)
    b_wins = S.wins(winner=BOB)
    ab_total_wins = a_wins + b_wins
    ab_total_fully_wins = S.ful_wins(challenged=SUCCESSFUL, winner=ALICE) + S.ful_wins(challenged=SUCCESSFUL, winner=BOB) + S.ful_wins(challenged=FAILED, winner=ALICE) + S.ful_wins(challenged=FAILED, winner=BOB)
    ab_total_points_wins = S.pts_wins(challenged=SUCCESSFUL, winner=ALICE) + S.pts_wins(challenged=SUCCESSFUL, winner=BOB) + S.pts_wins(challenged=FAILED, winner=ALICE) + S.pts_wins(challenged=FAILED, winner=BOB)
    ab_total = ab_total_wins + S.no_wins

    ab152 = ab_total   # 全シリーズ計
    ab154 = ab_total_fully_wins   # 引分け無しのシリーズ
    ab157 = ab_total_points_wins + S.no_wins     # 引分けを含んだシリーズ

    ab162 = ab_total / ab_total * 100
    ab164 = ab_total_fully_wins / ab_total * 100
    ab167 = (ab_total_points_wins + S.no_wins) / ab_total * 100

    c101 = S.wins(winner=ALICE)                       # Ａさんの勝ちの総数
    c102 = S.wins(winner=BOB)                         # Ｂさんの勝ちの総数

    c103 = S.ful_wins(challenged=SUCCESSFUL, winner=ALICE)       # Ａさん満点勝ち
    c104 = S.ful_wins(challenged=SUCCESSFUL, winner=BOB)         # Ｂさん満点勝ち
    c103b = S.pts_wins(challenged=SUCCESSFUL, winner=ALICE)     # Ａさん判定勝ち（引分けがなければ零です）
    c104b = S.pts_wins(challenged=SUCCESSFUL, winner=BOB)     # Ｂさん判定勝ち（引分けがなければ零です）

    c105b = S.ful_wins(challenged=FAILED, winner=ALICE)       # Ａさん満点勝ち
    c106b = S.ful_wins(challenged=FAILED, winner=BOB)         # Ｂさん満点勝ち
    c105 = S.pts_wins(challenged=FAILED, winner=ALICE)     # Ａさん判定勝ち（引分けがなければ零です）
    c106 = S.pts_wins(challenged=FAILED, winner=BOB)     # Ｂさん判定勝ち（引分けがなければ零です）

    c107 = S.no_wins           # ＡさんもＢさんも勝ちではなかった

    ab71 = a_wins / ab_total_wins * 100           # 引分けを除いた［Ａさんが勝つ確率（％）］実践値
    ab72 = b_wins / ab_total_wins * 100           # 引分けを除いた［Ｂさんが勝つ確率（％）］実践値
    ab81 = (a_wins / ab_total_wins - 0.5) * 100         # 引分けを除いた［Ａさんが勝つ確率（％）と 0.5 との誤差］実践値
    ab82 = (b_wins / ab_total_wins - 0.5) * 100         # 引分けを除いた［Ｂさんが勝つ確率（％）と 0.5 との誤差］実践値

    ab41 = a_wins / ab_total * 100                    # ［表も裏も出なかった確率］も含んだ割合で、［Ａさんが勝つ確率］実践値（％）
    ab42 = b_wins / ab_total * 100                    # ［表も裏も出なかった確率］も含んだ割合で、［Ｂさんが勝つ確率］実践値（％）
    ab47 = S.no_wins / ab_total * 100                             # ［表も裏も出なかった確率］実践値（％）
    ab51 = (a_wins / ab_total - 0.5) * 100                   # 茣蓙の実践値（％）
    ab52 = (b_wins / ab_total - 0.5) * 100                   # 茣蓙の実践値（％）
    ab57 = (S.no_wins / ab_total - 0.5) * 100            # 茣蓙の実践値（％）

    # 対局数
    # ------
    tm_s = S.series_shortest_coins    # ［シリーズ最短対局数］実践値
    tm_l = S.series_longest_coins     # ［シリーズ最長対局数］

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
              |                                                                            表          {b_pt1:4.0f}点      --点 |{b_tm10:>4} ～{b_tm11:>4} 局 |
              |                                                                            裏          {b_pt2:4.0f}点      --点 |               |
              |                                                                          目標          {b_pt3:4.0f}点                 |               |
              +---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
              | 以下、［かくきんシステム］を使って試行                                                                                        |
              | 全シリーズ計                  | 引分け無しのシリーズ          | 引分けを含んだシリーズ                        | 対局数        |
              |                                 |                              |                                             |{tm_s:>4} ～{tm_l:>4} 局 |
              |                                   |                                  |                                                   |               |
              |                               |                               |                                               |               |
              | 先手勝ち      | 後手勝ち      |///////////////|///////////////|///////////////|///////////////| 勝敗付かず    |               |
              |                |                |///////////////|///////////////|///////////////|///////////////|   {c17:>8} 回 |               |
              |               |               | 先手満点勝ち  | 後手満点勝ち  | 先手点数勝ち  | 後手点数勝ち  |               | 対局数        |
              |               |               |              |               |              |               |               |               |
              |                                                                                                               |               |
    引分除く  |                                                                                                                |               |
              |                                                                                                                   |               |
              |                                                                                                               |               |
    引分込み  |                                                                                                                 |               |
              |                                                                                                              |               |
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


def stringify_csv_of_score_board_header(spec, series_rule):
    """スコアボードCSVヘッダー作成"""
    span = series_rule.step_table.span
    h_step = series_rule.step_table.get_step_by(face_of_coin=HEAD)
    t_step = series_rule.step_table.get_step_by(face_of_coin=TAIL)
    shortest_coins = series_rule.shortest_coins
    upper_limit_coins = series_rule.upper_limit_coins

    if h_step < 1:
        raise ValueError(f"正の整数でなければいけません {h_step=}")

    if t_step < 1:
        raise ValueError(f"正の整数でなければいけません {t_step=}")


    # NOTE 書式設定の桁指定は、文字数なので、文字幅が考慮されないので桁揃えできない。CSV形式にして Excel で閲覧すること
    str_p = str(spec.p * 100)
    str_failure_rate = str(spec.failure_rate * 100)
    str_turn_system = str(Converter.turn_system_to_code(spec.turn_system))
    str_h_step = str(h_step)
    str_t_step = str(t_step)
    str_span = str(span)
    str_shortest_coins = str(shortest_coins)
    str_upper_limit_coins = str(upper_limit_coins)


    # ヘッダー行作成
    header_row = ['Pattern', 'Category', 'Name', 'Value']

    for round in range(1,100):
        header_row.append(f"R{round}")

    str_header_row = ','.join(header_row)


    # CSV
    return f"""\
{str_header_row}

,,ヘッダー
,,--------

,,前提条件
,,--------
,,p,{str_p}
,,failure_rate,{str_failure_rate}
,,turn_system,{str_turn_system}

,,大会で設定するルール
,,-------------------
,,h_step,{str_h_step}
,,t_step,{str_t_step}
,,span,{str_span}
,,shortest_coins,{str_shortest_coins}
,,upper_limit_coins,{str_upper_limit_coins}


"""


def stringify_csv_of_score_board_body(scoreboard):
    """スコアボードCSVボディー作成"""

    if scoreboard.game_results == IN_GAME:
        raise ValueError(f"対局中なのはおかしい")
    
    elif scoreboard.game_results == ALICE_FULLY_WON:
        game_result_reason = "満点で"
        game_result = "Ａさんの勝ち"

    elif scoreboard.game_results == BOB_FULLY_WON:
        game_result_reason = "満点で"
        game_result = "Ｂさんの勝ち"

    elif scoreboard.game_results == ALICE_POINTS_WON:
        game_result_reason = "勝ち点差で"
        game_result = "Ａさんの勝ち"

    elif scoreboard.game_results == BOB_POINTS_WON:
        game_result_reason = "勝ち点差で"
        game_result = "Ｂさんの勝ち"
    
    elif scoreboard.game_results == NO_WIN_MATCH:
        game_result_reason = ""
        game_result = "勝者なし"

    else:
        raise ValueError(f"{scoreboard.game_results=}")
    

    # `[1, 2]` のようなデータを `1 2` に変換
    #source_data = f"{scoreboard._list_of_face_of_coin}"[1:-1].replace(',', ' ')

    # NOTE 書式設定の桁指定は、文字数なので、文字幅が考慮されないので桁揃えできない。CSV形式にして Excel で閲覧すること
    str_ptn = str(scoreboard.pattern_no)
    str_first_of_round_number = scoreboard.list_of_round_number_str[0]
    str_first_of_head_player = scoreboard.list_of_head_player_str[0]
    str_first_of_face_of_coin = scoreboard.list_of_face_of_coin_str[0]
    str_first_of_a_points = scoreboard.list_of_a_points_str[0]
    str_first_of_b_points = scoreboard.list_of_b_points_str[0]

    str_second_of_round_number = scoreboard.list_of_round_number_str[1]
    str_second_of_head_player = scoreboard.list_of_head_player_str[1]
    str_second_of_face_of_coin = scoreboard.list_of_face_of_coin_str[1]
    str_second_of_a_points = scoreboard.list_of_a_points_str[1]
    str_second_of_b_points = scoreboard.list_of_b_points_str[1]

    # ２つ目以降の要素は必ずあるだろう、という前提
    str_tail_of_round_number = ','.join([str(element) for element in scoreboard.list_of_round_number_str[2:]])
    str_tail_of_head_player = ','.join([str(element) for element in scoreboard.list_of_head_player_str[2:]])
    str_tail_of_face_of_coin = ','.join([str(element) for element in scoreboard.list_of_face_of_coin_str[2:]])
    str_tail_of_a_points = ','.join([str(element) for element in scoreboard.list_of_a_points_str[2:]])
    str_tail_of_b_points = ','.join([str(element) for element in scoreboard.list_of_b_points_str[2:]])


    #,元データ,{source_data}
    return f"""\
{str_ptn},スコアボード
{str_ptn},-----------

{str_ptn},,{str_first_of_round_number},{str_second_of_round_number},{str_tail_of_round_number}
{str_ptn},,{str_first_of_head_player},{str_second_of_head_player},{str_tail_of_head_player}
{str_ptn},,{str_first_of_face_of_coin},{str_second_of_face_of_coin},{str_tail_of_face_of_coin}
{str_ptn},,{str_first_of_a_points},{str_second_of_a_points},{str_tail_of_a_points}
{str_ptn},,{str_first_of_b_points},{str_second_of_b_points},{str_tail_of_b_points}

{str_ptn},,内容,{game_result_reason}
{str_ptn},,判定,{game_result}

"""
