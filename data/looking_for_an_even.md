# 均等を探す

コイントスをシミュレーションして、力業で先後の勝率が均等になるような h_time, t_time を探しています。  
h_time と t_time 同士は同じ比でも、桁が多いと精度が上がるようです。  

* `p` - 表が出る確率
* `h_time` - 表(Black)を選んだ側が勝つのに必要な、［表勝ちだけでの対局数］
* `t_time` - 裏(White)を選んだ側が勝つのに必要な、［裏勝ちだけでの対局数］
