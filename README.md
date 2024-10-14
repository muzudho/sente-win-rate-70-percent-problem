# sente-win-rate-70-percent-problem

先手勝率７０％問題を解決する方法の１つを提案します  

📖 [かくきんシステム ～Probabilistic Evenizing System～](./docs/takahashi_satoshi_system.md)  
📖 [用語集](./docs/terms.md)  


# 文字フォント

 文字フォントは `Cascadia Next JP ExtraLight` を使ってプログラミングしています

* 📖 [https://github.com/microsoft/cascadia-code/releases/tag/cascadia-next](https://github.com/microsoft/cascadia-code/releases/tag/cascadia-next)


# インポート

足りなかったら、インポートすること（使うとは限りません）  

```
python -m pip install scipy
python -m pip install pandas
```


# プログラムの使い方

👇 `automatic` は、並行処理できるように改造中です。ターミナルを複数個開けてログを見ながら起動してください。完了するものもあれば、無限ループしているものもあります。  

```shell
python step_oa12o0_automatic_all_epdt.py
python step_oa13o0_automatic_all_epdt.py
python step_oa21o0_automatic_tp.py
python step_oa22o0_automatic_tpr.py
python step_oa23o0_automatic_tpb.py
python step_oa31o0_automatic_kds.py
python step_oa32o0_automatic_kdwb.py
```


## create_a_csv_to_data_score_board.py

```shell
python create_a_csv_to_data_score_board.py
```

以下の csvファイルを生成します  

* 📄 `temp/score_board/data_alter_p50.0_f0.0.csv` - ファイル名は一部変わります。 **理論値** のデータです


## create_a_csv_to_data_score_board_best.py

```shell
python create_a_csv_to_data_score_board_best.py
```

以下のファイルを入力に使います。  

* 📄 `temp/score_board/data_alter_p50.0_f0.0.csv` - ファイル名は一部変わります。 **理論値** のデータです

理論値をマージします  

以下の csvファイルを生成します  

* 📄 `reports/score_board_data_best.csv` - **理論値** をマージしたデータです


## step_o1o0_automatic.py

`step_o1o0_automatic.py` は、 `step_o2o0_automatic.py` と並行して動かすことができますが、 `step_o3o0_automatic.py` とは並行して動かしてはいけません  

```shell
python step_o1o0_automatic.py
```

入力は以下の３つです。  

* ［コインの表も裏も出ない確率］
* ［先後の決め方］
* ［試行シリーズ数］

入力を元に **試行** します。  

以下の csvファイルを生成します  

* 📄 `temp/kakukin_data_sheet/KDS_alter_f0.0_try2000.csv` - ファイル名は一部変わります。 **試行** の結果のデータです


## step_o2o0_automatic.py

`step_o2o0_automatic.py` は、 `step_o1o0_automatic.py` と並行して動かすことができますが、 `step_o3o0_automatic.py` とは並行して動かしてはいけません  

```shell
python step_o2o0_automatic.py
```

以下の csvファイルを生成します  

* 📄 `temp/theoretical_probability/TP_alter_p50.0_f0.0.csv` - ファイル名は一部変わります。 **理論値** の算出データです


## step_o3o0_automatic.py

`step_o3o0_automatic.py` は、 `step_o1o0_automatic.py` や `step_o2o0_automatic.py` とは並行して動かしてはいけません  

```shell
python step_o3o0_automatic.py
```

以下のファイルを入力に使います。  

* 📄 `temp/kakukin_data_sheet/KDS_alter_f0.0_try2000.csv` - ファイル名は一部変わります。 **試行** の結果のデータです

最終的な成果物は、以下の３つの Excel ファイル  

* 📄 `reports/auto_generated_kakukin_data_alter_try2000.xlsx`
* 📄 `reports/auto_generated_kakukin_data_froze_try2000.xlsx`
* 📄 `reports/kakukin_viewer.xlsx`


# 参考

* 📖 [リナンバリンギスト番号](https://note.com/muzudho/n/n3090e6c0622c) - `o1o0` のような表記の解説
* 📖 [光学技術の基礎用語 ＞ 確率の英語表現](https://www.optics-words.com/english_for_science/probability.html) - 確率の英語表現一覧
* 📖 [Excel で CSV UTF-8 ファイルを正しく開く](https://support.microsoft.com/ja-jp/office/excel-%E3%81%A7-csv-utf-8-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E6%AD%A3%E3%81%97%E3%81%8F%E9%96%8B%E3%81%8F-8a935af5-3416-4edd-ba7e-3dfd2bc4a032)
* 📖 [半導体の製造 ＞ 正確度と精度](https://www.hitachi-hightech.com/jp/ja/knowledge/semiconductor/room/manufacturing/accuracy-precision.html) - precision と accuracy の違い
* 📖 [プログラミングにおける数値計算はワナがいっぱい](https://qiita.com/papi_tokei/items/37a4e31949ba8efb6897) - 割り算には Fraction を使うと正確だが 17倍ぐらい計算が遅くなってしまう
