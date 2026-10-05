#include <algorithm>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

template <class T>
class Stack {
    vector<T> data_;
public:
    void push(const T& x) { data_.push_back(x); }
    void pop() { data_.pop_back(); }
    const T& top() const { return data_.back(); }
    size_t size() const { return data_.size(); }
    bool empty() const { return data_.empty(); }
    const vector<T>& items() const { return data_; }
};

template <class T> void print(const T& x) { cout << x; }
template <class A, class B> void print(const pair<A, B>& p) { cout << '(' << p.first << ',' << p.second << ')'; }

template <class T> void read(T& x) { cin >> x; }
template <class A, class B> void read(pair<A, B>& p) { cin >> p.first >> p.second; }

template <class T>
T maxOf(const vector<T>& v) {
    T best = v[0];
    for (const T& x : v) if (best < x) best = x;
    return best;
}

template <class T>
void handle(Stack<T>& s, const string& op) {
    if (op == "push") { T x; read(x); s.push(x); return; }
    if (op == "size") { cout << s.size() << '\n'; return; }
    if (s.empty()) { cout << "empty\n"; return; }
    if (op == "pop") { print(s.top()); cout << '\n'; s.pop(); }
    else if (op == "top") { print(s.top()); cout << '\n'; }
    else if (op == "max") { print(maxOf(s.items())); cout << '\n'; }
    else if (op == "sorted") {
        vector<T> v = s.items();
        sort(v.begin(), v.end());
        for (size_t i = 0; i < v.size(); i++) { print(v[i]); cout << (i + 1 < v.size() ? ' ' : '\n'); }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    Stack<int> si;
    Stack<string> ss;
    Stack<pair<int, string>> sp;
    int Q;
    cin >> Q;
    while (Q--) {
        string type, op;
        cin >> type >> op;
        if (type == "int") handle(si, op);
        else if (type == "str") handle(ss, op);
        else handle(sp, op);
    }
    return 0;
}
