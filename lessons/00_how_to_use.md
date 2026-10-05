# 00. 如何使用這個平台

這是一個在自己電腦上跑的 **C++ 家教 + 線上評測（Online Judge）**，有兩條路線：

- 📚 **資料結構**（這裡）：`lessons/` 和 `problems/`
- 🔧 **C++ 深入**：`cpp/lessons/` 和 `cpp/problems/`，專門把 C++ 語言本身學扎實（指標、記憶體、類別、繼承、模板、例外……）。網頁版上方可以切換，從 `cpp/lessons/00_roadmap.md` 開始。

建議：C++ 語法還不熟的話，先讀 C++ 深入的第 01 ~ 07 課，再回來做資料結構。
你會在這裡：

1. 讀 **教學**（`lessons/`），理解每種資料結構的原理、複雜度和 C++ 寫法。
2. 做 **練習題**（`problems/`），從河內塔到 LRU Cache、拓撲排序。
3. 用 **評測工具** 跑你的程式：自動產生測資（包含各種 corner case）、比對答案、告訴你 AC / WA / TLE / RE。

## 需要的工具

- `g++`（支援 C++17）
- `python3`（3.8 以上，不需要安裝任何套件）

## 方法一：網頁版（推薦）

```bash
python3 judge.py serve
```

打開瀏覽器 <http://127.0.0.1:8000>，左邊選教學或題目，右邊直接寫 C++：

- **提交評測**（`Ctrl+Enter`）：跑全部測資，點失敗的測資可以看輸入、預期輸出、你的輸出。
- **執行（自訂輸入）**：用你自己打的輸入跑一次，就像在終端機執行。
- **debug**：用 AddressSanitizer 編譯，陣列越界、存取已釋放的記憶體都會被抓出來，並告訴你是哪一行。
- **測資** 分頁：看所有測資內容，或換 seed 重新產生一批隨機測資。

程式會自動存到 `workspace/<題目>.cpp`，也可以用自己習慣的編輯器（VS Code 等）改那個檔案。

## 方法二：命令列

```bash
python3 judge.py list                 # 看所有題目與進度
python3 judge.py start hanoi          # 建立 workspace/01_hanoi.cpp（從樣板複製）
# ... 用你喜歡的編輯器寫 workspace/01_hanoi.cpp ...
python3 judge.py test hanoi           # 評測
python3 judge.py test hanoi --debug   # 用 sanitizer 評測，找記憶體錯誤
python3 judge.py stress hanoi         # 對拍：隨機產生小測資，和標準解比對直到找到反例
python3 judge.py gen hanoi --seed 42  # 換一批隨機測資
python3 judge.py run my.cpp input.txt # 單純編譯執行任何 C++ 檔案
```

題目可以用編號（`1`）、名稱（`hanoi`）或全名（`01_hanoi`）指定；C++ 深入的題目用 `c1` ~ `c14`。

## 評測結果代表什麼？

| 結果 | 意思 | 常見原因 |
|---|---|---|
| **AC** Accepted | 答案正確 | 🎉 |
| **WA** Wrong Answer | 輸出和預期不同 | 邏輯錯誤、沒處理 corner case、輸出格式不對 |
| **TLE** Time Limit Exceeded | 超過時間限制 | 演算法複雜度太高、無窮迴圈、用了 `endl` 輸出大量資料 |
| **RE** Runtime Error | 程式當掉 | 陣列越界、空指標、遞迴太深、除以 0 |
| **MLE** Memory Limit Exceeded | 記憶體用太多 | 陣列開太大、記憶體洩漏 |
| **CE** Compile Error | 編譯失敗 | 語法錯誤 |

比對時會忽略 **行尾空白** 和 **最後多餘的空行**，其他都要完全一樣。

## 測資是怎麼來的？

每一題的 `problems/<題目>/gen.py` 是測資產生器：

- `manual_cases()`：手工設計的 **corner case**，檔名會是 `corner_xxx`，名稱本身就是提示（例如 `corner_pop_empty`、`corner_negative_keys`、`corner_serpentine_1000x1000`）。
- `random_case()`：隨機產生 `small` / `medium` / `large` 三種大小的測資，`large` 用來檢查時間複雜度。

預期輸出是用 `solution.cpp`（標準解）跑出來的。**建議先自己寫，卡住很久再看標準解。**

## 建議的學習路線

| 教學 | 練習題 |
|---|---|
| `01_cpp_basics_and_complexity.md` | （先讀，打基礎） |
| `01b_complexity_exam.md` | 時間複雜度考題（40 題，附解答） |
| `02_recursion.md` | `01_hanoi` → `02_hanoi_kth` → `17_n_queens` |
| `03_dynamic_array.md` | `03_my_vector` |
| `04_linked_list.md` | `04_linked_list` |
| `05_stack_queue.md` | `05_brackets` → `06_min_stack` → `07_circular_queue` → `08_next_greater` → `09_sliding_window_max` |
| `06_hash_table.md` | `10_hash_table` → `11_lru_cache` |
| `07_heap.md` | `12_binary_heap` |
| `08_bst.md` | `13_bst` |
| `09_graph.md` | `15_maze_bfs` → `16_topo_sort` |
| `10_union_find.md` | `14_union_find` |
| `11_testing_and_corner_cases.md` | 學會自己找 corner case、自己寫產生器和對拍 |

## 新增你自己的題目

在 `problems/` 開一個新資料夾（例如 `18_my_problem/`），放四個檔案：

- `problem.md`：題目敘述
- `template.cpp`：給自己的樣板
- `solution.cpp`：標準解
- `gen.py`：至少要有 `TITLE`、`TOPIC`、`DIFFICULTY`、`manual_cases()`、`random_case(rng, size)`

可以參考任何一題現有的 `gen.py`。
