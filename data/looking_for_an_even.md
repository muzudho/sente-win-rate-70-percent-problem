# 均等を探す

コイントスをシミュレーションして、力業で先後の勝率が均等になるような b_repeat_when_frozen_turn, w_repeat_when_frozen_turn を探しています。  
b_repeat_when_frozen_turn と w_repeat_when_frozen_turn 同士は同じ比でも、桁が多いと精度が上がるようです。  

* `p` - 表が出る確率
* `b_repeat_when_frozen_turn` - 表(Black)を選んだ側が勝つのに必要な、表が先取する本数
* `w_repeat_when_frozen_turn` - 裏(White)を選んだ側が勝つのに必要な、裏が先取する本数
