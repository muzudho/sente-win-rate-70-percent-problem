import datetime


def write_coin_toss_log(output_file_path, black_win_rate, b_require, w_require, round_total, black_wons):
    """ログ出力
    
    Parameters
    ----------
    output_file_path : str
        出力先ファイルへのパス
    black_win_rate : float
        黒が出る確率（先手勝率）
    b_require : int
        先手の何本先取制
    w_require : int
        後手の何本先取制
    round_total : int
        対局数
    black_wons : int
        黒が勝った回数
    """
    with open(output_file_path, 'a', encoding='utf8') as f:

        # 先後交代なし（Freeze-turn）方式のときの［最長対局数］
        #
        #   NOTE 例えば３本勝負というとき、２本取れば勝ち。最大３本勝負という感じ。３本取るゲームではない。先後非対称のとき、白と黒は何本取ればいいのか明示しなければ、伝わらない
        #
        max_number_of_bout_in_freeze_turn = (b_require-1) + (w_require-1) + 1

        # 黒が勝った確率
        black_won_rate = black_wons / round_total

        # 均等からの誤差
        error = abs(black_won_rate - 0.5)

        text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％ --調整後--> 先手が勝った確率{black_won_rate*100:8.4f} ％（± {error*100:7.4f}）  {max_number_of_bout_in_freeze_turn:2}本勝負（ただし、{b_require:>3}本先取制）  先手勝ち数{black_wons:7}／{round_total:7}対局試行"
        print(text) # 表示
        f.write(f"{text}\n")    # ファイルへ出力
