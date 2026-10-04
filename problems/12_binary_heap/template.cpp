#include <iostream>
#include <string>
#include <vector>
using namespace std;
typedef long long ll;

class MinHeap {
    vector<ll> a;

    void sift_up(int i) {
        // TODO
    }
    void sift_down(int i) {
        // TODO
    }

public:
    bool empty() const { return a.empty(); }
    int size() const { return a.size(); }
    ll top() const { return a[0]; }
    void push(ll x) {
        a.push_back(x);
        sift_up(a.size() - 1);
    }
    void pop() {
        // TODO
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    MinHeap h;
    while (Q--) {
        string op;
        cin >> op;
        if (op == "push") { ll x; cin >> x; h.push(x); }
        else if (op == "size") cout << h.size() << '\n';
        else if (h.empty()) cout << "empty\n";
        else if (op == "top") cout << h.top() << '\n';
        else if (op == "pop") { cout << h.top() << '\n'; h.pop(); }
    }
    return 0;
}
