#include <iostream>
#include <stack>
#include <string>
using namespace std;

class MinStack {
    // TODO: 想想看要存什麼
public:
    void push(int x) {}
    bool empty() const { return true; }
    void pop() {}
    int top() const { return 0; }
    int getmin() const { return 0; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    MinStack s;
    while (Q--) {
        string op;
        cin >> op;
        if (op == "push") { int x; cin >> x; s.push(x); }
        else if (s.empty()) cout << "empty\n";
        else if (op == "pop") s.pop();
        else if (op == "top") cout << s.top() << '\n';
        else if (op == "getmin") cout << s.getmin() << '\n';
    }
    return 0;
}
