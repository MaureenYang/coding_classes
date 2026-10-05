#include <algorithm>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

template <class T>
class Stack {
    vector<T> data_;
public:
    // TODO: push, pop, top, size, empty, 以及讓外部讀取全部元素的方法
};

// TODO: print 函式模板（以及 pair 的多載）

// TODO: 讀入一個 T（int / string / pair 的讀法不同）

// TODO: template <class T> void handle(Stack<T>& s, const string& op)

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    Stack<int> si;
    Stack<string> ss;
    Stack<pair<int, string>> sp;
    int Q;
    cin >> Q;
    while (Q--) {
        string type, op;
        cin >> type >> op;
        // TODO: 依 type 呼叫 handle(si, op) / handle(ss, op) / handle(sp, op)
    }
    return 0;
}
