# パスカルの三角形を使って、ハンディキャップを計算しよう

**先手ｍ本先取、後手ｎ本先取** といったルールを作ったとき、先手と後手の勝率の比がどれぐらいになるのかは、パスカルの三角形を眺めれば計算できます  


# 先手１本先取／後手１本先取制

```
+---+
| 1 |   先手１回勝ち
+---+

後手
１回勝ち
```

先手と後手の勝率の比　１：１　（先手勝率５０％）  

※先手勝率＝先手の勝率の比／（先手の勝率の比＋後手の勝率の比）  


# 先手２本先取／後手１本先取制

```
+---+   +----+
| 1 +---+  1 |   先手１回勝ち
+---+   +----+

後手　　　後手
１回勝ち　１回勝ち
```

先手と後手の勝率の比　１：２　（先手勝率３３％）


# 先手３本先取／後手１本先取制

```
+---+   +----+   +----+
| 1 +---+  1 +---+  1 |   先手１回勝ち
+---+   +----+   +----+

後手　　　後手　　　後手
１回勝ち　１回勝ち　１回勝ち
```

先手と後手の勝率の比　１：３　（先手勝率２５％）


# 先手３本先取／後手２本先取制

```
+---+   +----+   +----+
| 1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+
  |        |        |
+-+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 |   先手３回勝ち
+---+   +----+   +----+

後手　　　後手　　　後手
１回勝ち　２回勝ち　３回勝ち
```

先手と後手の勝率の比　４：６　＝　２：３　（先手勝率４０％）


# 先手４本先取／後手１本先取制

```
+---+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+---+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手
１回勝ち　１回勝ち　１回勝ち　１回勝ち
```

先手と後手の勝率の比　１：４　（先手勝率２０％）


# 先手４本先取／後手２本先取制

```
+---+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 +---+  4 |   先手４回勝ち
+---+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手
１回勝ち　２回勝ち　３回勝ち　４回勝ち
```

先手と後手の勝率の比　５：１０　＝　１：２　（先手勝率３３％）


# 先手４本先取／後手３本先取制

```
+---+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 +---+  4 |   先手４回勝ち
+-+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  3 +---+  6 +---+ 10 |   先手１０回勝ち
+---+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手
１回勝ち　３回勝ち　６回勝ち　１０回勝ち
```

先手と後手の勝率の比　１５：２０　＝　３：４　（先手勝率４３．３％）


# 先手５本先取／後手１本先取制

```
+---+   +----+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+---+   +----+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手　　　後手
１回勝ち　１回勝ち　１回勝ち　１回勝ち　１回勝ち
```

先手と後手の勝率の比　１：５　（先手勝率１６．６％）


# 先手５本先取／後手２本先取制

```
+---+   +----+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 +---+  4 +---+  5 |   先手５回勝ち
+---+   +----+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手　　　後手
１回勝ち　２回勝ち　３回勝ち　４回勝ち　５回勝ち
```

先手と後手の勝率の比　６：１５　＝　２：５　（先手勝率２８．５％）


# 先手５本先取／後手３本先取制

```
+---+   +----+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 +---+  4 +---+  5 |   先手５回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  3 +---+  6 +---+ 10 +---+ 15 |   先手１５回勝ち
+---+   +----+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手　　　後手
１回勝ち　３回勝ち　６回勝ち　10回勝ち　15回勝ち
```

先手と後手の勝率の比　２１：３５　＝　３：５　（先手勝率３７．５％）


# 先手５本先取／後手４本先取制

```
+---+   +----+   +----+   +----+   +----+
| 1 +---+  1 +---+  1 +---+  1 +---+  1 |   先手１回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  2 +---+  3 +---+  4 +---+  5 |   先手５回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  3 +---+  6 +---+ 10 +---+ 15 |   先手１５回勝ち
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
  |        |        |        |        |
+-+-+   +--+-+   +--+-+   +--+-+   +--+-+
| 1 +---+  4 +---+ 10 +---+ 20 +---+ 35 |   先手３５回勝ち
+---+   +----+   +----+   +----+   +----+

後手　　　後手　　　後手　　　後手　　　後手
１回勝ち　４回勝ち　10回勝ち　20回勝ち　35回勝ち
```

先手と後手の勝率の比　５６：７０　＝　４：５　（先手勝率４４．４％）

