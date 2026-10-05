#include <cstring>
#include <iostream>
#include <string>
#include <utility>
using namespace std;

// ===== 記憶體配置記錄（不要修改）=====
long long g_alloc = 0, g_free = 0;
char* alloc_chars(size_t n) { g_alloc++; return new char[n]; }
void free_chars(char* p) { if (p) { g_free++; delete[] p; } }
// =====================================

class MyString {
    char* data_ = nullptr;   // 不含結尾的 '\0' 也可以，看你怎麼設計
    size_t len_ = 0;

public:
    MyString() = default;
    MyString(const char* s) {
        // TODO
    }
    ~MyString() {
        // TODO
    }
    MyString(const MyString& other) {
        // TODO: 深複製
    }
    MyString& operator=(const MyString& other) {
        // TODO: 小心自我指定
        return *this;
    }
    MyString(MyString&& other) noexcept {
        // TODO: 偷走 other 的資料
    }
    MyString& operator=(MyString&& other) noexcept {
        // TODO: 小心自我移動
        return *this;
    }
    MyString& operator+=(const MyString& other) {
        // TODO: 小心 s += s
        return *this;
    }
    size_t size() const { return len_; }
    void print() const {
        if (len_ == 0) cout << "(empty)\n";
        else { cout.write(data_, len_); cout << '\n'; }
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int K, Q;
    cin >> K >> Q;
    {
        MyString s[10];
        while (Q--) {
            string op;
            int i, j;
            cin >> op >> i;
            if (op == "set") { string w; cin >> w; s[i] = MyString(w.c_str()); }
            else if (op == "copy") { cin >> j; s[i] = s[j]; }
            else if (op == "move") { cin >> j; s[i] = std::move(s[j]); }
            else if (op == "append") { cin >> j; s[i] += s[j]; }
            else if (op == "swap") { cin >> j; std::swap(s[i], s[j]); }
            else if (op == "print") s[i].print();
            else if (op == "len") cout << s[i].size() << '\n';
        }
    }  // 所有字串在這裡解構
    if (g_alloc == g_free) cout << "leak check: ok\n";
    else cout << "leak check: LEAK (alloc " << g_alloc << ", free " << g_free << ")\n";
    return 0;
}
