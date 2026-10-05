#include <iostream>
#include <memory>
#include <string>
using namespace std;
typedef long long ll;

struct Node {
    ll val;
    unique_ptr<Node> next;
};

class List {
    unique_ptr<Node> head;
    size_t n = 0;
public:
    ~List() {
        // TODO: 用迴圈拆掉所有節點，避免遞迴解構
    }
    void push(ll x) { /* TODO */ }
    bool pop(ll& out) { /* TODO */ return false; }
    bool front(ll& out) const { /* TODO */ return false; }
    void reverse() { /* TODO */ }
    size_t size() const { return n; }
    ll sum() const { /* TODO */ return 0; }
    void print(ll k) const { /* TODO */ }
    void clear() { /* TODO */ }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    List L;
    int Q;
    cin >> Q;
    while (Q--) {
        string op;
        cin >> op;
        ll x;
        if (op == "push") { cin >> x; L.push(x); }
        else if (op == "pushmany") { cin >> x; for (ll i = 1; i <= x; i++) L.push(i); }
        else if (op == "pop") { if (L.pop(x)) cout << x << '\n'; else cout << "empty\n"; }
        else if (op == "front") { if (L.front(x)) cout << x << '\n'; else cout << "empty\n"; }
        else if (op == "reverse") L.reverse();
        else if (op == "size") cout << L.size() << '\n';
        else if (op == "sum") cout << L.sum() << '\n';
        else if (op == "print") { cin >> x; L.print(x); }
        else if (op == "clear") L.clear();
    }
    return 0;
}
