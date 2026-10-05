# C++ 資料結構家教 🧑‍🏫

一個在自己電腦上跑的 **C++ 教學 + 練習題 + 自動測資 + 線上評測（Online Judge）** 平台，分成兩條路線：

| 路線 | 內容 |
|---|---|
| 📚 **資料結構** | `lessons/` 12 篇教學 + 複雜度考題、`problems/` 17 題（河內塔、vector、鏈結串列、stack/queue、雜湊表、heap、BST、圖、併查集……） |
| 🔧 **C++ 深入** | `cpp/lessons/` 15 篇教學、`cpp/problems/` 14 題（運算式、敘述、函式、指標、RAII、類別、繼承與多型、ADT、模板、STL、字串 IO、例外、編譯模型、現代 C++） |

- 🧪 **測資產生器**：每題都有 corner case + 小 / 中 / 大隨機測資，可以換 seed 重新產生
- ⚖️ **評測**：編譯你的 C++、跑測資、回報 AC / WA / TLE / RE / CE，顯示第一個不同的地方
- 🔍 **除錯工具**：`--debug`（AddressSanitizer + UBSan）、**對拍**（自動找出反例）
- 🌐 **網頁版**：瀏覽器裡看教學、寫 code、按一下就評測；上方切換兩條路線

只需要 `g++`（C++17）和 `python3`，**不用安裝任何套件**。

## 快速開始

```bash
# 網頁版（推薦）
python3 judge.py serve
# 打開 http://127.0.0.1:8000

# 或命令列
python3 judge.py list              # 題目列表與進度
python3 judge.py start hanoi       # 建立 workspace/01_hanoi.cpp
python3 judge.py test hanoi        # 評測
python3 judge.py stress hanoi      # 對拍找反例
python3 judge.py test hanoi --debug
python3 judge.py run my.cpp in.txt # 執行任何 C++ 程式
python3 judge.py test c7           # C++ 深入路線第 7 題（c07_fraction）
```

詳細說明請看 [`lessons/00_how_to_use.md`](lessons/00_how_to_use.md)。

## 題目列表

### 📚 資料結構

| # | 題目 | 主題 | 難度 |
|---|---|---|---|
| 01 | 河內塔 | 遞迴 | ★☆☆ |
| 02 | 河內塔的第 k 步（n ≤ 60） | 遞迴 / 分治 | ★★☆ |
| 03 | 自己做一個 vector | 動態陣列、攤銷分析 | ★☆☆ |
| 04 | 單向鏈結串列 | 鏈結串列 | ★★☆ |
| 05 | 括號配對 | Stack | ★☆☆ |
| 06 | 最小值堆疊 | Stack | ★★☆ |
| 07 | 環狀佇列 | Queue | ★★☆ |
| 08 | 下一個更大的元素 | 單調 Stack | ★★☆ |
| 09 | 滑動視窗最大值 | 單調 Deque | ★★★ |
| 10 | 自己做一個雜湊表 | Hash Table | ★★☆ |
| 11 | LRU 快取 | 雙向串列 + 雜湊表 | ★★★ |
| 12 | 二元堆積 | Heap | ★★☆ |
| 13 | 二元搜尋樹 | BST | ★★★ |
| 14 | 併查集 | Union-Find | ★★☆ |
| 15 | 迷宮最短路徑 | Graph / BFS | ★★☆ |
| 16 | 拓撲排序 | Graph / DAG | ★★★ |
| 17 | N 皇后 | 回溯法 | ★★☆ |

### 🔧 C++ 深入

| # | 題目 | 主題 | 難度 |
|---|---|---|---|
| C01 | 運算式求值 | 優先順序、結合性、整數除法 | ★★☆ |
| C02 | 位元運算 | 位元運算子、移位的未定義行為 | ★★☆ |
| C03 | 日期計算 | 控制流程、switch 穿透 | ★★☆ |
| C04 | 多條件排序 | lambda、嚴格弱序 | ★★☆ |
| C05 | 用指標做矩陣 | 指標的指標、動態配置 | ★★☆ |
| C06 | 自己做一個字串類別 | RAII、五法則、自我指定 | ★★★ |
| C07 | 分數類別 | 運算子多載、不變量 | ★★☆ |
| C08 | 圖形與多型 | 繼承、虛擬函式、抽象類別 | ★★☆ |
| C09 | 銀行帳戶系統 | ADT、介面、原子操作 | ★★★ |
| C10 | 泛型堆疊 | 類別模板、函式模板多載 | ★★☆ |
| C11 | 單字頻率統計 | STL 容器與演算法 | ★★☆ |
| C12 | 成績單解析 | getline、stringstream、格式化 | ★★☆ |
| C13 | 安全的計算機 | 例外、強例外保證、溢位檢查 | ★★★ |
| C14 | 智慧指標串列 | unique_ptr、解構的遞迴陷阱 | ★★★ |

## 目錄結構

```
judge.py                 評測工具（CLI + 網頁伺服器入口）
web/                     網頁版（server.py + index.html）
lessons/                 資料結構教學
cpp/lessons/             C++ 深入教學
cpp/problems/            C++ 深入題目（結構同 problems/）
problems/<題目>/
    problem.md           題目敘述
    template.cpp         作答樣板
    solution.cpp         標準解（卡關再看！）
    gen.py               測資產生器（corner case + 隨機）
    tests/               產生出來的測資（自動產生，不進 git）
workspace/               你的程式碼放這裡
```

## 新增題目

在 `problems/` 新增資料夾並放入上面四個檔案即可，格式見
[`lessons/11_testing_and_corner_cases.md`](lessons/11_testing_and_corner_cases.md)。
