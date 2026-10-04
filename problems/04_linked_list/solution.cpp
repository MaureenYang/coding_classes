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

    void push_front(int x) {
        Node* nd = new Node(x);
        nd->next = head;
        head = nd;
        if (!tail) tail = nd;
        n++;
    }
    void push_back(int x) {
        Node* nd = new Node(x);
        if (!tail) head = tail = nd;
        else { tail->next = nd; tail = nd; }
        n++;
    }
    bool pop_front() {
        if (!head) return false;
        Node* t = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete t;
        n--;
        return true;
    }
    bool pop_back() {
        if (n == 0) return false;
        return erase(n - 1);
    }
    bool insert(int i, int x) {
        if (i < 0 || i > n) return false;
        if (i == 0) { push_front(x); return true; }
        if (i == n) { push_back(x); return true; }
        Node* prev = head;
        for (int k = 0; k < i - 1; k++) prev = prev->next;
        Node* nd = new Node(x);
        nd->next = prev->next;
        prev->next = nd;
        n++;
        return true;
    }
    bool erase(int i) {
        if (i < 0 || i >= n) return false;
        if (i == 0) return pop_front();
        Node* prev = head;
        for (int k = 0; k < i - 1; k++) prev = prev->next;
        Node* t = prev->next;
        prev->next = t->next;
        if (t == tail) tail = prev;
        delete t;
        n--;
        return true;
    }
    void reverse() {
        Node *prev = nullptr, *cur = head;
        tail = head;
        while (cur) {
            Node* nx = cur->next;
            cur->next = prev;
            prev = cur;
            cur = nx;
        }
        head = prev;
    }
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
