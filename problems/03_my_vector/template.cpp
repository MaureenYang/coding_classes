#include <iostream>
#include <string>
using namespace std;

class MyVector {
    int* data_ = nullptr;
    int size_ = 0;
    int cap_ = 0;

public:
    ~MyVector() { delete[] data_; }

    void push_back(int x) {
        // TODO: 容量不夠時，配置新陣列 (max(1, cap*2))、搬資料、釋放舊陣列
    }
    bool pop_back() {
        // TODO: 成功回傳 true，空的回傳 false
        return false;
    }
    bool in_range(int i) const {
        // TODO
        return false;
    }
    int& at(int i) { return data_[i]; }
    int size() const { return size_; }
    int capacity() const { return cap_; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    MyVector v;
    while (Q--) {
        string op;
        cin >> op;
        if (op == "push") {
            int x; cin >> x;
            v.push_back(x);
        } else if (op == "pop") {
            if (!v.pop_back()) cout << "error\n";
        } else if (op == "get") {
            int i; cin >> i;
            // TODO
        } else if (op == "set") {
            int i, x; cin >> i >> x;
            // TODO
        } else if (op == "size") {
            cout << v.size() << '\n';
        } else if (op == "capacity") {
            cout << v.capacity() << '\n';
        }
    }
    return 0;
}
