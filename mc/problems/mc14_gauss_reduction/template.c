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
        /* TODO：Gauss 格基約化
           loop:
             若 ‖b‖² < ‖a‖²，交換 a、b
             m = round(a·b / ‖a‖²)（用 floor_div(2·dot + ‖a‖², 2·‖a‖²) 算）
             m == 0 就結束；否則 b ← b − m·a */
        printf("%lld %lld %lld %lld\n", a[0], a[1], b[0], b[1]);
    }
    return 0;
}
