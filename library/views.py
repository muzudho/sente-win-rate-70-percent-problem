import datetime
import re

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, FACE_OF_COIN, PLAYERS, IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Converter, SeriesRule, Candidate


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

    if series_rule.turn_system_id == FROZEN_TURN:
        ts = '先後固定制'
    elif series_rule.turn_system_id == ALTERNATING_TURN:
        ts = '先後交互制'
    else:
        raise ValueError(f"{series_rule.turn_system_id=}")

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


def stringify_series_log(
        p, failure_rate, series_rule, trial_results_for_one_series, title, turn_system_id):
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

    for winner_color in trial_results_for_one_series.path_of_face_of_coin:
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
    if spec.turn_system_id == FROZEN_TURN:
        a_trn = "［先後固定制］上手と下手のように、Ａさんはずっと先手、Ｂさんはずっと後手"
    elif spec.turn_system_id == ALTERNATING_TURN:
        a_trn = "［先後交互制］Ａさんの先手、Ｂさんの後手で始まり、１局毎に先後を入替える"
    else:
        raise ValueError(f"{spec.turn_system_id=}")


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


#############
# Score board
#############

class ScoreBoardViewData():
    """スコアボード・ビューデータ"""


    def __init__(self, path_of_round_number_str, path_of_head_player_str, path_of_face_of_coin_str, path_of_a_count_down_points_str, path_of_b_count_down_points_str):
        """初期化

        Parameters
        ----------
        path_of_round_number_str : list
            スコアボードのラウンド番号の行
        path_of_head_player_str : list
            スコアボードの表番の行
        path_of_face_of_coin_str : list
            スコアボードの出目の行
        path_of_a_count_down_points_str : list
            スコアボードのＡさんの行
        path_of_b_count_down_points_str : list
            スコアボードのＢさんの行
        """
        self._path_of_round_number_str = path_of_round_number_str
        self._path_of_head_player_str = path_of_head_player_str
        self._path_of_face_of_coin_str = path_of_face_of_coin_str
        self._path_of_a_count_down_points_str = path_of_a_count_down_points_str
        self._path_of_b_count_down_points_str = path_of_b_count_down_points_str


    @staticmethod
    def from_data(score_board_data):

        # NOTE 書式設定の桁指定は、文字数なので、文字幅が考慮されないので桁揃えできない。CSV形式にして Excel で閲覧すること
        path_of_round_number_str = ['']
        path_of_head_player_str = ['表番']
        path_of_face_of_coin_str = ['出目']
        path_of_a_count_down_points_str = ['Ａさん']
        path_of_b_count_down_points_str = ['Ｂさん']


        for round in score_board_data.round_list:
            path_of_round_number_str.append(round[0])
            path_of_head_player_str.append(round[1])
            path_of_face_of_coin_str.append(round[2])
            path_of_a_count_down_points_str.append(round[3])
            path_of_b_count_down_points_str.append(round[4])


        return ScoreBoardViewData(
                path_of_round_number_str=path_of_round_number_str,
                path_of_head_player_str=path_of_head_player_str,
                path_of_face_of_coin_str=path_of_face_of_coin_str,
                path_of_a_count_down_points_str=path_of_a_count_down_points_str,
                path_of_b_count_down_points_str=path_of_b_count_down_points_str)


    @property
    def path_of_round_number_str(self):
        """スコアボードのラウンド番号の行"""
        return self._path_of_round_number_str


    @property
    def path_of_head_player_str(self):
        """スコアボードの表番の行"""
        return self._path_of_head_player_str


    @property
    def path_of_face_of_coin_str(self):
        """スコアボードの出目の行"""
        return self._path_of_face_of_coin_str


    @property
    def path_of_a_count_down_points_str(self):
        """スコアボードのＡさんの行"""
        return self._path_of_a_count_down_points_str


    @property
    def path_of_b_count_down_points_str(self):
        """スコアボードのＢさんの行"""
        return self._path_of_b_count_down_points_str


def stringify_csv_of_score_board_view_header(spec, series_rule):
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
    str_turn_system = str(Converter.turn_system_id_to_name(spec.turn_system_id))
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
,,turn_system_name,{str_turn_system}

,,大会で設定するルール
,,-------------------
,,h_step,{str_h_step}
,,t_step,{str_t_step}
,,span,{str_span}
,,shortest_coins,{str_shortest_coins}
,,upper_limit_coins,{str_upper_limit_coins}


"""


def stringify_csv_of_score_board_view_body(score_board):
    """スコアボードCSVボディー作成"""

    if score_board.game_results == IN_GAME:
        raise ValueError(f"対局中なのはおかしい")
    
    elif score_board.game_results == ALICE_FULLY_WON:
        game_result_reason = "満点で"
        game_result = "Ａさんの勝ち"

    elif score_board.game_results == BOB_FULLY_WON:
        game_result_reason = "満点で"
        game_result = "Ｂさんの勝ち"

    elif score_board.game_results == ALICE_POINTS_WON:
        game_result_reason = "勝ち点差で"
        game_result = "Ａさんの勝ち"

    elif score_board.game_results == BOB_POINTS_WON:
        game_result_reason = "勝ち点差で"
        game_result = "Ｂさんの勝ち"
    
    elif score_board.game_results == NO_WIN_MATCH:
        game_result_reason = ""
        game_result = "勝者なし"

    else:
        raise ValueError(f"{score_board.game_results=}")
    

    # `[1, 2]` のようなデータを `1 2` に変換
    #source_data = f"{score_board._path_of_face_of_coin}"[1:-1].replace(',', ' ')

    # NOTE 書式設定の桁指定は、文字数なので、文字幅が考慮されないので桁揃えできない。CSV形式にして Excel で閲覧すること
    str_ptn = str(score_board.pattern_no)
    str_pattern_p = str(score_board.pattern_p)


    score_board_view_data = ScoreBoardViewData.from_data(score_board)

    str_first_of_round_number = score_board_view_data.path_of_round_number_str[0]
    str_first_of_head_player = score_board_view_data.path_of_head_player_str[0]
    str_first_of_face_of_coin = score_board_view_data.path_of_face_of_coin_str[0]
    str_first_of_a_points = score_board_view_data.path_of_a_count_down_points_str[0]
    str_first_of_b_points = score_board_view_data.path_of_b_count_down_points_str[0]

    str_second_of_round_number = score_board_view_data.path_of_round_number_str[1]
    str_second_of_head_player = score_board_view_data.path_of_head_player_str[1]
    str_second_of_face_of_coin = score_board_view_data.path_of_face_of_coin_str[1]
    str_second_of_a_points = score_board_view_data.path_of_a_count_down_points_str[1]
    str_second_of_b_points = score_board_view_data.path_of_b_count_down_points_str[1]

    # ２つ目以降の要素は必ずあるだろう、という前提
    str_tail_of_round_number = ','.join([str(element) for element in score_board_view_data.path_of_round_number_str[2:]])
    str_tail_of_head_player = ','.join([str(element) for element in score_board_view_data.path_of_head_player_str[2:]])
    str_tail_of_face_of_coin = ','.join([str(element) for element in score_board_view_data.path_of_face_of_coin_str[2:]])
    str_tail_of_a_points = ','.join([str(element) for element in score_board_view_data.path_of_a_count_down_points_str[2:]])
    str_tail_of_b_points = ','.join([str(element) for element in score_board_view_data.path_of_b_count_down_points_str[2:]])


    #,元データ,{source_data}
    return f"""\
{str_ptn},スコアボード
{str_ptn},-----------
{str_ptn},,確率,{str_pattern_p}

{str_ptn},,{str_first_of_round_number},{str_second_of_round_number},{str_tail_of_round_number}
{str_ptn},,{str_first_of_head_player},{str_second_of_head_player},{str_tail_of_head_player}
{str_ptn},,{str_first_of_face_of_coin},{str_second_of_face_of_coin},{str_tail_of_face_of_coin}
{str_ptn},,{str_first_of_a_points},{str_second_of_a_points},{str_tail_of_a_points}
{str_ptn},,{str_first_of_b_points},{str_second_of_b_points},{str_tail_of_b_points}

{str_ptn},,内容,{game_result_reason}
{str_ptn},,判定,{game_result}

"""


def stringify_csv_of_score_board_view_footer(three_rates, all_patterns_p):
    """スコアボードCSVフッター作成"""

    return f"""\

,フッター
,--------
,,Ａさんの勝率,{three_rates.a_win_rate}
,,Ｂさんの勝率,{three_rates.b_win_rate}
,,勝ち負けが付かない確率,{three_rates.no_win_match_rate}
,,確率合計,{all_patterns_p}
"""


class KakukinDataSheetTableCsv():
    """Excel の［かくきんビューワー］"""


    def stringify_header():
        """\
        データの構造
        +------------------------------------------------+---------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Specification                                  | Series rule                                                               | Large Series Trial Summary                                                                                                                                                                                                                              |
        | 前提条件                                        | 大会のルール設定                                                           | シミュレーション結果                                                                                                                                                                                                                                      |
        +---------------+------------------+-------------+-------------+-------------+-----------+---------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | p             | failure_rate     | turn_system_name | h_step   | t_step   | span     | shortest_coins | upper_limit_coins | trial_series    series_shortest_coins  series_longest_coins                                                                                                                                                                                            |
        | 将棋の先手勝率 | 将棋の引分け率    | 先後の決め方 | 先手で勝った  | 後手で勝った | シリーズ  | 最短対局数     | 上限対局数         | 試行シリーズ総数  シリーズ最短対局数      シリーズ最長対局数                                                                                                                                                                                                 |
        | ％            | ％               |             | ときの勝ち点  | ときの勝ち点 | 勝利条件  |               |                   |                                                                                            ______________________________________________________________________________________________________________________________________________________________|
        |               |                  |             |              |             |          |               |                   |                                                                                           | succucessful_series                                                   | failed_series                                                                       |
        |               |                  |             |              |             |          |               |                   |                                                                                           | 引分けが起こらなかったシリーズ数                                         | 引分けが含まれたシリーズ数                                                            |
        |               |                  |             |              |             |          |               |                   |                                                                総数                       |                                                                       |                                                                                      |
        |               |                  |             |              |             |          |               |                   |                                                                ___________________________|                                                                       |                                                                        _____________|
        |               |                  |             |              |             |          |               |                   |                                                               | wins_a      | wins_b      |                                                                       |                                                                        | no_wins_ab |
        |               |                  |             |              |             |          |               |                   |                                                               | Ａさんの勝ち | Ｂさんの勝ち |             勝利条件達成                   点数差による判定勝ち          |             勝利条件達成                   点数差による判定勝ち           | 勝敗付かず  |
        |               |                  |             |              |             |          |               |                   |                                                               | シリーズ数   | シリーズ数   |            ___________________________________________________________|           _____________________________________________________________| シリーズ数  |
        |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | s_ful_wins_a | s_ful_wins_b | s_pts_wins_a | s_pts_wins_b |           | f_ful_wins_a  | f_ful_wins_b | f_pts_wins_a | f_pts_wins_b |            |
        |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | Ａさんの勝ち  | Ｂさんの勝ち  | Ａさんの勝ち  | Ｂさんの勝ち  |            | Ａさんの勝ち  | Ｂさんの勝ち  | Ａさんの勝ち  | Ｂさんの勝ち  |             |
        |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | シリーズ数    | シリーズ数    | シリーズ数    | シリーズ数    |           | シリーズ数    | シリーズ数    | シリーズ数    | シリーズ数    |             |
        |               |                  |             |              |             |          |               |                   |                                                               |             |             |           |              |              |              |              |            |              |              |              |              |             |
        +---------------+------------------+-------------+--------------+-------------+----------+---------------+-------------------+---------------------------------------------------------------+-------------+-------------+-----------+--------------+--------------+--------------+--------------+------------+--------------+--------------+--------------+--------------+-------------+
        """

        # CSV
        return f"p,failure_rate,turn_system_name,h_step,t_step,span,shortest_coins,upper_limit_coins,trial_series,series_shortest_coins,series_longest_coins,wins_a,wins_b,succucessful_series,s_ful_wins_a,s_ful_wins_b,s_pts_wins_a,s_pts_wins_b,failed_series,f_ful_wins_a,f_ful_wins_b,f_pts_wins_a,f_pts_wins_b,no_wins_ab"


    def stringify_csv_of_body(spec, theoretical_series_rule, presentable, comment, large_series_trial_summary):
        """データ部を文字列化

        TODO 廃止方針

        Parameters
        ----------
        spec : Specification
            ［仕様］
        theoretical_series_rule : SeriesRule
            理論値の［シリーズ・ルール］
        """

        # 変数名を縮める（Summary）
        S = large_series_trial_summary


        s_wins_a = S.wins(challenged=SUCCESSFUL, winner=ALICE)
        f_wins_a = S.wins(challenged=FAILED, winner=ALICE)
        s_wins_b = S.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_b = S.wins(challenged=FAILED, winner=BOB)


        # ［前提条件］
        str_p = f"{spec.p*100:.4f}"                                                 # ［将棋の先手勝率］ p （Probability）
        str_failure_rate = f"{spec.failure_rate*100:.4f}"                           # ［将棋の引分け率］
        str_turn_system = f"{Converter.turn_system_id_to_name(spec.turn_system_id)}"      # ［手番の決め方］

        # ［大会のルール設定］
        # TODO ここは理論値を入れたい
        str_head_step = f"{theoretical_series_rule.step_table.get_step_by(face_of_coin=HEAD)}"  # ［先手で勝ったときの勝ち点］
        str_tail_step = f"{theoretical_series_rule.step_table.get_step_by(face_of_coin=TAIL)}"  # ［後手で勝ったときの勝ち点］
        str_span = f"{theoretical_series_rule.step_table.span}"                                 # ［シリーズ勝利条件］
        str_shortest_coins = f"{theoretical_series_rule.shortest_coins}"                        # ［最短対局数］
        str_upper_limit_coins = f"{theoretical_series_rule.upper_limit_coins}"                  # ［上限対局数］
                                                                                    # NOTE ルール設定を求めたときの試行回数も記録しようかと思ったが、作り方についてそんなに信用できる記録でもないので止めた

        # ［シミュレーション結果］
        str_trial_series = f"{S.total}"                                             # ［試行シリーズ総数］
        str_series_shortest_coins = f"{S.series_shortest_coins}"                    # ［シリーズ最短局数］
        str_series_longest_coins = f"{S.series_longest_coins}"                      # ［シリーズ最長局数］
        str_wins_a = f"{s_wins_a + f_wins_a}"                                       # ［Ａさんの勝ちシリーズ数］
        str_wins_b = f"{s_wins_b + f_wins_b}"                                       # ［Ｂさんの勝ちシリーズ数］
        str_succucessful_series = f"{S.successful_series}"                          # ［引分けが起こらなかったシリーズ数］
        str_s_ful_wins_a = f"{S.ful_wins(challenged=SUCCESSFUL, winner=ALICE)}"     # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ａさんの勝ち］
        str_s_ful_wins_b = f"{S.ful_wins(challenged=SUCCESSFUL, winner=BOB)}"       # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ｂさんの勝ち］
        str_s_pts_wins_a = f"{S.pts_wins(challenged=SUCCESSFUL, winner=ALICE)}"     # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
        str_s_pts_wins_b = f"{S.pts_wins(challenged=SUCCESSFUL, winner=BOB)}"       # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
        str_failed_series = f"{S.failed_series}"                                    # ［引分けが含まれたシリーズ数］
        str_f_ful_wins_a = f"{S.ful_wins(challenged=FAILED, winner=ALICE)}"         # ［引分けが含まれたシリーズ＞勝利条件達成＞Ａさんの勝ち］
        str_f_ful_wins_b = f"{S.ful_wins(challenged=FAILED, winner=BOB)}"           # ［引分けが含まれたシリーズ＞勝利条件達成＞Ｂさんの勝ち］
        str_f_pts_wins_a = f"{S.pts_wins(challenged=FAILED, winner=ALICE)}"         # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
        str_f_pts_wins_b = f"{S.pts_wins(challenged=FAILED, winner=BOB)}"           # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
        str_no_wins_ab = f"{S.no_wins}"                                             # ［勝敗付かずシリーズ数］


        # CSV
        return f"{str_p},{str_failure_rate},{str_turn_system},{str_head_step},{str_tail_step},{str_span},{str_shortest_coins},{str_upper_limit_coins},{str_trial_series},{str_series_shortest_coins},{str_series_longest_coins},{str_wins_a},{str_wins_b},{str_succucessful_series},{str_s_ful_wins_a},{str_s_ful_wins_b},{str_s_pts_wins_a},{str_s_pts_wins_b},{str_failed_series},{str_f_ful_wins_a},{str_f_ful_wins_b},{str_f_pts_wins_a},{str_f_pts_wins_b},{str_no_wins_ab}"


class PromptCatalog():
    """プロンプト・カタログ"""


    @staticmethod
    def how_many_times_do_you_want_to_try_the_series():
        """シリーズを何回試行するか？　つまり［試行シリーズ数］を尋ねます"""
        prompt = f"""\

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

例：
Example: 3

シリーズを何回試行しますか？
How many times do you want to try the series(0-6)? """
        precision = int(input(prompt))
        specified_trial_series = Converter.precision_to_trial_series(precision)
        specified_abs_small_error = Converter.precision_to_small_error(precision)

        return specified_trial_series, specified_abs_small_error


    @staticmethod
    def which_method_do_you_use_to_determine_sente_and_gote():
        """［対局者が先手と後手のどちらの番になるかの決め方］をどちらの方法にするか？　つまり［先後の決め方］を尋ねます"""
        prompt = f"""\

先後固定制
(1) Frozen turn

先後交互制
(2) Alternating turn

［対局者が先手と後手のどちらの番になるかの決め方］をどちらの方法にしますか？　つまり［先後の決め方］はどちらにしますか？
Which method do you use to determine sente and gote(1-2)? """
        choice = input(prompt)

        if choice == '1':
            specified_turn_system_id = FROZEN_TURN

        elif choice == '2':
            specified_turn_system_id = ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")
    
        return specified_turn_system_id


    @staticmethod
    def what_is_the_failure_rate():
        """［コインを投げて表も裏も出ない確率］をいくらにするか、つまり［将棋の引分け率］を尋ねます"""
        prompt = f"""\

Example: 10% is 0.1

［コインを投げて表も裏も出ない確率］はいくらにしますか？　つまり［将棋の引分け率］はいくらにしますか？
What is the failure rate? """
        specified_failure_rate = float(input(prompt))

        return specified_failure_rate


    @staticmethod
    def what_is_the_probability_of_flipping_a_coin_and_getting_heads():
        """［コインを投げて表が出る確率］はいくらにするか？　つまり［将棋の先手勝率］を尋ねます"""
        prompt = f"""\

Example: 70% is 0.7

［コインを投げて表が出る確率］はいくらにしますか？　つまり［将棋の先手勝率］はいくらにしますか？
What is the probability of flipping a coin and getting heads? """
        specified_p = float(input(prompt))

        return specified_p


    @staticmethod
    def how_many_goal_win_points():
        """［目標の点数］をいくつにするか？　つまり［目標の点数］を尋ねます"""
        prompt = f"""\

Example: 6

［目標の点数］はいくつにしますか？
How many goal win points? """
        specified_span = int(input(prompt))

        return specified_span


    @staticmethod
    def how_many_win_points_of_tail_of_coin():
        """［後手で勝ったときの勝ち点］をいくつにするか？　つまり［後手で勝ったときの勝ち点］を尋ねます"""
        prompt = f"""\

Example: 3

［後手で勝ったときの勝ち点］はいくつにしますか？
How many win points of tail of coin? """
        specified_t_step = int(input(prompt))

        return specified_t_step


    @staticmethod
    def how_many_win_points_of_head_of_coin():
        """［先手で勝ったときの勝ち点］をいくつにするか？　つまり［先手で勝ったときの勝ち点］を尋ねます"""
        prompt = f"""\

Example: 2
How many win points of head of coin? """
        specified_h_step = int(input(prompt))

        return specified_h_step
