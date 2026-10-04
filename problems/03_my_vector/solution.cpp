#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

class MyVector {
    int* data_ = nullptr;
    int size_ = 0;
    int cap_ = 0;

public:
    ~MyVector() { delete[] data_; }
    void push_back(int x) {
        if (size_ == cap_) {
            int ncap = max(1, cap_ * 2);
            int* nd = new int[ncap];
            for (int i = 0; i < size_; i++) nd[i] = data_[i];
            delete[] data_;
            data_ = nd;
            cap_ = ncap;
        }
        data_[size_++] = x;
    }
    bool pop_back() {
        if (size_ == 0) return false;
        size_--;
        return true;
    }
    bool in_range(int i) const { return 0 <= i && i < size_; }
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
            if (v.in_range(i)) cout << v.at(i) << '\n';
            else cout << "error\n";
        } else if (op == "set") {
            int i, x; cin >> i >> x;
            if (v.in_range(i)) v.at(i) = x;
            else cout << "error\n";
        } else if (op == "size") {
            cout << v.size() << '\n';
        } else if (op == "capacity") {
            cout << v.capacity() << '\n';
        }
    }
    return 0;
}
