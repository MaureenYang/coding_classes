#include <stdio.h>

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

/* a 是不是 n 的 Miller–Rabin 證人（證明 n 是合數）；n − 1 = 2^s · d */
/* a 是不是 n 的 Miller–Rabin 證人（證明 n 是合數）；n − 1 = 2^s · d */
static int is_witness(u64 a, u64 n, u64 d, int s) {
    /* TODO：x = a^d；x 是 1 或 n − 1 → 不是證人；
             再平方 s − 1 次，途中出現 n − 1 → 不是證人；都沒有 → 是證人 */
    return 0;
}

static int is_prime(u64 n) {
    static const u64 bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    /* TODO：先處理 n < 2 和小質數的倍數；把 n − 1 寫成 2^s · d；
             12 個底數都不是證人才是質數 */
    return 0;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        u64 n;
        scanf("%llu", &n);
        puts(is_prime(n) ? "prime" : "composite");
    }
    return 0;
}
