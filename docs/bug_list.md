# おかしい

 `0.014715 10表 12裏 14目 1～1局（先後交互制）`
Ａでも 4目残る ---> h_time と t_time を間違えていたので修正


# 2024-09-20

`0.014715 10表 12裏 14目 1～1局（先後固定制）`

裏裏で最長２局では？  

間違い： `表があと１つで勝てるところで止まり、裏が全勝したときの回数と同じ`
修正　： `裏があと１つで勝てるところで止まり、表が全勝したときの回数と同じ`

h_time, t_time 四捨五入していたので、切り上げに変更


## 先手勝率６６％のケース

同様に、もう１例確かめてみましょう。 `先手勝率 66 ％` の行を見てください。  

当システムを使うと、ゲームの先手勝率の偏りを `54.1061 ％` まで調整できます。５割との差は `（ +4.1061）` です。  

`先手勝ち  1点、後手勝ち  2点、目標  7点` と書いてあるのが、先手と後手ごとに異なる勝ち点と、目標の点数です。  

`5～ 10局（先後固定制）` と書いてあるのは、先後固定制で、最短で 5 局、最長で 10 局ということです。  
FIXME 最短のケースは、後手が 4 連勝して終わりです。  
最長のケースは、先手が 6 勝で止まり、後手が 4 勝して勝ったか、後手が 3 勝で止まり、先手が 7 勝したケースです。  


## 先後交互制での上限対局数

[2024-09-21 14:41:22.260125]  先手勝率 56 ％ --先後固定制-->  46.1673 ％（±  3.8326）    先手勝ち数 923347／2000000対局試行    対局数  3～ 6  先手勝ち 3点、後手勝ち 4点　目標 12点    むずでょセレクション
                                                                                                                           実際    3～ 6
                                            --先後交互制-->  51.4864 ％（±  1.4864）    Ａ氏勝ち数1029729／2000000対局試行    対局数  4～ 6
                                                                                                                           実際    4～ 7

# 2024-10-02 両者が満点バグ

```
[unexpected error] err=ValueError("両者が満点はおかしい ----> カウントダウン式になっているのを忘れていた

           ,  S,   1,   2,  3,   4
    表番   ,   ,   A,   B,  A,   B
    出目   ,   ,  表,  表,  裏,  裏
    Ａさん ,  3,   2,   2,   2,  0
    Ｂさん ,  3,   3,   2,   0,  0
    span=3"


         type(err)=<class 'ValueError'>
Traceback (most recent call last):
  File "C:\Users\muzud\OneDrive\ドキュメント\GitHub\sente-win-rate-70-percent-problem\create_a_csv_to_data_score_board.py", line 191, in <module>
    is_terminated = automatic(turn_system=turn_system, failure_rate=failure_rate, p=p)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\muzud\OneDrive\ドキュメント\GitHub\sente-win-rate-70-percent-problem\create_a_csv_to_data_score_board.py", line 133, in automatic
    a_win_rate, b_win_rate, no_win_match_rate, all_patterns_p = search_all_score_boards(
                                                                ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\muzud\OneDrive\ドキュメント\GitHub\sente-win-rate-70-percent-problem\library\score_board.py", line 83, in search_all_score_boards
    score_board = ScoreBoard.make_score_board(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\muzud\OneDrive\ドキュメント\GitHub\sente-win-rate-70-percent-problem\library\__init__.py", line 2161, in make_score_board
    raise ValueError(f"両者が満点はおかしい {list_of_round_number_str=}  {list_of_head_player_str=}  {list_of_face_of_coin_str=}  {list_of_a_count_down_points_str=}  {list_of_b_count_down_points_str=}  {span=}")
ValueError: 両者が満点はおかしい list_of_round_number_str=['', 'S', 1, 2, 3, 4]  list_of_head_player_str=['表番', '', 'A', 'B', 'A', 'B']  list_of_face_of_coin_str=['出目', '', '表', '表', '裏', '裏']  list_of_a_count_down_points_str=['Ａさん', 3, 2, 2, 2, 0]  list_of_b_count_down_points_str=['Ｂさん', 3, 3, 2, 0, 0]  span=3
```


# 2024-10-02 14:47 両者が満点バグ

* [x] ［先後固定制］なのに、表番が入れ替わってる ----> 修正

```
[unexpected error] err=ValueError("両者が満点はおかしい list_of_round_number_str=[
  
           ,   S,    1,   2,   3,   4   list_of_head_player_str=[
    表番   ,    ,    A,   B,   A,   B   list_of_face_of_coin_str=[
    出目   ,    ,   表,  表,   裏,  裏   list_of_a_count_down_points_str=[
    Ａさん ,   3,    2,   2,   2,   0   list_of_b_count_down_points_str=[
    Ｂさん ,   3,    3,   2,   0,   0 
    
    spec.p=0.51
    spec.failure_rate=0.05
    spec.turn_system=frozen
    span=3
    t_step=2
    h_step=1
Traceback (most recent call last):
```
