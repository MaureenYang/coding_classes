#include <iostream>
#include <string>
using namespace std;

struct Node {
    int val;
    Node* next;
    Node(int v) : val(v), next(nullptr) {}
};

class LinkedList {
    Node* head = nullptr;
    Node* tail = nullptr;
    int n = 0;

public:
    ~LinkedList() {
        while (head) { Node* t = head; head = head->next; delete t; }
    }
    int size() const { return n; }

    void push_front(int x) { /* TODO */ }
    void push_back(int x) { /* TODO */ }
    bool pop_front() { /* TODO */ return false; }
    bool pop_back() { /* TODO: 單向串列要找到「倒數第二個」 */ return false; }
    bool insert(int i, int x) { /* TODO */ return false; }
    bool erase(int i) { /* TODO */ return false; }
    void reverse() { /* TODO: prev / cur / next 三個指標 */ }
    void print() const {
        if (!head) { cout << "empty\n"; return; }
        for (Node* p = head; p; p = p->next) cout << p->val << (p->next ? ' ' : '\n');
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    LinkedList L;
    while (Q--) {
        string op;
        cin >> op;
        int i, x;
        if (op == "push_front") { cin >> x; L.push_front(x); }
        else if (op == "push_back") { cin >> x; L.push_back(x); }
        else if (op == "pop_front") { if (!L.pop_front()) cout << "error\n"; }
        else if (op == "pop_back") { if (!L.pop_back()) cout << "error\n"; }
        else if (op == "insert") { cin >> i >> x; if (!L.insert(i, x)) cout << "error\n"; }
        else if (op == "erase") { cin >> i; if (!L.erase(i)) cout << "error\n"; }
        else if (op == "reverse") L.reverse();
        else if (op == "print") L.print();
        else if (op == "size") cout << L.size() << '\n';
    }
    return 0;
}
