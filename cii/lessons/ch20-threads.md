# 第 20 章　Threads（執行緒）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.405–467
> **全書最後一章**

---

## 1. 本章定位

### 1.1 什麼是執行緒

- 典型的 C 程式是**循序的（單執行緒）**：程式裡只有一個控制點。程式計數器的值描繪出一條穿過程式的路徑，**看起來就像一條線（thread）**。
- **並行（多執行緒）程式**有不只一個執行緒，而且至少在概念上**同時執行**。
- **困難之處**：執行緒之間可能以**非決定性**的方式互動，所以寫多執行緒程式比單執行緒難得多。

本章的**三個介面**：

| 介面 | 用途 |
|---|---|
| **Thread** | 建立和管理執行緒 |
| **Sem** | 同步協作的執行緒（信號量） |
| **Chan** | 執行緒之間的通訊（同步通道） |

### 1.2 執行緒的三種用途

1. **本質上就是並行的應用**：例如**圖形介面**，鍵盤輸入、滑鼠移動和點擊、畫面輸出都同時發生。每個活動可以用一個執行緒處理，**各自寫成循序程式**，只有少數地方需要通訊或同步。
2. **在多處理器上提升效能**：把可以自然分解的工作分成獨立的子工作，同時執行（見 20.2 的平行排序）。
3. **組織循序程式的結構**：執行緒**有狀態**，可以暫停後再從中斷處繼續。例如 UNIX 的 C 編譯器由前處理器、編譯器本體、組譯器組成，通常用**暫存檔**互相傳遞資料；改用執行緒的話，每個階段是一個執行緒，**省掉暫存檔**（見 20.2 的質數管線）。

### 1.3 使用者層級 vs. 核心層級執行緒

| | 使用者層級（user-level） | 核心層級（kernel-level） |
|---|---|---|
| 實作 | 完全在使用者模式，不需要作業系統幫忙 | 使用作業系統的功能 |
| 效率 | **非常有效率** | 某些操作需要系統呼叫，比較貴 |
| 缺點 | **阻塞式 I/O 會讓整個行程停住**；signal 綁定在行程上 | — |
| 優點 | — | 非阻塞 I/O、每個執行緒各自的 signal |

> **本章的 Thread 介面提供的是使用者層級執行緒。**

### 1.4 ⭐ 可重入（reentrant）vs. 執行緒安全（thread-safe）

| 概念 | 定義 |
|---|---|
| **可重入** | 函式**只修改區域變數和參數**；修改全域變數或用 static 變數存中間結果的函式就是**不可重入**的 |
| **執行緒安全** | 用同步機制管理共用資料的存取，可以被多個執行緒**同時呼叫**；不一定可重入。代價是就算單執行緒的 client 也要付出同步的成本 |

- 單執行緒程式也可能同時有多個啟動中的呼叫，例如直接或間接的遞迴；多執行緒程式則是多個執行緒同時呼叫同一個函式。
- **標準 C 不要求函式庫函式可重入或執行緒安全**，所以程式設計師必須做最壞的假設，用同步機制確保一次只有一個執行緒執行不可重入的函式庫函式。
- **本書大多數函式不是執行緒安全的，但是可重入的**；少數像 **`Text_map`**（用了 static 的 map）是**不可重入**的。
- 例如多個執行緒共用一個 Table_T 時，**client 必須自己確保**一次只有一個執行緒對它呼叫 Table 的函式。

### 1.5 其他執行緒系統

- **DCE**（OSF 的分散式計算環境）：同時支援使用者層級和核心層級，**超過 50 個函式**，支援執行緒層級的 signal，並用適當的同步保護標準函式庫呼叫。
- **Solaris 2**：兩層架構，核心層級的 **LWP**（輕量級行程）加上在 LWP 上執行的使用者層級執行緒。
- **POSIX threads（pthreads）**：正在成為**主流標準**，功能是 Thread 和 Sem 的**超集**，還規定了哪些標準 C 函式必須是執行緒安全的。

---

## 2. 基本概念

| 術語 | 意義 |
|---|---|
| **排程（scheduling）** | 執行緒通常比處理器多，處理器依照排程策略在執行緒之間**多工** |
| **非搶占式（nonpreemptive）** | 執行中的執行緒**自己**阻塞或讓出處理器 |
| **搶占式（preemptive）** | 執行中的執行緒**被動地**讓出處理器，通常用**時鐘中斷**實作 |
| **時間片（quantum）** | 執行緒被搶占前可以執行的時間 |
| **context switch** | 暫停目前的執行緒，繼續另一個（也可能是同一個） |
| **原子動作（atomic action）** | 執行過程**不會被搶占**；原子函式**仍然可能阻塞**，例如 Sem 的同步函式 |

> 並行程式設計有自己的術語，而且**同一個概念常有不同名稱**：執行緒也叫輕量級行程、task、subtask、microtask；同步機制也叫 event、condition variable、synchronizing resource、message。

---

## 3. Thread 介面（20.1.1）

```c
/* thread.h */
#ifndef THREAD_INCLUDED
#define THREAD_INCLUDED
#include "except.h"

#define T Thread_T
typedef struct T *T;

extern const Except_T Thread_Failed;
extern const Except_T Thread_Alerted;

extern int  Thread_init (int preempt, ...);
extern T    Thread_new  (int apply(void *), void *args, int nbytes, ...);
extern void Thread_exit (int code);
extern void Thread_alert(T t);
extern T    Thread_self (void);
extern int  Thread_join (T t);
extern void Thread_pause(void);

#undef T
#endif
```

**這個介面的所有函式呼叫都是原子的。**

### 3.1 `Thread_init`：初始化

- **必須在其他任何函式之前呼叫**，而且**只能呼叫一次**；在這之前呼叫 Thread、Sem、Chan 的任何函式都是 checked error。
- `preempt = 0`：只支援非搶占式排程，回傳 1。
- `preempt = 1`：要求搶占式排程。**支援就回傳 1；不支援就退回非搶占式，回傳 0。**
- 可以接受**和實作相關的額外參數**，通常是名稱/值對，以 NULL 結束：

```c
preempt = Thread_init(1, "priorities", 4, NULL);   /* 4 個優先等級 */
```

**典型的 main：**

```c
int main(int argc, char *argv[]) {
    int preempt;
    ...
    preempt = Thread_init(1, NULL);
    assert(preempt == 1);
    ...
    Thread_exit(EXIT_SUCCESS);     /* ⚠ 執行緒必須用 Thread_exit 結束 */
    return EXIT_SUCCESS;
}
```

### 3.2 ⭐ `Thread_new`：建立執行緒

```c
extern T Thread_new(int apply(void *), void *args, int nbytes, ...);
```

新執行緒開始執行時，做的事**等同於**：

```c
void *p = ALLOC(nbytes);
memcpy(p, args, nbytes);       /* ⭐ 複製一份參數 */
Thread_exit(apply(p));
```

| 參數情況 | 行為 |
|---|---|
| args 不是 NULL，nbytes > 0 | `apply` 拿到 args 前 nbytes 個位元組的**複本** |
| args 不是 NULL，nbytes = 0 | `apply(args)`，**原封不動**地傳遞（共用） |
| args 是 NULL | `apply(NULL)`，忽略 nbytes |

- **args 通常指向一個結構**，結構的欄位存放 apply 的參數，nbytes 就是 `sizeof` 那個結構。
- **為什麼要複製？** 讓呼叫端可以**馬上重複使用** args 指向的結構，例如在迴圈裡建立多個執行緒。
- **新執行緒的例外堆疊是空的**：它**不會繼承**呼叫端執行緒 TRY-EXCEPT 建立的例外狀態。**例外是每個執行緒各自的。**
- **建立是同步的**：`Thread_new` 在新執行緒建立好、也拿到參數之後才返回，但新執行緒**可能還沒開始執行**。
- 資源不足時（例如執行緒數量有上限）丟出 **`Thread_Failed`**。
- apply 是 NULL，或 args 不是 NULL 但 nbytes 是負數，都是 checked error。
- 也可以接受額外參數，例如 `Thread_new(apply, args, nbytes, "priority", 2, NULL)`。

### 3.3 結束與等待

| 函式 | 行為 |
|---|---|
| `Thread_exit(code)` | 結束呼叫的執行緒；**等待它結束**的執行緒會被喚醒，並從 `Thread_join` 拿到 code；**最後一個**執行緒呼叫時，整個程式以 `exit(code)` 結束 |
| `Thread_join(t)` | 暫停，直到 t 呼叫 `Thread_exit`，然後回傳 t 的 code；t 不存在時**立即回傳 −1** |
| `Thread_join(NULL)` | **等待所有其他執行緒結束**（包括其他執行緒之後建立的），回傳 0 |
| `Thread_self()` | 回傳呼叫的執行緒自己的 handle |
| `Thread_pause()` | 讓出處理器給另一個準備好的執行緒；**主要用在非搶占式排程** |

**Checked error**：t 是呼叫的執行緒自己；**不只一個**執行緒用 NULL 呼叫 `Thread_join`；**沒有任何執行中的執行緒**（死結）。`Thread_join` 可能丟出 `Thread_Alerted`。

### 3.4 執行緒的三種狀態

```
         Thread_new
              ↓
          ┌────────┐  Thread_join / Sem_wait / Chan_*   ┌─────────┐
          │ running│ ─────────────────────────────────→ │ blocked │
          │        │ ←───────────────────────────────── │         │
          └────────┘     被喚醒 / Thread_alert            └─────────┘
              │
              │ Thread_exit
              ↓
          ┌────────┐
          │  dead  │
          └────────┘
```

### 3.5 ⭐ `Thread_alert`：唯一能「中斷」另一個執行緒的方法

```c
extern void Thread_alert(T t);
```

- 設定 t 的「**alert-pending**」旗標。
- **t 正在阻塞**：讓 t 變成可執行，下次執行時清除旗標並**丟出 `Thread_Alerted`**。
- **t 正在執行**：t 下次呼叫 `Thread_join`、或會阻塞的通訊或同步函式時，清除旗標並丟出 `Thread_Alerted`。
- 傳 NULL 或不存在的 handle 是 checked error。

> **沒有辦法強制終止一個執行中的執行緒**。執行緒必須**自己結束**：呼叫 `Thread_exit`，或是對 `Thread_Alerted` 做出反應。如果執行緒沒有捕捉 `Thread_Alerted`，**整個程式**會因為未捕捉的例外而結束。

**標準寫法**：

```c
int apply(void *p) {
    TRY
        ...
    EXCEPT(Thread_Alerted)
        Thread_exit(EXIT_FAILURE);   /* 最常見的反應：結束自己 */
    END_TRY;
    Thread_exit(EXIT_SUCCESS);
}
```

**⚠ 常見錯誤**：

```c
Thread_T t;
TRY
    t = Thread_new(...);             /* ✗ 這個 TRY 屬於「呼叫端」執行緒 */
EXCEPT(Thread_Alerted)
    Thread_exit(EXIT_FAILURE);
END_TRY;
```

這是錯的，因為 **TRY-EXCEPT 只作用在執行它的那個執行緒**，不會作用在新執行緒上。

---

## 4. Sem 介面：一般信號量（20.1.2）

### 4.1 概念

**一般（計數）信號量**是低階的同步原語。抽象來說，信號量是一個**受保護的整數**，可以被**原子地**遞增和遞減：

```
signal(s):  s = s + 1               （原子地）
wait(s):    while (s <= 0) ;        （等到 s 變成正數）
            s = s - 1               （原子地）
```

當然，實際的實作會**阻塞**呼叫的執行緒，而不是像上面那樣空轉。

### 4.2 介面

```c
/* sem.h */
#ifndef SEM_INCLUDED
#define SEM_INCLUDED

#define T Sem_T
typedef struct T {
    int count;
    void *queue;
} T;

#define LOCK(mutex) do { Sem_T *_yymutex = &(mutex); \
    Sem_wait(_yymutex);
#define END_LOCK Sem_signal(_yymutex); } while (0)

extern void Sem_init  (T *s, int count);
extern T   *Sem_new   (int count);
extern void Sem_wait  (T *s);
extern void Sem_signal(T *s);

#undef T
#endif
```

**⭐ 公開結構但當作不透明型別**：
> 介面公開 Sem_T 的內部結構，**只是為了讓它能被靜態配置，或內嵌在其他結構裡**。client 必須把 Sem_T 當成不透明型別，**只能透過介面函式存取**；直接存取欄位是 unchecked error。

（這和第 10 章 ArrayRep 的考量類似，但 Sem 更嚴格：可以看，但不能用。）

| 函式 | 行為 |
|---|---|
| `Sem_init(&s, count)` | 初始化並設定計數器的初值；對同一個信號量呼叫兩次是 unchecked error |
| `Sem_new(count)` | 等同於 `NEW(s); Sem_init(s, count);`（原子的），可能丟出 `Mem_Failed` |
| `Sem_wait(&s)` | 等到計數器是正數，然後減 1（原子的） |
| `Sem_signal(&s)` | 計數器加 1（原子的）；有執行緒在等待的話，其中一個會完成它的 `Sem_wait` |

- **alert**：呼叫 `Sem_wait` 時旗標已經設定，就**立即**丟出 `Thread_Alerted`，**不遞減**計數器；阻塞期間被 alert，就**停止等待**並丟出 `Thread_Alerted`，同樣**不遞減**。
- 傳 NULL 是 checked error；傳**沒有初始化**的信號量是 unchecked error。
- **⭐ 公平性**：佇列是**先進先出**的，而且是公平的。阻塞在 s 上的執行緒 t，會比**之後**才呼叫 `Sem_wait(&s)` 的執行緒先被喚醒。

### 4.3 二元信號量（mutex）與臨界區域

**二元信號量（mutex）**是計數器只會是 0 或 1 的一般信號量，用於**互斥**：

```c
Sem_T mutex;
Sem_init(&mutex, 1);
...
Sem_wait(&mutex);
statements          /* 臨界區域：一次只有一個執行緒 */
Sem_signal(&mutex);
```

這種寫法太常見了，所以 Sem 匯出 **LOCK-END_LOCK** 巨集：

```c
LOCK(mutex)
    statements
END_LOCK;
```

**好處**：避免兩種常見而且災難性的錯誤：
1. **忘了**在臨界區域結尾呼叫 `Sem_signal`。
2. 用**錯的信號量**呼叫 `Sem_signal`。

**⚠ 和例外的互動**：

> 如果 statements 可能丟出例外，**就不能用 LOCK-END_LOCK**，因為例外發生時 mutex **不會被釋放**。正確的寫法是：
> ```c
> TRY
>     Sem_wait(&mutex);
>     statements
> FINALLY
>     Sem_signal(&mutex);     /* 不論是否有例外都會釋放 */
> END_TRY;
> ```
> 也可以把這個寫法直接放進 LOCK 的定義，但**每次使用 LOCK 都會多付出 TRY-FINALLY 的成本**。

### 4.4 用 mutex 保護 ADT

```c
typedef struct {
    Sem_T mutex;            /* 內嵌，這就是公開結構的理由 */
    Table_T table;
} Protected_Table_T;

Protected_Table_T tab;
tab.table = Table_new(...);
Sem_init(&tab.mutex, 1);

/* 讀取：不會丟出例外，可以用 LOCK */
LOCK(tab.mutex)             /* 注意：LOCK 接受 mutex 本身，不是位址 */
    value = Table_get(tab.table, key);
END_LOCK;

/* 寫入：Table_put 可能丟出 Mem_Failed，要用 TRY-FINALLY */
TRY
    Sem_wait(&tab.mutex);
    Table_put(tab.table, key, value);
FINALLY
    Sem_signal(&tab.mutex);
END_TRY;
```

---

## 5. Chan 介面：同步通訊通道（20.1.3）

```c
/* chan.h */
#ifndef CHAN_INCLUDED
#define CHAN_INCLUDED

#define T Chan_T
typedef struct T *T;

extern T   Chan_new    (void);
extern int Chan_send   (T c, const void *ptr, int size);
extern int Chan_receive(T c,       void *ptr, int size);

#undef T
#endif
```

| 函式 | 行為 |
|---|---|
| `Chan_new()` | 建立新通道，可能丟出 `Mem_Failed` |
| `Chan_send(c, ptr, size)` | **等到**另一個執行緒對同一個通道呼叫 `Chan_receive`；**會合（rendezvous）**時資料從傳送端複製到接收端，兩邊都返回；回傳**接收端接受的位元組數** |
| `Chan_receive(c, ptr, size)` | **等到**另一個執行緒呼叫 `Chan_send`；會合時複製資料；傳送端給的超過 size 個位元組時，**多的部分會被丟掉**；回傳接受的位元組數 |

- **⭐ 同步**：傳送和接收必須**會合**，兩邊都會阻塞，直到對方到達。沒有緩衝區。
- **size 可以是 0**，可以用來傳遞「訊號」而不傳資料（見質數篩選範例）。
- 傳 NULL 的 Chan_T 或 ptr、或負的 size，都是 checked error。
- **alert**：旗標已經設定時立即丟出 `Thread_Alerted`；阻塞期間被 alert 就停止等待並丟出例外，**這時資料可能已經傳送，也可能還沒傳送**。

> 通道的概念來自 **CSP**（Hoare, 1978）。Go 語言沒有緩衝區的 channel 就是同樣的語意。

---

## 6. 範例（20.2 Examples）

### 6.1 平行排序 `sort`

**概念**：快速排序的兩個遞迴呼叫是**獨立**的，可以交給不同的執行緒同時執行。在多處理器系統上能縮短總時間；在單處理器上反而會因為切換執行緒的成本而**稍微變慢**，但這個範例示範了 Thread 介面的用法。

```c
int partition(int a[], int i, int j) {    /* 用 a[i] 當樞紐 */
    int v, k, t;
    j++;
    k = i;
    v = a[k];
    while (i < j) {
        i++; while (a[i] < v && i < j) i++;
        j--; while (a[j] > v         ) j--;
        if (i < j) { t = a[i]; a[i] = a[j]; a[j] = t; }
    }
    t = a[k]; a[k] = a[j]; a[j] = t;
    return j;
}

struct args {           /* 把 quick 的參數包成一個結構 */
    int *a;
    int lb, ub;
};

int cutoff = 10000;     /* 子陣列至少要這麼多元素，才值得開新執行緒 */

int quick(void *cl) {
    struct args *p = cl;
    int lb = p->lb, ub = p->ub;
    if (lb < ub) {
        int k = partition(p->a, lb, ub);

        p->lb = lb;                         /* 左半部 */
        p->ub = k - 1;
        if (k - lb > cutoff) {
            Thread_T t;
            t = Thread_new(quick, p, sizeof *p, NULL);   /* 參數會被複製 */
            Fmt_print("thread %p sorted %d..%d\n", t, lb, k - 1);
        } else
            quick(p);                       /* 太小了，直接遞迴 */

        p->lb = k + 1;                      /* 右半部（重複使用 p！）*/
        p->ub = ub;
        if (ub - k > cutoff) {
            Thread_T t;
            t = Thread_new(quick, p, sizeof *p, NULL);
            Fmt_print("thread %p sorted %d..%d\n", t, k + 1, ub);
        } else
            quick(p);
    }
    return EXIT_SUCCESS;
}

void sort(int *x, int n, int argc, char *argv[]) {
    struct args args;
    if (argc >= 3)
        cutoff = atoi(argv[2]);
    args.a = x;
    args.lb = 0;
    args.ub = n - 1;
    quick(&args);
    Thread_join(NULL);                      /* 等所有執行緒完成 */
}
```

**要點**：
- **`Thread_new` 會複製 nbytes 個位元組的參數**，所以建立左半部的執行緒之後，**p 可以馬上被改寫**來處理右半部。
- 用 **cutoff** 控制粒度：子陣列太小就直接遞迴，避免建立執行緒的成本超過好處。
- 預設 n = 100,000、cutoff = 10,000 時大約會產生 18 個執行緒；每次執行的結果都不一樣。
- **`Thread_join(NULL)`** 等待所有衍生出來的執行緒。

**⚠ 作者自己指出的 bug**：

> sort 有一個重要的 bug：**它沒有保護 quick 裡對 `Fmt_print` 的呼叫**。`Fmt_print` 不保證可重入，C 函式庫的許多常式也一樣，被中斷後再繼續執行時，不保證能正確運作。

### 6.2 臨界區域 `spin`

**示範共用資料存取的正確和錯誤寫法。** m 個執行緒各把共用的 n 遞增 NBUMP = 30000 次。

```c
int n;

int unsafe(void *cl) {                    /* ✗ 錯誤 */
    int i, *ip = cl;
    for (i = 0; i < NBUMP; i++)
        *ip = *ip + 1;                    /* 讀取、加 1、寫回之間可能被搶占 */
    return EXIT_SUCCESS;
}

struct args {
    Sem_T *mutex;
    int *ip;
};

int safe(void *cl) {                      /* ✓ 正確 */
    struct args *p = cl;
    int i;
    for (i = 0; i < NBUMP; i++)
        LOCK(*p->mutex)
            *p->ip = *p->ip + 1;          /* 臨界區域 */
        END_LOCK;
    return EXIT_SUCCESS;
}

/* 不安全的版本 */
for (i = 0; i < m; i++)
    Thread_new(unsafe, &n, 0, NULL);      /* nbytes = 0：共用 &n，不複製 */
Thread_join(NULL);

/* 安全的版本 */
{
    struct args args;
    Sem_T mutex;
    Sem_init(&mutex, 1);
    args.mutex = &mutex;
    args.ip = &n;
    for (i = 0; i < m; i++)
        Thread_new(safe, &args, sizeof args, NULL);
    Thread_join(NULL);
}
```

**執行結果**（每次都不一樣）：

```
% spin
87102 == 150000      ← unsafe：結果錯誤，而且每次都不同
150000 == 150000     ← safe：正確
% spin
148864 == 150000
150000 == 150000
```

> **為什麼 unsafe 是錯的？** `*ip = *ip + 1` 如果在**讀取 `*ip` 之後**被中斷，這時其他執行緒遞增了 `*ip`，等它恢復執行時**寫回的就是舊值加 1**，其他執行緒的遞增全部遺失。這就是經典的**競爭條件（race condition）**。
>
> **在搶占式系統中，任何可能被多個執行緒存取的資料都必須受到保護**，存取只能發生在一次只允許一個執行緒的臨界區域裡。

注意兩個呼叫的第三個參數：
- `Thread_new(unsafe, &n, 0, NULL)`：nbytes = 0，所以**直接傳遞 &n**，大家共用同一個 n。
- `Thread_new(safe, &args, sizeof args, NULL)`：**複製** args 結構，但結構裡的指標仍然指向同一個 mutex 和 n。

### 6.3 ⭐ 質數篩選管線 `sieve`

**埃拉托斯特尼篩法**的管線實作：每個「篩子」是一個執行緒，負責丟掉自己那些質數的倍數，**用通道把執行緒串成管線**。

```
% sieve 100
2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
```

```
 source ──→ filter ──→ filter ──→ sink
 2,3,5,…    [2,3,5,     [13,17,19,  [31,37]
             7,11]       23,29]
```

- **source**：產生 2，接著是所有奇數，送進管線。
- **filter**：丟掉自己質數的倍數，其他的往下傳。
- **sink**：也過濾自己的質數；**能通過 sink 篩選的數字就是質數**。
- 每個 filter 和 sink 存放 **n 個質數**（預設 5）。**sink 收集滿 n 個質數後，就產生一個新的 sink，自己變成 filter**，所以管線會**動態成長**。

```c
struct args {
    Chan_T c;
    int n, last;       /* 每個篩子的質數個數、要算到多大 */
};

int main(int argc, char *argv[]) {
    struct args args;
    Thread_init(1, NULL);
    args.c = Chan_new();
    Thread_new(source, &args, sizeof args, NULL);
    args.n    = argc > 2 ? atoi(argv[2]) : 5;
    args.last = argc > 1 ? atoi(argv[1]) : 1000;
    Thread_new(sink,   &args, sizeof args, NULL);
    Thread_exit(EXIT_SUCCESS);       /* main 自己結束，讓其他執行緒繼續 */
    return EXIT_SUCCESS;
}

int source(void *cl) {
    struct args *p = cl;
    int i = 2;
    if (Chan_send(p->c, &i, sizeof i))
        for (i = 3; Chan_send(p->c, &i, sizeof i); )   /* 接收端讀 0 個位元組時就停止 */
            i += 2;
    return EXIT_SUCCESS;
}

void filter(int primes[], Chan_T input, Chan_T output) {
    int j, x;
    for (;;) {
        Chan_receive(input, &x, sizeof x);
        for (j = 0; primes[j] != 0 && x%primes[j] != 0; j++)   /* primes 以 0 結尾 */
            ;
        if (primes[j] == 0)                       /* 不是任何一個質數的倍數 */
            if (Chan_send(output, &x, sizeof x) == 0)
                break;                            /* 下游讀了 0 個位元組 → 結束 */
    }
    Chan_receive(input, &x, 0);                   /* 通知上游：讀 0 個位元組 */
}

int sink(void *cl) {
    struct args *p = cl;
    Chan_T input = p->c;
    int i = 0, j, x, primes[256];
    primes[0] = 0;
    for (;;) {
        Chan_receive(input, &x, sizeof x);
        for (j = 0; primes[j] != 0 && x%primes[j] != 0; j++)
            ;
        if (primes[j] == 0) {                     /* x 是質數 */
            if (x > p->last)
                break;                            /* 超過範圍，結束 */
            Fmt_print(" %d", x);
            primes[i++] = x;
            primes[i] = 0;
            if (i == p->n) {                      /* 收集滿了：分裂 */
                p->c = Chan_new();
                Thread_new(sink, p, sizeof *p, NULL);   /* 新的 sink */
                filter(primes, input, p->c);            /* 自己變成 filter */
                return EXIT_SUCCESS;
            }
        }
    }
    Fmt_print("\n");
    Chan_receive(input, &x, 0);                   /* 通知上游結束 */
    return EXIT_SUCCESS;
}
```

**⭐ 優雅的結束協定**：
1. sink 印完所有質數後，**從輸入通道讀 0 個位元組**。
2. 上游的 filter 看到 `Chan_send` 回傳 **0**，就知道下游結束了，於是自己也讀 0 個位元組，然後結束。
3. 這個訊號**一路往上傳**，直到 source 發現它的接收端讀了 0 個位元組，就結束。

> **這就是 Chan 回傳「接收端接受的位元組數」的用處**：用 size = 0 的傳輸當作「關閉」訊號。

**⭐ 搶占式和非搶占式都能用**：
> sieve 中所有的執行緒切換都發生在 `Chan_send` 和 `Chan_receive` 裡，而且**永遠至少有一個執行緒準備好執行**。所以 sieve 在**搶占式和非搶占式**排程下都能正確運作，是**主要用執行緒來組織應用程式結構**的簡單範例。
> **非搶占式的執行緒常被稱為協程（coroutine）。**

---

## 7. 實作（20.3 Implementations）

### 7.1 實作的分層

```
Chan  ──建立在──→  Sem  ──依賴內部──→  Thread
（和機器無關）     （和機器無關，但      （大致和機器、OS 無關，
                    由 thread.c 實作）    只有 context switch 和搶占例外）
```

- **Chan** 完全建立在 Sem 之上，所以和機器無關。
- **Sem** 也和機器無關，但它依賴 Thread 實作的內部，所以**由 thread.c 一起實作**。
- **單處理器的 Thread** 實作可以大致做到和機器、作業系統無關：**只有 context switch 和搶占**的程式碼會牽涉到機器和 OS 的相依性。

### 7.2 ⭐ Chan 的實作：用三個信號量

```c
struct T {
    const void *ptr;      /* 傳送端的資料 */
    int *size;            /* 指向傳送端的 size，讓接收端可以回寫 */
    Sem_T send, recv, sync;
};

T Chan_new(void) {
    T c;
    NEW(c);
    Sem_init(&c->send, 1);    /* 1：可以傳送 */
    Sem_init(&c->recv, 0);    /* 0：還沒有訊息 */
    Sem_init(&c->sync, 0);    /* 0：還沒有複製完成 */
    return c;
}
```

| 信號量 | 意義 |
|---|---|
| **send** | 1 = 傳送端**可以**設定 ptr 和 size；0 = 不行（例如接收端還沒取走訊息） |
| **recv** | 1 = ptr 和 size **有效**（有訊息可以接收）；0 = 沒有 |
| **sync** | 1 = 接收端已經**把訊息複製到自己的緩衝區**；保證傳輸是**同步**的 |

send 和 recv **交替**：一個是 1 時另一個是 0。

```c
int Chan_send(Chan_T c, const void *ptr, int size) {
    assert(c);
    assert(ptr);
    assert(size >= 0);
    Sem_wait(&c->send);       /* ① 等待可以傳送 */
    c->ptr = ptr;             /* ② 放上訊息 */
    c->size = &size;          /*    注意：存的是 size 的「位址」 */
    Sem_signal(&c->recv);     /* ③ 通知接收端 */
    Sem_wait(&c->sync);       /* ④ 等待接收端複製完 */
    return size;              /* ⑤ size 已經被接收端改成實際接收的位元組數 */
}

int Chan_receive(Chan_T c, void *ptr, int size) {
    int n;
    assert(c);
    assert(ptr);
    assert(size >= 0);
    Sem_wait(&c->recv);       /* ① 等待訊息 */
    n = *c->size;
    if (size < n)
        n = size;             /*    取兩者比較小的 */
    *c->size = n;             /* ② 回寫給傳送端：實際接收了多少 */
    if (n > 0)
        memcpy(ptr, c->ptr, n);
    Sem_signal(&c->sync);     /* ③ 通知傳送端：複製完成 */
    Sem_signal(&c->send);     /* ④ 允許下一次傳送 */
    return n;
}
```

**巧妙之處**：
- **`c->size` 存的是傳送端區域變數 size 的位址**，接收端可以**直接修改**它，傳送端就從自己的 size 拿到實際接收的位元組數。這之所以安全，是因為**傳送端會一直阻塞在 `Sem_wait(&c->sync)`**，它的堆疊框架在那之前都有效。
- 程式碼同時處理三種情況：傳送端的 size 大於、等於、小於接收端的 size。

### 7.3 執行緒控制區塊與佇列

```c
struct T {
    unsigned long *sp;        /* 堆疊指標，⭐ 必須是第一個欄位 */
    T link;                   /* 佇列的鏈結 */
    T *inqueue;               /* 指向所在的佇列變數 */
    T handle;                 /* 指向自己：用來驗證 handle 是否有效 */
    Except_Frame *estack;     /* 這個執行緒的例外堆疊 */
    int code;                 /* 結束碼 */
    T join;                   /* 等待這個執行緒結束的佇列 */
    T next;                   /* freelist 的鏈結 */
    int alerted;              /* alert-pending 旗標 */
};
```

- 這個結構常被稱為**執行緒控制區塊（thread control block）**。
- **`sp` 必須是第一個欄位**：組合語言程式碼要存取它，放在最前面就不受結構大小和其他欄位位置影響，**之後加新欄位也不用修改組合語言程式碼**。
- **`handle` 指向自己**：t 是存在的執行緒 ⇔ **`t == t->handle`**；執行緒結束時把 handle 清成 NULL。

**⭐ 佇列的不變式**：
> **一個執行緒要嘛不在任何佇列上，要嘛剛好在一個佇列上。**
> 這個設計讓佇列**完全不需要配置空間**：不用 Seq_T，而是直接用 `link` 欄位把 Thread_T 串成**環狀串列**。

```c
static T ready = NULL;        /* 就緒佇列：可以執行但沒有處理器的執行緒 */
#define isempty(q) ((q) == NULL)
```

```
  ready ──────────────────────────┐
                                  ↓
      ┌──→ [A] ──→ [B] ──→ [C] ──┐
      └──────────────────────────┘
  （ready 指向最後一個 C；C->link 就是第一個 A）
```

```c
static void put(T t, T *q) {          /* 加到佇列尾端 */
    assert(t);
    assert(t->inqueue == NULL && t->link == NULL);   /* 不能已經在佇列上 */
    if (*q) {
        t->link = (*q)->link;
        (*q)->link = t;
    } else
        t->link = t;
    *q = t;
    t->inqueue = q;
}

static T get(T *q) {                  /* 取出佇列的第一個 */
    T t;
    assert(!isempty(*q));             /* ⭐ ready 是空的就是死結 */
    t = (*q)->link;
    if (t == *q)
        *q = NULL;
    else
        (*q)->link = t->link;
    assert(t->inqueue == q);
    t->link = NULL;
    t->inqueue = NULL;
    return t;
}

static void delete(T t, T *q);        /* 從佇列中間移除，給 Thread_alert 用 */
```

**⭐ 死結偵測**：`run` 被呼叫但 ready 是空的，就代表**沒有任何可以執行的執行緒**，也就是死結。這是 checked runtime error，**在 `get` 的 assert 中偵測**。

### 7.4 初始化

```c
static T current;             /* 目前持有處理器的執行緒 */
static int nthreads;          /* 存在的執行緒數 */
static struct Thread_T root;  /* 根執行緒（main）：靜態配置 */

int Thread_init(int preempt, ...) {
    assert(preempt == 0 || preempt == 1);
    assert(current == NULL);          /* 只能呼叫一次 */
    root.handle = &root;
    current = &root;
    nthreads = 1;
    if (preempt) {
        /* initialize preemptive scheduling */
    }
    return 1;
}

T Thread_self(void) {
    assert(current);                  /* current 是 NULL 代表還沒初始化 */
    return current;
}
```

用 `current` 是否為 NULL，同時實作了兩個 checked error：**只能初始化一次**，以及**必須先初始化**。

### 7.5 ⭐ Context switch：`_swtch` 和 `run`

```c
extern void _swtch(T from, T to);     /* 用組合語言實作 */
```

> `_swtch` 很像 setjmp/longjmp：執行緒 A 呼叫 `_swtch` 時，控制權轉移到 B；**B 之後呼叫 `_swtch` 恢復 A 時，A 的那次 `_swtch` 呼叫才返回**。所以 A 和 B 都把 `_swtch` **當成一般的函式呼叫**。
>
> 這個簡單的設計**利用了機器的呼叫慣例**來保存 A 的狀態。唯一的缺點是：**新執行緒必須被建立成「看起來像是呼叫過 `_swtch`」的狀態**，因為它第一次執行就是從 `_swtch` 返回。

```c
static void run(void) {               /* 唯一呼叫 _swtch 的地方 */
    T t = current;
    current = get(&ready);            /* 取出下一個要執行的 */
    t->estack = Except_stack;         /* ⭐ 保存目前執行緒的例外堆疊 */
    Except_stack = current->estack;   /*    換成新執行緒的例外堆疊 */
    _swtch(t, current);
}

void Thread_pause(void) {
    assert(current);
    put(current, &ready);             /* 把自己放回 ready */
    run();                            /* 切換到下一個 */
}
```

> **例外狀態是每個執行緒各自的**，所以 context switch 時要**切換第 4 章的全域 `Except_stack`**，這就是「例外是執行緒專屬的」在實作上的意義。

只有一個執行緒時，`Thread_pause` 會把它放進 ready 再取出來，所以 **`_swtch(t, t)` 也必須正確運作**。

**三個執行緒的切換範例**（A 一開始持有處理器，ready = [B C]）：

| 時間 | 執行中 | 呼叫 | ready |
|---|---|---|---|
| 1 | A | `Thread_pause()` → `_swtch(A,B)` | [C A] |
| 2 | B | `Thread_pause()` → `_swtch(B,C)` | [A B] |
| 3 | C | `Thread_pause()` → `_swtch(C,A)` | [B C] |
| 4 | A | `Thread_join(C)` → `_swtch(A,B)`，A 進入 C 的 join 佇列 | [C] |
| 5 | B | `Thread_exit(0)` → `_swtch(B,C)` | [] |
| 6 | C | `Thread_exit(0)` → A 被放回 ready，`_swtch(C,A)` | [] |
| 7 | A | `Thread_exit(0)` → 只剩 A，所以呼叫 `exit(0)` | |

### 7.6 `Thread_join` 和 `Thread_exit`

```c
int Thread_join(T t) {
    assert(current && t != current);
    testalert();                              /* 阻塞前檢查 alert */
    if (t) {
        if (t->handle == t) {                 /* t 存在 */
            put(current, &t->join);           /* 進入 t 的 join 佇列 */
            run();
            testalert();                      /* 恢復後檢查 alert */
            return current->code;             /* t 結束時寫進來的結束碼 */
        } else
            return -1;
    } else {
        assert(isempty(join0));               /* 只能有一個 */
        if (nthreads > 1) {
            put(current, &join0);             /* 等待所有其他執行緒 */
            run();
            testalert();
        }
        return 0;
    }
}

static T join0;            /* 等待「所有其他執行緒」的那一個執行緒 */
static T freelist;

void Thread_exit(int code) {
    assert(current);
    release();                                /* 釋放之前結束的執行緒 */
    if (current != &root) {
        current->next = freelist;             /* ⭐ 延後釋放自己 */
        freelist = current;
    }
    current->handle = NULL;                   /* 標記成不存在 */
    while (!isempty(current->join)) {         /* 喚醒等待我的執行緒 */
        T t = get(&current->join);
        t->code = code;                       /* 把結束碼複製給它們 */
        put(t, &ready);
    }
    if (!isempty(join0) && nthreads == 2) {   /* 只剩我和 join0 裡的那一個 */
        assert(isempty(ready));
        put(get(&join0), &ready);
    }
    if (--nthreads == 0)
        exit(code);                           /* 最後一個執行緒 */
    else
        run();
}
```

**⭐ 延後釋放**：
> `Thread_exit` **不能釋放目前執行緒的堆疊，因為它正在使用那個堆疊！** 所以先把自己加到 `freelist`，**等到下一次呼叫 `release` 時才釋放**（由下一個執行 `Thread_exit` 或 `Thread_new` 的執行緒負責）。
> 根執行緒是**靜態配置**的，所以不能釋放。

**結束碼複製到等待者的 `code` 欄位**，這樣結束的執行緒就可以被釋放。

### 7.7 `Thread_alert` 和 `testalert`

```c
void Thread_alert(T t) {
    assert(current);
    assert(t && t->handle == t);
    t->alerted = 1;
    if (t->inqueue) {                 /* 如果 t 在阻塞（在某個佇列上）*/
        delete(t, t->inqueue);        /* 從那個佇列移除 */
        put(t, &ready);               /* 放到 ready */
    }
}

static void testalert(void) {
    if (current->alerted) {
        current->alerted = 0;
        RAISE(Thread_Alerted);        /* 只有執行緒「自己」能丟出例外 */
    }
}

const Except_T Thread_Alerted = { "Thread alerted" };
```

> `Thread_alert` **本身不能丟出 `Thread_Alerted`**，因為呼叫它的執行緒和 t 處於不同的狀態。**執行緒必須自己丟出並處理 `Thread_Alerted`**，這就是 `testalert` 的用途：在**即將阻塞時**和**阻塞後恢復時**呼叫。

### 7.8 `Thread_new` 和堆疊配置

```c
T Thread_new(int apply(void *), void *args, int nbytes, ...) {
    T t;
    assert(current);
    assert(apply);
    assert(args && nbytes >= 0 || args == NULL);
    if (args == NULL)
        nbytes = 0;
    {   /* allocate resources for a new thread */
        int stacksize = (16*1024+sizeof (*t)+nbytes+15)&~15;   /* 16KB 堆疊 */
        release();
        do { critical++;                   /* begin critical region */
        TRY
            t = ALLOC(stacksize);          /* 控制區塊和堆疊一起配置 */
            memset(t, '\0', sizeof *t);
        EXCEPT(Mem_Failed)
            t = NULL;
        END_TRY;
        critical--; } while (0);           /* end critical region */
        if (t == NULL)
            RAISE(Thread_Failed);          /* 離開臨界區域之後才丟出 */
        t->sp = (void *)((char *)t + stacksize);
        while (((unsigned long)t->sp)&15)
            t->sp--;                       /* 對齊 16 位元組（DEC ALPHA 需要）*/
    }
    t->handle = t;
    /* initialize t's state：複製 args 到堆疊底部，再建立假的 _swtch 框架 */
    nthreads++;
    put(t, &ready);
    return t;
}
```

```
  t ──→ ┌──────────────────┐  ← Thread_T 結構
        │  thread control  │
        │      block       │
        ├──────────────────┤
        │                  │
        │   16KB 堆疊空間    │  ↓ 堆疊往低位址成長
        │                  │
        ├──────────────────┤  ← t->sp
        │  _swtch 框架      │  ← 假裝曾經呼叫過 _swtch
        │  startup 框架     │  ← 存放 apply 和 args
        │  args 的複本      │
        └──────────────────┘
```

**⭐ 為什麼要自己捕捉 `Mem_Failed`？**
> 如果不捕捉，控制權會傳到**呼叫端**的例外處理程式，而 **`critical` 會停留在正數，永遠不會被遞減**，之後所有的計時器中斷都會被忽略。所以必須先離開臨界區域，**再**丟出 `Thread_Failed`。

**機器相依的部分**：用條件編譯為 **ALPHA、MIPS、SPARC** 建立不同的初始堆疊框架。

> **`thread.c` 和 `swtch.s` 是本書唯一使用條件編譯的模組。** 呼應第 1 章「盡量避免條件編譯」的主張：真的無法避免時，就把它**限制在最小的範圍**內。

### 7.9 SPARC 的 `_swtch`

```asm
__swtch: save  %sp,-(8+64),%sp     ! 1 配置框架
         st    %fp,[%sp+64+0]      ! 2 保存 from 的 frame pointer
         st    %i7,[%sp+64+4]      ! 3 保存 from 的返回位址
         ta    3                   ! 4 flush from 的暫存器視窗（系統呼叫！）
         st    %sp,[%i0]           ! 5 保存 from 的堆疊指標到 from->sp
         ld    [%i1],%sp           ! 6 ⭐ 載入 to 的堆疊指標：真正的 context switch
         ld    [%sp+64+0],%fp      ! 7 恢復 to 的 frame pointer
         ld    [%sp+64+4],%i7      ! 8 恢復 to 的返回位址
         ret                       ! 9 繼續執行 to
         restore                   ! 10
```

- **第 6 行就是真正的 context switch**：載入 to 的堆疊指標之後，`_swtch` 就在 **to 的堆疊**上執行了。
- 第 5 行說明了 **`sp` 為什麼必須是第一個欄位**：`[%i0]` 就是 `from->sp`，和結構的其他部分無關。
- **SPARC 的遺憾**：第 4 行需要**系統呼叫**來 flush 暫存器視窗，而使用者層級執行緒原本的優點之一，就是 context switch **不需要核心介入**。

**新執行緒的啟動**：

```asm
__start: ld    [%sp+64+4],%o0      ! 載入 args 當第一個參數
         ld    [%sp+64],%o1        ! 載入 apply 的位址
         call  %o1; nop            ! 呼叫 apply(args)
         call  _Thread_exit; nop   ! apply 的回傳值就是 Thread_exit 的參數
         unimp 0                   ! 不應該執行到這裡
```

`Thread_new` 建立的 `_swtch` 框架中，返回位址指向 `_start`，所以**第一次從 `_swtch` 返回時就落到 `_start`**，接著呼叫 `apply(args)`，再呼叫 `Thread_exit`。

### 7.10 ⭐ 搶占：計時器中斷

> **搶占等同於週期性地、隱含地呼叫 `Thread_pause`。**

```c
/* initialize preemptive scheduling */
{
    struct sigaction sa;
    memset(&sa, '\0', sizeof sa);
    sa.sa_handler = (void (*)())interrupt;
    if (sigaction(SIGVTALRM, &sa, NULL) < 0)   /* 虛擬計時器 signal */
        return 0;                               /* 不支援 → 非搶占式 */
}
{
    struct itimerval it;
    it.it_value.tv_sec     = 0;
    it.it_value.tv_usec    = 50;
    it.it_interval.tv_sec  = 0;
    it.it_interval.tv_usec = 50;
    if (setitimer(ITIMER_VIRTUAL, &it, NULL) < 0)
        return 0;
}
```

- 用 UNIX 的 **`SIGVTALRM`** 加上 **`ITIMER_VIRTUAL`** 虛擬計時器。**虛擬**的意思是只在**行程執行時**才計時。
- 書中說每 **50 毫秒**中斷一次。（⚠ 注意：`tv_usec` 的單位其實是**微秒**，所以程式碼寫的 50 實際上是 50 微秒；要 50 毫秒應該寫 50000。）

```c
static int interrupt(int sig, int code, struct sigcontext *scp) {
    if (critical ||
        scp->sc_pc >= (unsigned long)_MONITOR
     && scp->sc_pc <= (unsigned long)_ENDMONITOR)
        return 0;                      /* ⭐ 在 Thread/Sem 函式裡：忽略這次中斷 */
    put(current, &ready);
    sigsetmask(scp->sc_mask);          /* 恢復被中斷停用的 signal */
    run();
    return 0;
}
```

**⭐ 保證 Thread 函式是原子的：兩個機制**

| 機制 | 處理的情況 |
|---|---|
| **`_MONITOR` / `_ENDMONITOR`** | 中斷發生時，**程式計數器在 Thread 或 Sem 函式裡** |
| **`critical` 計數器** | 中斷發生時，正在 Thread 函式**呼叫的其他函式**裡，例如 `ALLOC`、`memset`、`FREE` |

- `thread.c` 的**開頭**定義一個空函式 `_MONITOR`，`swtch.s` 的**結尾**定義 `_ENDMONITOR`。
- 只要連結時 `swtch.s` 的目的碼**緊接在** `thread.c` 後面，**程式計數器落在兩者之間就代表在 Thread 或 Sem 函式裡**，這時就忽略中斷。
- 這個技巧來自 Cormack (1988)。

**為什麼需要 `sigsetmask`？**
中斷處理期間 `SIGVTALRM` 被停用。如果下一個要執行的執行緒 A **不是被中斷暫停的**（例如是自己呼叫 `Thread_pause` 的），它就不會經過中斷處理程式的返回，**`SIGVTALRM` 會一直保持停用**。所以切換前要先恢復 signal 遮罩。

### 7.11 ⭐ 公平的信號量

```c
T *Sem_new(int count) {
    T *s;
    NEW(s);
    Sem_init(s, count);
    return s;
}

void Sem_init(T *s, int count) {
    assert(current);
    assert(s);
    s->count = count;
    s->queue = NULL;
}
```

**簡潔、正確，但不公平的版本：**

```c
void Sem_wait(T *s) {
    while (s->count <= 0) {
        put(current, &s->queue);
        run();
    }
    --s->count;
}

void Sem_signal(T *s) {
    if (++s->count > 0 && !isempty(s->queue))
        put(get(&s->queue), &ready);
}
```

**⚠ 飢餓（starvation）問題**：s 初始值是 1，A 和 B 都在迴圈裡 wait → 臨界區域 → signal。
1. A 在臨界區域裡，B 在 `s->queue` 上。
2. A 呼叫 `Sem_signal`，B 被移到 ready。
3. **但 A 可能比 B 先呼叫 `Sem_wait`，又搶到了臨界區域。**
4. A 在臨界區域裡被搶占，B 恢復執行，卻發現 `s->count` 是 0，**又被放回 `s->queue`**。
5. B 可能**無限期地**在 ready 和 `s->queue` 之間循環。競爭的執行緒越多，飢餓越容易發生。

**公平的版本：直接把信號量「交給」被喚醒的執行緒**

```c
void Sem_wait(T *s) {
    assert(current);
    assert(s);
    testalert();
    if (s->count <= 0) {
        put(current, (Thread_T *)&s->queue);
        run();
        testalert();
        /* ⭐ 被喚醒後「不」遞減 count，因為 signal 時也沒有遞增 */
    } else
        --s->count;
}

void Sem_signal(T *s) {
    assert(current);
    assert(s);
    if (s->count == 0 && !isempty(s->queue)) {
        Thread_T t = get((Thread_T *)&s->queue);
        assert(!t->alerted);
        put(t, &ready);
        /* ⭐ 「不」遞增 count，直接把信號量交給 t */
    } else
        ++s->count;
}
```

> **概念**：計數器**要從 0 變成 1** 時，不真的遞增，而是**直接把佇列上的執行緒移到 ready**；被喚醒的執行緒也**不遞減**計數器。這樣**被喚醒的執行緒保證會拿到信號量**，因為 count 一直是 0，其他呼叫 `Sem_wait` 的執行緒都會阻塞。

**Alert 讓 `Sem_wait` 比較難懂**：阻塞在 s 上的執行緒被 alert 時，它是被 `Thread_alert` 移到 ready 的，**和 `Sem_signal` 無關**，也和 `s->count` 無關。所以它必須**不動 s**，清除旗標，然後丟出 `Thread_Alerted`，這正是第二個 `testalert` 的作用。

---

## 8. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **三個小介面，各司其職** | Thread（建立和管理）、Sem（同步）、Chan（通訊） |
| **原子性** | 所有 Thread 函式都是原子的，用 `_MONITOR`/`_ENDMONITOR` 加上 `critical` 保證 |
| **參數複製** | `Thread_new` 複製 args，呼叫端可以馬上重複使用 |
| **例外是執行緒專屬的** | context switch 時切換 `Except_stack` |
| **協作式終止** | 沒有強制終止；用 alert 加上例外 |
| **公開但不透明** | Sem_T 公開結構，只是為了能靜態配置或內嵌 |
| **LOCK 巨集** | 避免忘記 signal 或 signal 錯的信號量；有例外時改用 TRY-FINALLY |
| **同步通道 + 0 位元組協定** | 用 size = 0 的傳輸當作關閉訊號，一路往上游傳遞 |
| **不需配置的佇列** | 「最多在一個佇列上」的不變式，讓佇列直接用 `link` 欄位串成環狀串列 |
| **延後釋放** | 不能釋放正在使用的堆疊，所以放進 freelist 等下一次 release |
| **公平性** | 直接交接信號量，避免飢餓 |
| **最小化機器相依** | 只有 `_swtch`、`_start` 和堆疊初始化是組合語言或條件編譯 |
| **把 context switch 當成函式呼叫** | 利用機器的呼叫慣例保存狀態 |

### 回顧全書的模組在本章的角色

| 模組 | 在 Thread 中的用途 |
|---|---|
| **Except**（第 4 章） | `Thread_Failed`、`Thread_Alerted`；每個執行緒各自的例外堆疊 |
| **Mem**（第 5 章） | 配置控制區塊和堆疊 |
| **Fmt**（第 14 章） | 範例的輸出（但要注意可重入性） |
| **Table**（第 8 章） | 用 mutex 保護的範例 |

---

## 9. 延伸閱讀重點

- **Andrews (1991)**：並行程式設計的完整教科書，包括同步機制、訊息傳遞系統、遠端程序呼叫，以及四種為並行設計的程式語言。
- **Thread 介面以 Modula-3 的執行緒介面為基礎**，而 Modula-3 的介面來自 DEC SRC 的 Modula-2+ 經驗。**Nelson (1991) 第 4 章由 Andrew Birrell 撰寫，是執行緒程式設計的指南，所有寫執行緒程式的人都會受益。** 大多數現代作業系統的執行緒功能都以某種方式源自 SRC 的介面。
- **Tanenbaum (1995)**：使用者層級和核心層級執行緒的設計議題，以及 Amoeba、Chorus、Mach 和 DCE 的個案研究。
- **Kleiman, Shah & Smaalders (1996)**：POSIX threads 和 Solaris 2 執行緒的實務書籍，有執行緒和函式庫互動的章節、平行化演算法（包括排序）的範例，以及串列、佇列、雜湊表的執行緒安全實作。
- **sieve 改編自 McIlroy (1968)** 用來說明**協程**的範例。Icon 的 **coexpression** 是協程的一種；**Marlin (1980)** 整理了許多原始的協程提案。
- **通道源自 CSP**（Hoare, 1978）。**Newsqueak** 也有執行緒和通道，而且能**非決定性地同時等待多個通道**，比 Chan 更強大。**Pike (1990)** 介紹了 Newsqueak 直譯器的實作，包括用亂數改變搶占頻率，讓排程變成非決定性但公平；**McIlroy (1990)** 用 Newsqueak 把冪級數當成資料流處理。Newsqueak 被用來實作**視窗系統**，這正是最能受益於執行緒的互動式應用。（Newsqueak 是 Go 語言的先驅之一。）
- **NeWS** 視窗系統的核心是一個 PostScript 直譯器，它的 PostScript 變體有非搶占式執行緒的擴充。
- **Concurrent ML**（Reppy, 1997）：支援和 Chan 很像的執行緒與同步通道。在 Standard ML 裡**沒有堆疊**（活動記錄可以比呼叫者活得更久），所以不需要特別的安排就能支援執行緒，Concurrent ML 完全用 Standard ML 實作。
- **Cormack (1988)**：`_MONITOR`/`_ENDMONITOR` 技巧的來源。**Stevens (1992)** 第 10 章：signal 和 signal 處理程序的完整說明。

---

## 10. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 20.1 | 為**二元信號量（lock/mutex）**設計一個獨立的介面，實作比一般信號量簡單 | 小心處理 alert |
| 20.2 | A 鎖了 x 再要鎖 y，B 鎖了 y 再要鎖 x → **死結**；擴充 20.1 的實作來偵測這種簡單的死結 | 等待圖的環偵測 |
| 20.3 | **不用信號量**、直接用內部的佇列和執行緒函式重新實作 Chan | 量測效益，要有多少訊息量才有明顯差別？ |
| 20.4 | 設計**非同步、有緩衝**的通訊：傳送端不用等，訊息可以比傳送端執行緒活得更久 | 緩衝訊息的儲存管理；如何知道訊息是否被收到 |
| 20.5 | 實作 Modula-3 的**條件變數**：`sleep(m, c)`、`wakeup(c)`、`broadcast(c)`、`alertsleep` | 用 20.1 的 lock |
| 20.6 | 用**非阻塞 I/O** 系統呼叫建立執行緒安全的標準 I/O 函式庫 | 一個執行緒等待輸入時，其他執行緒可以繼續執行 |
| 20.7 | **不用 `_MONITOR`/`_ENDMONITOR`** 讓 Thread 和 Sem 函式變成原子的 | 一個全域旗標不夠，需要每個執行緒各自的旗標，組合語言也要修改它；**非常容易出現細微的錯誤** |
| 20.8 | 讓 `Thread_new` 接受指定堆疊大小的選用參數，例如 `"stacksize", 4096` | |
| 20.9 | 加入少數幾個**優先等級**的支援 | Tanenbaum (1995) 說明了如何實作支援優先權的公平排程 |

---

## 11. 本章重點整理

1. **三個小介面**：Thread（init/new/exit/join/self/pause/alert）、Sem（init/new/wait/signal 和 LOCK）、Chan（new/send/receive）。
2. **Thread 是使用者層級執行緒**，支援搶占式和非搶占式；所有函式都是原子的。
3. **`Thread_new` 複製參數**；新執行緒的例外堆疊是空的；執行緒必須用 `Thread_exit` 結束。
4. **沒有強制終止**：用 `Thread_alert` 讓目標執行緒在阻塞點丟出 `Thread_Alerted`，由它自己決定怎麼結束。
5. **Sem 是公平的 FIFO 信號量**；LOCK-END_LOCK 處理一般的臨界區域，**可能丟出例外時要改用 TRY-FINALLY**。
6. **Chan 是同步的會合通道**；size = 0 的傳輸可以當作結束訊號。
7. **三個範例**：平行快速排序（cutoff 控制粒度；但有 Fmt_print 不可重入的 bug）、spin（競爭條件 vs. mutex）、sieve（動態成長的通道管線，搶占式和非搶占式都能用）。
8. **實作的關鍵**：
   - Chan 用三個信號量，加上傳送端 size 的位址。
   - 執行緒佇列用「最多在一個佇列上」的不變式串成環狀串列，不需要配置。
   - `_swtch` 把 context switch 變成一般的函式呼叫；`run` 同時切換例外堆疊。
   - `Thread_exit` 延後釋放自己的堆疊。
   - 搶占用 SIGVTALRM，並用 `_MONITOR`/`_ENDMONITOR` 加上 `critical` 保護原子性。
   - 公平的 Sem 直接把信號量交給被喚醒的執行緒，避免飢餓。

> **一句話**：用三個小而正交的介面（Thread、Sem、Chan）提供完整的使用者層級並行能力，實作上把機器相依的部分壓縮到幾十行組合語言，再用佇列不變式、延後釋放和直接交接等技巧，同時做到正確、公平和不需要額外配置。

---

## 🎓 全書總結

20 章走下來，Hanson 一再示範同一套方法：

1. **介面是合約**：寫清楚能做什麼、怎樣算用錯（checked 或 unchecked）、會丟出哪些例外、效能承諾是什麼。
2. **不透明指標加上命名慣例**（`T`、`Module_`、`_free(T *)`），讓實作可以替換。
3. **隱藏不是教條**：List、Text、XP、MP、Sem 都依需求公開表示方式。
4. **分層**：Mem 之上有 Arena；Array 之上有 Seq；XP 之上有 AP 和 MP；Sem 之上有 Chan。低層追求速度，高層提供安全。
5. **基礎設施優先**：Atom、Except、Assert、Mem 支撐所有後面的模組。
6. **一致的寫法**：閉包（`apply` + `cl`）、`toArray`、timestamp 檢查、指標的指標、`union align`。
7. **用範例程式驗證介面**：double、wf、xref、ids、calc、mpcalc、sort、spin、sieve。程式寫起來彆扭的地方（例如 calc 用 Stack 印出整個堆疊），就是介面需要改進的地方。
