#include <stdio.h>

typedef long long ll;
typedef __int128 i128;

static i128 floor_div(i128 a, i128 b) {           /* b > 0 */
    i128 q = a / b;
    if (a % b != 0 && a < 0) q--;
    return q;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        ll a[2], b[2];
        scanf("%lld %lld %lld %lld", &a[0], &a[1], &b[0], &b[1]);
        for (;;) {
            i128 na = (i128)a[0] * a[0] + (i128)a[1] * a[1];
            i128 nb = (i128)b[0] * b[0] + (i128)b[1] * b[1];
            if (nb < na) {                         /* 讓 a 是比較短的那個 */
                ll t0 = a[0], t1 = a[1];
                a[0] = b[0]; a[1] = b[1]; b[0] = t0; b[1] = t1;
                i128 tn = na; na = nb; nb = tn;
            }
            i128 dot = (i128)a[0] * b[0] + (i128)a[1] * b[1];
            ll m = (ll)floor_div(2 * dot + na, 2 * na);   /* round(dot / na)，0.5 往上進位 */
            if (m == 0) break;
            b[0] -= m * a[0];
            b[1] -= m * a[1];
        }
        printf("%lld %lld %lld %lld\n", a[0], a[1], b[0], b[1]);
    }
    return 0;
}
