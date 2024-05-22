## 要件定義書

### 1. 足し算モジュール (`足し算py`)

#### 機能概要
1. **数値の足し算**
    - 2つの数値を足し算する。
2. **リスト内の数値の合計**
    - 数値のリストの合計を計算する。
3. **複数の数値の合計**
    - 任意の数の数値を受け取り、その合計を計算する。

#### 関数仕様

1. **add**
    - **説明**: 2つの数値を足し算する関数。
    - **引数**:
        - `a` (int または float): 1つ目の数値
        - `b` (int または float): 2つ目の数値
    - **戻り値**: `a`と`b`の和 (int または float)

2. **add_list**
    - **説明**: 数値のリストの合計を計算する関数。
    - **引数**:
        - `numbers` (list): 数値のリスト
    - **戻り値**: `numbers`の合計値 (int または float)

3. **add_multiple**
    - **説明**: 複数の数値を足し算する関数。
    - **引数**: 任意の数の数値 (可変長引数)
    - **戻り値**: 引数として渡された数値の合計 (int または float)

#### テスト項目
1. **add関数のテスト**
    - 正の整数同士の足し算
    - 負の整数同士の足し算
    - 小数同士の足し算
    - 正の整数と負の整数の足し算
    - 0を含む足し算

2. **add_list関数のテスト**
    - 空のリストの合計
    - 正の整数リストの合計
    - 負の整数リストの合計
    - 小数リストの合計

3. **add_multiple関数のテスト**
    - 引数なしの場合
    - 正の整数複数の合計
    - 負の整数複数の合計
    - 小数複数の合計
    - 混在する数値の合計

### 2. 掛け算モジュール (`掛け算py`)

#### 機能概要
1. **数値の掛け算**
    - 2つの数値を掛け算する。
2. **リスト内の数値の積**
    - 数値のリストの積を計算する。
3. **複数の数値の積**
    - 任意の数の数値を受け取り、その積を計算する。

#### 関数仕様

1. **multiply**
    - **説明**: 2つの数値を掛け算する関数。
    - **引数**:
        - `a` (int または float): 1つ目の数値
        - `b` (int または float): 2つ目の数値
    - **戻り値**: `a`と`b`の積 (int または float)

2. **multiply_list**
    - **説明**: 数値のリストの積を計算する関数。
    - **引数**:
        - `numbers` (list): 数値のリスト
    - **戻り値**: `numbers`の積 (int または float)

3. **multiply_multiple**
    - **説明**: 複数の数値を掛け算する関数。
    - **引数**: 任意の数の数値 (可変長引数)
    - **戻り値**: 引数として渡された数値の積 (int または float)

#### テスト項目
1. **multiply関数のテスト**
    - 正の整数同士の掛け算
    - 負の整数同士の掛け算
    - 小数同士の掛け算
    - 正の整数と負の整数の掛け算
    - 0を含む掛け算

2. **multiply_list関数のテスト**
    - 空のリストの積
    - 正の整数リストの積
    - 負の整数リストの積
    - 小数リストの積

3. **multiply_multiple関数のテスト**
    - 引数なしの場合
    - 正の整数複数の積
    - 負の整数複数の積
    - 小数複数の積
    - 混在する数値の積