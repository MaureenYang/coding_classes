#include <stdio.h>
#include <string.h>

static const double FREQ[26] = {
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
    6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074};

static char line[8192];

/* 用替換表 key（key[i] 是字母 'A'+i 的密文）加密 */
static void encrypt(const char *key, char *s) {
    for (; *s; s++)
        if (*s >= 'A' && *s <= 'Z') *s = key[*s - 'A'];
}

static void decrypt(const char *key, char *s) {
    char inv[26];
    for (int i = 0; i < 26; i++) inv[key[i] - 'A'] = (char)('A' + i);
    encrypt(inv, s);
}

/* 把 s 往回位移 k 之後，和英文頻率的卡方值 */
static double chi_after_shift(const char *s, int k) {
    long cnt[26] = {0}, n = 0;
    for (; *s; s++)
        if (*s >= 'A' && *s <= 'Z') { cnt[((*s - 'A') - k + 26) % 26]++; n++; }
    double chi = 0;
    for (int i = 0; i < 26; i++) {
        double e = n * FREQ[i] / 100.0;
        chi += (cnt[i] - e) * (cnt[i] - e) / e;
    }
    return chi;
}

int main(void) {
    int q;
    if (!fgets(line, sizeof line, stdin) || sscanf(line, "%d", &q) != 1) return 0;
    while (q--) {
        if (!fgets(line, sizeof line, stdin)) break;
        line[strcspn(line, "\r\n")] = '\0';
        if (strncmp(line, "BREAK ", 6) == 0) {
            char *s = line + 6;
            int best = 0;
            double bs = chi_after_shift(s, 0);
            for (int k = 1; k < 26; k++) {
                double c = chi_after_shift(s, k);
                if (c < bs) { bs = c; best = k; }
            }
            for (char *p = s; *p; p++)
                if (*p >= 'A' && *p <= 'Z') *p = (char)('A' + (*p - 'A' - best + 26) % 26);
            printf("%d %s\n", best, s);
        } else {
            char key[27];
            memcpy(key, line + 4, 26);
            key[26] = '\0';
            char *s = line + 31;          /* "ENC " + 26 個字母 + 空白 */
            if (line[0] == 'E') encrypt(key, s); else decrypt(key, s);
            printf("%s\n", s);
        }
    }
    return 0;
}
