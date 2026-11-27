#include <stdio.h>

typedef long long ll;
typedef __int128 i128;

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

static ll inv_mod(ll a, ll m) {           /* gcd(a, m) = 1 */
    ll u, v;
    ext_gcd(((a % m) + m) % m, m, &u, &v);
    return ((u % m) + m) % m;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        int k;
        scanf("%d", &k);
        ll x = 0, M = 1;                   /* 目前：x mod M */
        for (int i = 0; i < k; i++) {
            ll a, m;
            scanf("%lld %lld", &a, &m);
            /* 找 y 使 x + M·y ≡ a (mod m)：y ≡ (a − x)·M⁻¹ (mod m) */
            ll diff = (ll)((((i128)a - x) % m + m) % m);
            ll y = (ll)((i128)diff * inv_mod(M % m, m) % m);
            x = (ll)(x + (i128)M * y);
            M *= m;
        }
        printf("%lld\n", x);
    }
    return 0;
}
