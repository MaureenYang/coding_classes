#include <stdio.h>
#include <string.h>

static const double FREQ[26] = {
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
    6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074};

static char ct[8192];
static int n;

/* 第 col 行（下標 ≡ col mod L 的字母）的重合指數 */
static double ioc(int col, int L) {
    /* TODO：Σ cnt[i]·(cnt[i] − 1) / (m·(m − 1))，m 是這一行的字母數 */
    return 0;
}

/* 第 col 行往回位移 s 之後的卡方值 */
static double chi(int col, int L, int s) {
    /* TODO：同 MC01 */
    return 0;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        scanf("%8191s", ct);
        n = (int)strlen(ct);
        int L = 1;
        char key[16];
        /* TODO：1. 找最小的 L（1 ≤ L ≤ 15）使各行重合指數的平均 ≥ 0.060
                 2. 每一行找卡方值最小的位移 → 金鑰字母
                 3. 解密 ct */
        key[0] = 'A'; key[1] = '\0';
        printf("%s\n%s\n", key, ct);
    }
    return 0;
}
