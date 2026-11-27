#include <stdio.h>
#include <string.h>

typedef long long ll;
typedef __int128 i128;

/* 回傳 g = gcd(a, b)，並求出 u、v 使 a·u + b·v = g */
static ll ext_gcd(ll a, ll b, ll *u, ll *v) {
    ll u0 = 1, v0 = 0, u1 = 0, v1 = 1;
    while (b) {
        ll q = a / b, t;
        t = a - q * b; a = b; b = t;
        t = u0 - q * u1; u0 = u1; u1 = t;
        t = v0 - q * v1; v0 = v1; v1 = t;
    }
    *u = u0; *v = v0;
    return a;
}

/* 解 a·x ≡ b (mod m)：無解回傳 0；有解回傳 g = gcd(a, m)（解的個數），*x0 是最小的非負解 */
static ll solve_linear(ll a, ll b, ll m, ll *x0) {
    ll u, v;
    ll g = ext_gcd(a, m, &u, &v);
    if (b % g) return 0;
    ll mm = m / g;
    ll uu = ((u % mm) + mm) % mm;
    *x0 = (ll)((i128)(b / g) * uu % mm);
    return g;
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
