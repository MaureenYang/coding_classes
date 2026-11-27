#include <stdio.h>
#include <stdlib.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }

static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;
    a %= m;
    for (; e; e >>= 1, a = mulmod(a, a, m))
        if (e & 1) r = mulmod(r, a, m);
    return r;
}

static int is_prime(u64 n) {
    static const u64 B[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (n < 2) return 0;
    for (int i = 0; i < 12; i++)
        if (n % B[i] == 0) return n == B[i];
    u64 d = n - 1;
    int s = 0;
    while (d % 2 == 0) { d /= 2; s++; }
    for (int i = 0; i < 12; i++) {
        u64 x = powmod(B[i], d, n);
        if (x == 1 || x == n - 1) continue;
        int ok = 0;
        for (int r = 1; r < s && !ok; r++) {
            x = mulmod(x, x, n);
            if (x == n - 1) ok = 1;
        }
        if (!ok) return 0;
    }
    return 1;
}

static u64 gcd(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }

/* Pollard ρ：回傳 n 的一個非平凡因數（n 是奇合數）
   f(x) = x² + c，x 走一步、y 走兩步，看 gcd(|x − y|, n)；得到 n 就換一個 c */
static u64 rho(u64 n) {
    /* TODO */
    return n;
}

static u64 fac[128];
static int nf;

/* 把 n 的所有質因數（含重複）放進 fac[] */
static void factor(u64 n) {
    /* TODO：n = 1 → 結束；n 是質數 → 放進去；否則用 rho 拆成兩半，遞迴 */
}

static int cmp(const void *a, const void *b) {
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    return x < y ? -1 : x > y;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 n;
        scanf("%llu", &n);
        nf = 0;
        for (u64 p = 2; p < 100; p++)          /* 先除掉小質因數 */
            while (n % p == 0) { fac[nf++] = p; n /= p; }
        factor(n);
        qsort(fac, nf, sizeof fac[0], cmp);
        /* TODO：輸出 "p" 或 "p^e"，由小到大，空白隔開 */
        putchar('\n');
    }
    return 0;
}
