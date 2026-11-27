#include <stdio.h>
#include <string.h>

static const double FREQ[26] = {
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
    6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074};

static char ct[8192];
static int n;

/* 第 col 行（下標 ≡ col mod L 的字母）的重合指數 */
static double ioc(int col, int L) {
    long cnt[26] = {0}, m = 0;
    for (int i = col; i < n; i += L) { cnt[ct[i] - 'A']++; m++; }
    double s = 0;
    for (int i = 0; i < 26; i++) s += (double)cnt[i] * (cnt[i] - 1);
    return s / ((double)m * (m - 1));
}

/* 第 col 行往回位移 s 之後的卡方值 */
static double chi(int col, int L, int s) {
    long cnt[26] = {0}, m = 0;
    for (int i = col; i < n; i += L) { cnt[(ct[i] - 'A' - s + 26) % 26]++; m++; }
    double r = 0;
    for (int i = 0; i < 26; i++) {
        double e = m * FREQ[i] / 100.0;
        r += (cnt[i] - e) * (cnt[i] - e) / e;
    }
    return r;
}

int main(void) {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        scanf("%8191s", ct);
        n = (int)strlen(ct);
        int L = 1;
        for (; L < 15; L++) {
            double avg = 0;
            for (int c = 0; c < L; c++) avg += ioc(c, L);
            if (avg / L >= 0.060) break;
        }
        char key[16];
        for (int c = 0; c < L; c++) {
            int best = 0;
            double bs = chi(c, L, 0);
            for (int s = 1; s < 26; s++) {
                double v = chi(c, L, s);
                if (v < bs) { bs = v; best = s; }
            }
            key[c] = (char)('A' + best);
        }
        key[L] = '\0';
        for (int i = 0; i < n; i++) ct[i] = (char)('A' + (ct[i] - key[i % L] + 26) % 26);
        printf("%s\n%s\n", key, ct);
    }
    return 0;
}
