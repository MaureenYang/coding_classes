#include <cstring>
#include <iostream>
#include <string>
#include <utility>
using namespace std;

long long g_alloc = 0, g_free = 0;
char* alloc_chars(size_t n) { g_alloc++; return new char[n]; }
void free_chars(char* p) { if (p) { g_free++; delete[] p; } }

class MyString {
    char* data_ = nullptr;   // 只存 len_ 個字元，不存 '\0'
    size_t len_ = 0;

public:
    MyString() = default;
    MyString(const char* s) : len_(strlen(s)) {
        if (len_) { data_ = alloc_chars(len_); memcpy(data_, s, len_); }
    }
    ~MyString() { free_chars(data_); }

    MyString(const MyString& other) : len_(other.len_) {
        if (len_) { data_ = alloc_chars(len_); memcpy(data_, other.data_, len_); }
    }
    // copy-and-swap：參數是「傳值」的複製品，自我指定也安全
    MyString& operator=(const MyString& other) {
        if (this != &other) {
            MyString tmp(other);
            swap(data_, tmp.data_);
            swap(len_, tmp.len_);
        }
        return *this;
    }
    MyString(MyString&& other) noexcept : data_(other.data_), len_(other.len_) {
        other.data_ = nullptr;
        other.len_ = 0;
    }
    MyString& operator=(MyString&& other) noexcept {
        if (this != &other) {
            free_chars(data_);
            data_ = other.data_;
            len_ = other.len_;
            other.data_ = nullptr;
            other.len_ = 0;
        }
        return *this;
    }
    MyString& operator+=(const MyString& other) {
        if (other.len_ == 0) return *this;
        size_t n = len_ + other.len_;
        char* nd = alloc_chars(n);
        if (len_) memcpy(nd, data_, len_);
        memcpy(nd + len_, other.data_, other.len_);   // other 可能就是 *this，所以先複製再釋放
        free_chars(data_);
        data_ = nd;
        len_ = n;
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
    }
    if (g_alloc == g_free) cout << "leak check: ok\n";
    else cout << "leak check: LEAK (alloc " << g_alloc << ", free " << g_free << ")\n";
    return 0;
}
