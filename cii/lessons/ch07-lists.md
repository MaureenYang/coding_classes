# 第 7 章　Lists（串列）

> 《C Interfaces and Implementations》— David R. Hanson
> 本章頁碼：p.103–114

---

## 1. 本章定位

**串列**是零個或多個指標組成的序列：沒有指標的是**空串列**，指標的個數就是串列的**長度**。

- 幾乎每個有點規模的應用都會用到串列。LISP、Scheme、ML 甚至把它做成內建型別。
- 串列太容易實作，所以程式設計師通常**每個應用都重寫一次**，也一直沒有被廣泛接受的標準介面。
- `List` ADT 收集了大多數應用專屬串列介面共有的功能。
- 第 11 章的 Sequence 是表示串列的另一種方式。

**本章是資料結構部分的第一章**，也是全書**少數刻意公開表示方式**的 ADT，用來示範「什麼時候不該隱藏」。

---

## 2. 介面（7.1 Interface）

```c
/* list.h */
#ifndef LIST_INCLUDED
#define LIST_INCLUDED

#define T List_T
typedef struct T *T;

struct T {
    T rest;
    void *first;
};

extern T      List_append (T list, T tail);
extern T      List_copy   (T list);
extern T      List_list   (void *x, ...);
extern T      List_pop    (T list, void **x);
extern T      List_push   (T list, void *x);
extern T      List_reverse(T list);
extern int    List_length (T list);
extern void   List_free   (T *list);
extern void   List_map    (T list,
                  void apply(void **x, void *cl), void *cl);
extern void **List_toArray(T list, void *end);

#undef T
#endif
```

### 2.1 ⭐ 為什麼公開表示方式？

大多數 ADT 都會隱藏表示方式，**`List` 卻把 `struct T` 的定義直接放在介面裡**。作者的理由：

> 對這個 ADT 來說，**隱藏帶來的麻煩超過了好處**。

- `List_T` 的表示方式非常簡單，很難想像有哪種其他表示方式的實作能好到值得隱藏「元素是有兩個欄位的結構」這件事。
- **公開之後介面和使用都變簡單了**：
  1. 可以**靜態定義並初始化** `struct List_T` 變數，在編譯期就建好串列，不用配置記憶體。
  2. 其他結構可以**內嵌** `struct List_T`。
  3. **NULL 的 `List_T` 就是空串列**，這是最自然的表示方式。
  4. 存取 `first`、`rest` **不需要函式**。

> 這是第 2 章「封裝 vs. 方便」取捨的具體案例：**隱藏不是教條**，要看值不值得。

### 2.2 通則

- **所有函式都接受 NULL 的 `T`**，並把它當成空串列。
- 唯一的 checked runtime error：傳 NULL 的指標給 `List_free`。

### 2.3 建立串列：`List_list` 與 `List_push`

```c
List_T p1, p2;
p1 = List_list(NULL);                                   /* 空串列 */
p2 = List_list("Atom", "Mem", "Arena", "List", NULL);   /* 4 個節點 */
```

- `List_list` 接受 N 個非 NULL 指標加上**一個 NULL 結尾**，建立 N 個節點的串列。
- **⚠ 可變參數的陷阱**：可變參數部分**沒有原型提供隱含轉換**，所以傳 `char *` 和 `void *` 以外的指標時，**必須自己轉型**：

```c
p = List_list(List_list("Atom", NULL),
      (void *)List_list("Mem",   NULL),     /* 必須轉型！ */
      (void *)List_list("Arena", NULL),
      (void *)List_list("List",  NULL), NULL);
```

漏掉轉型是 **unchecked runtime error**。這是可變長度參數的典型陷阱。（第一個參數有原型 `void *x`，所以不用轉型。）

```c
/* 用 List_push 建立同樣的串列（從尾端往前推）*/
p2 = List_push(NULL, "List");
p2 = List_push(p2,   "Arena");
p2 = List_push(p2,   "Mem");
p2 = List_push(p2,   "Atom");
```

`List_push(list, x)` 在**開頭**加一個節點，回傳新串列。

### 2.4 其他操作

| 函式 | 功能 | 備註 |
|---|---|---|
| `List_pop(list, &x)` | 移除第一個節點，把它的 `first` 存到 `*x`（`x` 不是 NULL 時），回傳剩下的串列 | 空串列就直接回傳，不改 `*x` |
| `List_append(list, tail)` | 把 `tail` 接到 `list` 最後一個 `rest` | `list` 是 NULL 就回傳 `tail` |
| `List_reverse(list)` | **原地**反轉 | |
| `List_copy(list)` | 複製一份 | **applicative**（不修改原串列） |
| `List_length(list)` | 節點數 | |
| `List_free(&list)` | 釋放所有**節點**並把 `*list` 設成 NULL | 不釋放 `first` 指向的資料 |

**破壞性 vs. applicative**：
- 大多數函式是**破壞性的（nonapplicative）**，可能修改傳入的串列，再回傳結果。
- `List_copy` 是 **applicative** 的，回傳一份新的複本。

```c
p2 = List_append(p2, List_list("Except", NULL));  /* Atom Mem Arena List Except */
p2 = List_reverse(p2);                            /* Except List Arena Mem Atom */
List_T p3 = List_reverse(List_copy(p2));          /* p3 是正序；p2 不變 */
```

### 2.5 ⭐ 閉包：`List_map`

```c
extern void List_map(T list, void apply(void **x, void *cl), void *cl);
```

- 對每個節點呼叫 `apply(&node->first, cl)`。
- **`apply` + `cl` 合稱閉包（closure）或回呼（callback）**：`apply` 指定操作，`cl` 是 client 自帶的、跟情境有關的資料。`List_map` 不知道 `cl` 是什麼，只負責轉交。
- 傳給 `apply` 的是 **`first` 欄位的指標**，所以 `apply` **可以修改**元素。
- `apply` **修改串列本身**（例如增刪節點）是 unchecked runtime error。

**範例一：把字串換成 atom 並印出來**

```c
void mkatom(void **x, void *cl) {
    char **str = (char **)x;
    FILE *fp = cl;
    *str = Atom_string(*str);
    fprintf(fp, "%s\n", *str);
}

List_map(p3, mkatom, stderr);
```

**範例二：釋放元素，再釋放串列**

```c
void applyFree(void **ptr, void *cl) {
    FREE(*ptr);
}

List_map(names, applyFree, NULL);   /* 先釋放資料 */
List_free(&names);                  /* 再釋放節點 */
```

> 這就是 C 模擬閉包的標準寫法：**函式指標 + `void *cl`**。之後 Table、Set、Ring 等所有容器的 `_map` 都用同一個模式。

### 2.6 `List_toArray`

```c
extern void **List_toArray(T list, void *end);
```

- 建立一個 **N+1** 個元素的陣列：前 N 個是串列的值，**第 N 個是 `end`**（通常是 NULL，當作哨兵）。
- **client 必須自己釋放**這個陣列。
- **空串列也會回傳一個 1 個元素的陣列**，永遠不回傳 NULL。

```c
int i;
char **array = (char **)List_toArray(p3, NULL);
qsort((void **)array, List_length(p3), sizeof (*array),
      (int (*)(const void *, const void *))compare);
for (i = 0; array[i]; i++)       /* 用 NULL 哨兵結束迴圈 */
    printf("%s\n", array[i]);
FREE(array);
```

> 轉成陣列之後就能用 `qsort` 等標準工具，**容器和演算法可以分開**。

---

## 3. 實作（7.2 Implementation）

### 3.1 `List_push`：最簡單的一個

```c
T List_push(T list, void *x) {
    T p;
    NEW(p);
    p->first = x;
    p->rest = list;
    return p;
}
```

### 3.2 ⭐ 指標的指標：`List_list`

```c
T List_list(void *x, ...) {
    va_list ap;
    T list, *p = &list;

    va_start(ap, x);
    for ( ; x; x = va_arg(ap, void *)) {
        NEW(*p);
        (*p)->first = x;
        p = &(*p)->rest;
    }
    *p = NULL;
    va_end(ap);
    return list;
}
```

**運作方式：**
- `p` 一開始指向 `list`，所以**第一個節點的指標會被指派給 `list`**。
- 之後 `p` 指向**最後一個節點的 `rest` 欄位**，所以對 `*p` 賦值就是**在尾端加節點**。

```
初始：  p → [list]
第 1 次：list → [A|·]      p → A.rest
第 2 次：list → [A|·]→[B|·] p → B.rest
第 3 次：list → [A|·]→[B|·]→[C|·]  p → C.rest
結束：  *p = NULL
```

- 迴圈遇到第一個 NULL 參數就結束，這個參數**也可能是第一個 `x`**，所以 `List_list(NULL)` 會正確回傳空串列（NULL）。

> **指標的指標（`List_T *`）的威力**：用**一個簡潔的機制**同時處理兩種情況：(1) 可能為空的串列的**第一個節點**；(2) 非空串列的**內部節點**。不需要「如果是第一個節點就……否則……」的特判。

### 3.3 `List_append`：同樣的技巧

```c
T List_append(T list, T tail) {
    T *p = &list;
    while (*p)
        p = &(*p)->rest;
    *p = tail;
    return list;
}
```

- `p` 一路走到串列尾端那個 NULL 指標的位置。
- 如果 `list` 本身是 NULL，`p` 就停在 `&list`，結果等於把 `tail` 接到空串列上，**自動正確**。

### 3.4 `List_copy`

```c
T List_copy(T list) {
    T head, *p = &head;
    for ( ; list; list = list->rest) {
        NEW(*p);
        (*p)->first = list->first;
        p = &(*p)->rest;
    }
    *p = NULL;
    return head;
}
```

### 3.5 `List_pop` 與 `List_reverse`：直接寫就好

指標的指標**對這兩個沒有幫助**，所以用比較直觀的寫法。

```c
T List_pop(T list, void **x) {
    if (list) {
        T head = list->rest;     /* 釋放前先存起來！ */
        if (x)
            *x = list->first;
        FREE(list);
        return head;
    } else
        return list;
}
```

注意：**一定要在釋放 `list` 之前先存下 `list->rest`**。

```c
T List_reverse(T list) {
    T head = NULL, next;
    for ( ; list; list = next) {
        next = list->rest;      /* 記住下一個 */
        list->rest = head;      /* 把目前的節點推到 head 前面 */
        head = list;
    }
    return head;
}
```

- `head` 永遠指向**已反轉部分**的第一個節點，`next` 指向 `list` 的下一個。
- 每輪把 `list` 指向的節點「推」到 `head` 前面，然後前進。
- 只走過一次，**原地反轉**，O(N) 時間、O(1) 空間。

### 3.6 `List_length`、`List_free`、`List_map`、`List_toArray`

```c
int List_length(T list) {
    int n;
    for (n = 0; list; list = list->rest)
        n++;
    return n;
}

void List_free(T *list) {
    T next;
    assert(list);
    for ( ; *list; *list = next) {
        next = (*list)->rest;
        FREE(*list);
    }
}

void List_map(T list, void apply(void **x, void *cl), void *cl) {
    assert(apply);
    for ( ; list; list = list->rest)
        apply(&list->first, cl);      /* 閉包函式做所有的事 */
}

void **List_toArray(T list, void *end) {
    int i, n = List_length(list);
    void **array = ALLOC((n + 1)*sizeof (*array));
    for (i = 0; i < n; i++) {
        array[i] = list->first;
        list = list->rest;
    }
    array[i] = end;
    return array;
}
```

**觀察：**
- `List_free` 直接用 `*list` 當迴圈變數，迴圈結束時 `*list` 自然就是 NULL，**順便達成「釋放後設成 NULL」**。
- `List_map` 聽起來很複雜，其實很簡單，因為**閉包函式做了所有的事**。
- `List_toArray` 對空串列配置 1 個元素的陣列，看似浪費，但這樣**永遠回傳非 NULL 的指標**，client 就不用檢查 NULL。

---

## 4. 設計觀念整理

| 觀念 | 本章體現 |
|---|---|
| **隱藏不是教條** | 表示方式簡單到沒有替代方案時，公開反而更好：可以靜態初始化、內嵌、NULL 即空串列 |
| **NULL 即空串列** | 所有函式都接受 NULL，介面一致而且自然 |
| **閉包模式** | `apply(void **x, void *cl)`，C 模擬高階函式的標準手法 |
| **破壞性 vs. applicative** | 大多數操作原地修改；`List_copy` 提供不修改原串列的選擇 |
| **指標的指標** | 消除「第一個節點」的特判，讓程式碼更短也更不容易錯 |
| **不回傳 NULL** | `List_toArray` 對空串列也回傳陣列 |
| **哨兵結尾** | `List_list(..., NULL)` 和 `List_toArray(list, NULL)` |
| **可變參數的陷阱** | 沒有原型就沒有隱含轉換，非 `char *` / `void *` 的指標要自己轉型 |

---

## 5. 延伸閱讀重點

- **Knuth (1973a)**：所有重要的單向串列演算法，以及雙向串列（第 12 章的 Ring）。
- LISP、Scheme、ML 等語言以串列為核心。**Abelson & Sussman (1985)**（SICP）用 Scheme 示範串列幾乎能解決任何問題。

---

## 6. 習題摘要

| 題號 | 內容 | 考點 |
|---|---|---|
| 7.1 | 設計**隱藏表示方式**、而且**不用 NULL 表示空串列**的串列 ADT | 例如用不透明的串列頭，存首尾指標和長度。和本章的設計比較取捨 |
| 7.2 | 不用指標的指標，重寫 `List_list`、`List_append`、`List_copy` | 體會特判的麻煩 |
| 7.3 | 用指標的指標重寫 `List_reverse` | 反過來看是否有幫助 |
| 7.4 | 用**環狀串列**讓 `List_append` 變成 O(1) | 用指向最後一個節點的指標代表串列，首尾都能 O(1) 到達；試試公開和隱藏兩種介面 |

---

## 7. 本章重點整理

1. **`List` 刻意公開表示方式** `struct T { T rest; void *first; }`，因為隱藏的代價大於好處。
2. **NULL 就是空串列**，所有函式都接受 NULL。
3. 建立：`List_list(a, b, ..., NULL)`，注意可變參數要轉型；或用 `List_push` 從前端加入。
4. **閉包**：`List_map(list, apply, cl)`，`apply` 拿到的是元素的指標，可以修改元素。
5. **`List_toArray`** 加上 NULL 哨兵，方便搭配 `qsort`；client 負責釋放陣列。
6. **實作技巧**：指標的指標消除首節點特判；`List_reverse` 原地反轉；`List_pop` 釋放前先存 `rest`。

> **一句話**：串列簡單到不值得隱藏，所以 `List` 直接公開結構，再用閉包、指標的指標和陣列轉換，把最常用的操作包裝成一致又好用的介面。
