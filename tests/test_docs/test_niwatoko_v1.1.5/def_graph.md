# 要件定義書

## 目的
本プログラムは、2つのCSVファイル('zoltraak.csv'と'niwatoko.csv')から累積ダウンロード数の推移を折れ線グラフで可視化することを目的としています。

## 入力データ
- 'zoltraak.csv'
- 'niwatoko.csv'

## 処理内容
1. 'zoltraak.csv'と'niwatoko.csv'のデータを読み込み、1つのデータフレームにマージする。
2. 'download_date'列を日付型に変換し、インデックスとして設定する。
3. 日付が重複する行の累積ダウンロード数を合計する。
4. 累積ダウンロード数の推移を折れ線グラフで描画する。

## 出力
- 累積ダウンロード数の推移を示す折れ線グラフ

## 前提条件
- 'zoltraak.csv'と'niwatoko.csv'が同一のディレクトリに存在していること。
- pandas、matplotlib.pylotライブラリがインストールされていること。
