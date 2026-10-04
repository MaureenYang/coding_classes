#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

struct Node {
    int key;
    Node *left = nullptr, *right = nullptr;
    Node(int k) : key(k) {}
};

void insert(Node*& t, int x) {
    if (!t) { t = new Node(x); return; }
    if (x < t->key) insert(t->left, x);
    else if (x > t->key) insert(t->right, x);
}

bool find(Node* t, int x) {
    while (t) {
        if (x == t->key) return true;
        t = x < t->key ? t->left : t->right;
    }
    return false;
}

bool erase(Node*& t, int x) {
    if (!t) return false;
    if (x < t->key) return erase(t->left, x);
    if (x > t->key) return erase(t->right, x);
    if (t->left && t->right) {
        Node* s = t->right;
        while (s->left) s = s->left;
        t->key = s->key;
        return erase(t->right, s->key);
    }
    Node* child = t->left ? t->left : t->right;
    delete t;
    t = child;
    return true;
}

void inorder(Node* t, vector<int>& out) {
    if (!t) return;
    inorder(t->left, out);
    out.push_back(t->key);
    inorder(t->right, out);
}
void preorder(Node* t, vector<int>& out) {
    if (!t) return;
    out.push_back(t->key);
    preorder(t->left, out);
    preorder(t->right, out);
}
int height(Node* t) { return t ? 1 + max(height(t->left), height(t->right)) : 0; }

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
