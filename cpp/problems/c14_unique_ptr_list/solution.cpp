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
    ~List() { clear(); }
    void push(ll x) {
        auto nd = make_unique<Node>();
        nd->val = x;
        nd->next = std::move(head);
        head = std::move(nd);
        n++;
    }
    bool pop(ll& out) {
        if (!head) return false;
        out = head->val;
        head = std::move(head->next);
        n--;
        return true;
    }
    bool front(ll& out) const {
        if (!head) return false;
        out = head->val;
        return true;
    }
    void reverse() {
        unique_ptr<Node> prev;
        while (head) {
            unique_ptr<Node> nx = std::move(head->next);
            head->next = std::move(prev);
            prev = std::move(head);
            head = std::move(nx);
        }
        head = std::move(prev);
    }
    size_t size() const { return n; }
    ll sum() const {
        ll s = 0;
        for (Node* p = head.get(); p; p = p->next.get()) s += p->val;
        return s;
    }
    void print(ll k) const {
        if (!head) { cout << "empty\n"; return; }
        ll i = 0;
        for (Node* p = head.get(); p && i < k; p = p->next.get(), i++) cout << (i ? " " : "") << p->val;
        cout << '\n';
    }
    void clear() {
        while (head) head = std::move(head->next);   // 一次銷毀一個，不會遞迴
        n = 0;
    }
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
