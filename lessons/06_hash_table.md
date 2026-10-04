# 06. 雜湊表 (Hash Table)

> 練習題：`10_hash_table`、`11_lru_cache`

## 1. 想法

如果 key 是 `0 ~ 999` 的整數，開一個大小 1000 的陣列，`a[key]` 就是 `O(1)` 查詢。
但 key 可能是 `10^18` 或字串 —— 開不了那麼大的陣列。

**雜湊函數** `h(key)` 把任意的 key 對應到 `0 ~ M-1` 的「桶子」編號：

```
key = 1234567  → h(key) = 1234567 % 8 = 7  → 放到 bucket[7]
```

## 2. 碰撞 (Collision) 與 Separate Chaining

不同的 key 可能算出同一個桶子。最簡單的處理：每個桶子是一條串列。

```
bucket[0]: → (16, "a") → (8, "b")
bucket[1]: → (9, "c")
bucket[2]:
bucket[3]: → (3, "d") → (11, "e") → (19, "f")
...
```

```cpp
vector<vector<pair<ll,ll>>> buckets(M);

void put(ll k, ll v) {
    auto& b = buckets[index(k)];
    for (auto& e : b) if (e.first == k) { e.second = v; return; }  // 已存在：更新
    b.push_back({k, v});                                            // 不存在：新增
}
```

- **負載因子** `α = n / M`（平均每個桶子幾個元素）。保持 `α` 在常數範圍內，操作就是平均 `O(1)`。
- 元素太多時要 **rehash**：把 `M` 加倍、所有元素重新放一次（攤銷 `O(1)`，和 vector 一樣的道理）。

另一種方法是 **開放定址 (open addressing)**：碰撞時往下一格找（linear probing）。
比較快（記憶體連續），但刪除比較麻煩（要放「墓碑」標記）。

## 3. 好的雜湊函數

雜湊表的效能完全取決於 key 有沒有 **平均分散** 到各個桶子。

### 陷阱 1：負數取餘數

```cpp
ll k = -7;
k % 8;            // == -7，拿去當索引 → 越界！
(ull)k % 8;       // 先轉成無號數 → 0 ~ 7，安全
```

### 陷阱 2：key 有規律

如果 `M = 1024` 而 key 全都是 1024 的倍數，`k % 1024` 全部是 0 → 所有元素擠在同一桶 → **退化成 `O(n)`**。
真實世界的資料常常有規律（ID 是 1000 的倍數、位址是 8 的倍數……），
而且有心人可以 **故意** 構造這種資料攻擊你的程式（Hash DoS）。

解法：先把 key 的位元「打亂」再取桶子。常用的 splitmix64：

```cpp
static ull mix(ull x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
size_t index(ll key) { return mix((ull)key) & (M - 1); }  // M 是 2 的次方時，& (M-1) 等於 % M
```

競賽中為了防止別人針對固定的雜湊函數出測資，還會再 xor 一個 **隨機數**（程式啟動時決定）。

## 4. STL：unordered_map / unordered_set

```cpp
unordered_map<string, int> cnt;
cnt["apple"]++;                 // 不存在會自動建立（值為 0）
if (cnt.count("pear")) ...      // 查詢是否存在，不會建立
auto it = cnt.find("apple");
if (it != cnt.end()) cout << it->second;
cnt.erase("apple");
cnt.reserve(1 << 20);           // 預先配置桶子，避免多次 rehash
```

> ⚠️ `cnt[key]` 在 key 不存在時 **會插入一筆**。只想查詢時用 `find` 或 `count`。

### unordered_map vs map

| | `unordered_map` | `map` |
|---|---|---|
| 底層 | 雜湊表 | 紅黑樹 |
| 操作 | 平均 `O(1)`，最差 `O(n)` | 一律 `O(log n)` |
| 有序？ | 否 | 是（可以 `lower_bound`、依序走訪） |

## 5. Corner case checklist

- 負數 key、`±10^18` 的極端值。
- `put` 已存在的 key：只更新值，`size` 不變。
- 刪除不存在的 key。
- 有規律的 key（2 的次方的倍數、某質數的倍數）—— 會不會全擠在同一桶？
- 刪除後再插入同一個 key。
