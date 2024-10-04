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

## automatic_no1.py

```
python automatic_no1.py
```

入力は以下の３つです。  

* ［コインの表も裏も出ない確率］
* ［先後の決め方］
* ［試行シリーズ数］

入力を元にシミュレーションします。  

以下の csvファイルを生成します  

* 📄 `temp/kakukin_data_sheet/KDS_alter_f0.0_try2000.csv` - ファイル名は一部変わります


## automatic_no2.py

```
python automatic_no2.py
```

以下のファイルを入力に使います。  

* 📄 `temp/kakukin_data_sheet/KDS_alter_f0.0_try2000.csv` - ファイル名は一部変わります

最終的な成果物は、以下の３つの Excel ファイル  

* 📄 `reports/auto_generated_kakukin_data_alter_try2000.xlsx`
* 📄 `reports/auto_generated_kakukin_data_froze_try2000.xlsx`
* 📄 `reports/kakukin_viewer.xlsx`


# 参考

* 📖 [光学技術の基礎用語 ＞ 確率の英語表現](https://www.optics-words.com/english_for_science/probability.html) - 確率の英語表現一覧
* 📖 [Excel で CSV UTF-8 ファイルを正しく開く](https://support.microsoft.com/ja-jp/office/excel-%E3%81%A7-csv-utf-8-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E6%AD%A3%E3%81%97%E3%81%8F%E9%96%8B%E3%81%8F-8a935af5-3416-4edd-ba7e-3dfd2bc4a032)
* 📖 [半導体の製造 ＞ 正確度と精度](https://www.hitachi-hightech.com/jp/ja/knowledge/semiconductor/room/manufacturing/accuracy-precision.html) - precision と accuracy の違い
