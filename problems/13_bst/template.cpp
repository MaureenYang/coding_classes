#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct Node {
    int key;
    Node *left = nullptr, *right = nullptr;
    Node(int k) : key(k) {}
};

// 提示：參數用 Node*&，就能直接修改「父親指向自己的那個指標」
void insert(Node*& t, int x) {
    // TODO
}

bool find(Node* t, int x) {
    // TODO
    return false;
}

bool erase(Node*& t, int x) {
    // TODO: 照題目的三種情況處理
    return false;
}

void inorder(Node* t, vector<int>& out) { /* TODO */ }
void preorder(Node* t, vector<int>& out) { /* TODO */ }
int height(Node* t) { /* TODO */ return 0; }

void print(const vector<int>& v) {
    if (v.empty()) { cout << "empty\n"; return; }
    for (size_t i = 0; i < v.size(); i++) cout << v[i] << (i + 1 < v.size() ? ' ' : '\n');
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    Node* root = nullptr;
    while (Q--) {
        string op;
        cin >> op;
        int x;
        if (op == "insert") { cin >> x; insert(root, x); }
        else if (op == "find") { cin >> x; cout << (find(root, x) ? "yes" : "no") << '\n'; }
        else if (op == "delete") { cin >> x; if (!erase(root, x)) cout << "not found\n"; }
        else if (op == "inorder") { vector<int> v; inorder(root, v); print(v); }
        else if (op == "preorder") { vector<int> v; preorder(root, v); print(v); }
        else if (op == "height") cout << height(root) << '\n';
    }
    return 0;
}
