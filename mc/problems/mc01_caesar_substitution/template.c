#include <stdio.h>
#include <string.h>

/* 英文字母 A～Z 的出現頻率（百分比） */
static const double FREQ[26] = {
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
    6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074};

static char line[8192];

/* 用替換表 key 加密：字母 'A'+i 換成 key[i]；非字母不變 */
static void encrypt(const char *key, char *s) {
    /* TODO */
}

/* 解密：先算出反向的替換表 */
static void decrypt(const char *key, char *s) {
    /* TODO */
}

/* 把 s 中每個字母往回位移 k 之後，和英文頻率比較的卡方值 */
static double chi_after_shift(const char *s, int k) {
    /* TODO：數 26 個字母的次數 cnt[i]、總字母數 n，
       回傳 Σ (cnt[i] − n·FREQ[i]/100)² / (n·FREQ[i]/100) */
    return 0;
}

int main(void) {
    int q;
    if (!fgets(line, sizeof line, stdin) || sscanf(line, "%d", &q) != 1) return 0;
    while (q--) {
        if (!fgets(line, sizeof line, stdin)) break;
        line[strcspn(line, "\r\n")] = '\0';
        if (strncmp(line, "BREAK ", 6) == 0) {
            char *s = line + 6;
            /* TODO：試 k = 0..25，找卡方值最小的位移，輸出 "k 明文" */
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
