import datetime


def write_coin_toss_log(output_file_path, black_win_rate, b_point, w_point, round_total, black_wons):
    """ログ出力
    
    Parameters
    ----------
    output_file_path : str
        出力先ファイルへのパス
    black_win_rate : float
        黒が出る確率（先手勝率）
    b_point : int
        先手の何本先取制
    w_point : int
        後手の何本先取制
    round_total : int
        対局数
    black_wons : int
        黒が勝った回数
    """
    with open(output_file_path, 'a', encoding='utf8') as f:
        # 文言作成
        # -------

        # 黒が勝った確率
        black_won_rate = black_wons / round_total

        # 均等からの誤差
        error = abs(black_won_rate - 0.5)

        # 後手が最初からｎ本持つアドバンテージがあるという表記
        w_advantage = b_point - w_point

        text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％ --調整後--> 先手が勝った確率{black_won_rate*100:8.4f} ％（± {error*100:7.4f}）  {b_point:2}本勝負（後手は最初から{w_advantage:2}本もつアドバンテージ）  先手勝ち数{black_wons:7}／{round_total:7}対局試行"
        print(text) # 表示
        f.write(f"{text}\n")    # ファイルへ出力
