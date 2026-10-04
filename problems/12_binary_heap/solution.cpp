#include <iostream>
#include <string>
#include <vector>
using namespace std;
typedef long long ll;

class MinHeap {
    vector<ll> a;

    void sift_up(int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (a[p] <= a[i]) break;
            swap(a[p], a[i]);
            i = p;
        }
    }
    void sift_down(int i) {
        int n = a.size();
        while (true) {
            int l = 2 * i + 1, r = 2 * i + 2, m = i;
            if (l < n && a[l] < a[m]) m = l;
            if (r < n && a[r] < a[m]) m = r;
            if (m == i) break;
            swap(a[m], a[i]);
            i = m;
        }
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
        a[0] = a.back();
        a.pop_back();
        if (!a.empty()) sift_down(0);
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
