#include <iostream>
#include <stack>
#include <string>
#include <algorithm>
using namespace std;

class MinStack {
    stack<int> st, mn;  // mn.top() = 目前所有元素的最小值
public:
    void push(int x) {
        st.push(x);
        mn.push(mn.empty() ? x : min(x, mn.top()));
    }
    bool empty() const { return st.empty(); }
    void pop() { st.pop(); mn.pop(); }
    int top() const { return st.top(); }
    int getmin() const { return mn.top(); }
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
