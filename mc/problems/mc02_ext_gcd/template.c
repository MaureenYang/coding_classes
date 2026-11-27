#include <stdio.h>
#include <string.h>

typedef long long ll;
typedef __int128 i128;      /* 兩個 10^18 相乘會超過 long long，先轉成 128 位元再取模 */

/* 回傳 g = gcd(a, b)，並求出 u、v 使 a·u + b·v = g */
static ll ext_gcd(ll a, ll b, ll *u, ll *v) {
    /* TODO：擴展歐幾里得（迴圈版） */
    *u = 1; *v = 0;
    return a;
}

/* 解 a·x ≡ b (mod m)：無解回傳 0；有解回傳 g = gcd(a, m)（解的個數），*x0 是最小的非負解 */
static ll solve_linear(ll a, ll b, ll m, ll *x0) {
    /* TODO */
    return 0;
}

int main(void) {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "GCD") == 0) {
            ll a, b, u, v;
            scanf("%lld %lld", &a, &b);
            printf("%lld\n", ext_gcd(a, b, &u, &v));
        } else if (strcmp(op, "INV") == 0) {
            ll a, m, x;
            scanf("%lld %lld", &a, &m);
            if (solve_linear(a, 1 % m, m, &x) == 1) printf("%lld\n", x);
            else puts("none");
        } else {
            ll a, b, m, x;
            scanf("%lld %lld %lld", &a, &b, &m);
            ll g = solve_linear(a, b, m, &x);
            if (g) printf("%lld %lld\n", g, x);
            else puts("none");
        }
    }
    return 0;
}
