# C++ 資料結構家教 🧑‍🏫

一個在自己電腦上跑的 **C / C++ 教學 + 練習題 + 自動測資 + 線上評測（Online Judge）** 平台，分成三條練習路線和兩本讀本：

| 路線 | 內容 |
|---|---|
| 📚 **資料結構** | `lessons/` 12 篇教學 + 複雜度考題、`problems/` 17 題（河內塔、vector、鏈結串列、stack/queue、雜湊表、heap、BST、圖、併查集……） |
| 🔧 **C++ 深入** | `cpp/lessons/` 15 篇教學、`cpp/problems/` 14 題（運算式、敘述、函式、指標、RAII、類別、繼承與多型、ADT、模板、STL、字串 IO、例外、編譯模型、現代 C++） |
| 🅲 **C 語言** | `c/lessons/` 13 篇教學、`c/problems/` 10 題（printf/scanf、指標、字串、malloc/free、struct、函式指標、檔案 IO、前置處理器、用 C 實作串列與雜湊表），用 `gcc -std=c11` 評測，多題會檢查記憶體洩漏 |
| 📖 **C 介面與實作** | `cii/lessons/` 20 章讀書筆記：《C Interfaces and Implementations》（David R. Hanson），介面與實作、Atom、例外、記憶體管理、串列 / 關聯表 / 集合 / 序列 / 環 / 位元向量、字串、多精度算術、執行緒。只有閱讀，沒有評測題目 |
| 🔐 **密碼工程** | `ce/lessons/` 23 章讀書筆記：《Cryptography Engineering》（Ferguson、Schneier、Kohno），區塊加密、加密模式、雜湊、MAC、安全通道、亂數、質數、Diffie-Hellman、RSA、密碼協定、金鑰協商、時鐘、金鑰伺服器、PKI、儲存秘密、標準與專利。只有閱讀，沒有評測題目 |

- 🧪 **測資產生器**：每題都有 corner case + 小 / 中 / 大隨機測資，可以換 seed 重新產生
- ⚖️ **評測**：編譯你的 C / C++、跑測資、回報 AC / WA / TLE / RE / CE，顯示第一個不同的地方
- 📝 **總複習考卷**：每條路線一份（共 383 題），涵蓋每一章；可以照章節或打亂出題、只考選定的章節，寫完在右邊對答案、自評，最後列出要重讀的章節。作答自動存到 `workspace/exams/`
- 🔍 **除錯工具**：`--debug`（AddressSanitizer + UBSan）、**對拍**（自動找出反例）
- 🌐 **網頁版**：技術手冊風格的閱讀介面（章節目錄、本章段落、閱讀進度、深淺色、字級），寫 code、按一下就評測；左上角切換路線

只需要 `g++`（C++17）、`gcc`（C11，C 語言路線用）和 `python3`，**不用安裝任何套件**。

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
python3 judge.py start cl3         # C 語言路線第 3 題：建立 workspace/cl03_pointer_ops.c
python3 judge.py test cl3 --debug  # C 題目強烈建議用 --debug 抓記憶體錯誤
```

詳細說明請看 [`lessons/00_how_to_use.md`](lessons/00_how_to_use.md)。

### Windows 使用者

可以直接在 Windows 上執行（指令裡的 `python3` 可能要改成 `python` 或 `py`），需要先安裝：

- **Python 3**：從 python.org 安裝，安裝時勾選「Add Python to PATH」。
- **g++**：例如安裝 [MSYS2](https://www.msys2.org/) 後執行 `pacman -S mingw-w64-ucrt-x86_64-gcc`，再把 `C:\msys64\ucrt64\bin` 加進 PATH。打開新的終端機輸入 `g++ --version` 看得到版本號就成功了（同一個套件也包含 C 語言路線需要的 `gcc`）。

和 Linux / Mac 的差別：
- Windows 上沒有記憶體上限檢查（MLE 只能靠程式自己配置失敗才偵測得到）。
- `--debug` 模式只有 STL 的越界檢查（`_GLIBCXX_DEBUG`），沒有 AddressSanitizer / UBSan（MinGW 不支援）。需要完整的檢查時，建議用 WSL（`wsl --install`）在 Linux 環境裡執行。

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

### 🅲 C 語言

| # | 題目 | 主題 | 難度 |
|---|---|---|---|
| CL01 | 格式化輸入輸出 | printf / scanf 的格式 | ★☆☆ |
| CL02 | 自己寫 string.h | `'\0'`、字串函式 | ★★☆ |
| CL03 | 用指標操作陣列 | 指標算術、[begin, end) 區間 | ★★☆ |
| CL04 | 動態陣列 | malloc / realloc / free、容量倍增 | ★★☆ |
| CL05 | C 語言的鏈結串列 | 節點、`Node **`、記憶體洩漏 | ★★★ |
| CL06 | 學生成績排名 | struct、qsort、bsearch | ★★☆ |
| CL07 | 文字統計 | getchar 讀到 EOF、`<ctype.h>` | ★★☆ |
| CL08 | 動態二維矩陣 | 指標的指標、矩陣乘法 | ★★★ |
| CL09 | 函式指標與指令表 | 函式指標、回呼、查表分派 | ★★★ |
| CL10 | 字串雜湊表 | 分離鏈結法、rehash、字串複製 | ★★★★ |

## 目錄結構

```
judge.py                 評測工具（CLI + 網頁伺服器入口）
web/                     網頁版（server.py + index.html）
lessons/                 資料結構教學
cpp/lessons/             C++ 深入教學
cpp/problems/            C++ 深入題目（結構同 problems/）
c/lessons/               C 語言教學
c/problems/              C 語言題目（結構同 problems/，但檔案是 template.c / solution.c）
cii/lessons/             《C 介面與實作》讀書筆記（parts.json 定義側欄的四個部分）
ce/lessons/              《Cryptography Engineering》讀書筆記（parts.json 定義側欄的五個部分）
exams/<路線>.md          總複習考卷（格式見 web/exam.py；python3 exams/check.py 會編譯執行所有「預測輸出」題核對答案）
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
