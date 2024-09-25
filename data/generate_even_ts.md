# 均等データの生成

* `p` - ［表が出る確率］ 初期値は 0.50 ～ 0.99
* `failure_rate` - ［表も裏もでない確率］ 初期値は 0.0
* `best_p` - ［調整後の表が出る確率］ 初期値は 0
* `best_p_error` - ［調整後の表が出る確率の 0.5 からの差の絶対値］ 初期値は 0.51
* `best_number_of_series` - 対局回数。初期値は 2000000
* `best_b_step` - ［表勝ち１つの点数］ 初期値は 0
* `best_w_step` - ［裏勝ち１つの点数］ 初期値は 1
* `best_span` - ［目標の点数］ 初期値は 1
* `latest_p` - 探索の最後。初期値は 0
* `latest_p_error` - 探索の最後。初期値は 0.51
* `latest_number_of_series` - 探索の最後。初期値は 2000000
* `latest_b_step` - 探索の最後。初期値は 0
* `latest_w_step` - 探索の最後。初期値は 1
* `latest_span` - 探索の最後。初期値は 1
* `process` - 計算過程を文字列で記述します。初期値は "" ですが、 pandas では警告が出るようです
