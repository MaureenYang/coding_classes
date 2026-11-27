#include <stdio.h>

typedef long long ll;
typedef __int128 i128;      /* M·y 可能超過 10^18 × 10^18：要用 128 位元 */

/* 回傳 a 模 m 的反元素（保證 gcd(a, m) = 1） */
static ll inv_mod(ll a, ll m) {
    /* TODO：擴展歐幾里得 */
    return 0;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        int k;
        scanf("%d", &k);
        ll x = 0, M = 1;                   /* 目前的解：x mod M */
        for (int i = 0; i < k; i++) {
            ll a, m;
            scanf("%lld %lld", &a, &m);
            /* TODO：把 x ≡ a (mod m) 併進來：
               新的解是 x + M·y，其中 y ≡ (a − x)·M⁻¹ (mod m)；然後 M *= m */
        }
        printf("%lld\n", x);
    }
    return 0;
}
