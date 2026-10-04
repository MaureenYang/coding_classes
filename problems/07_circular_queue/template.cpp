#include <iostream>
#include <string>
using namespace std;

class CircularQueue {
    int* buf;
    int cap;
    int head = 0;   // 第一個元素的位置
    int count = 0;  // 目前元素個數
public:
    CircularQueue(int k) : buf(new int[k]), cap(k) {}
    ~CircularQueue() { delete[] buf; }

    bool enqueue(int x) { /* TODO */ return false; }
    bool dequeue() { /* TODO */ return false; }
    int front() const { /* TODO */ return 0; }
    int rear() const { /* TODO */ return 0; }
    int size() const { return count; }
    bool empty() const { return count == 0; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int K, Q;
    cin >> K >> Q;
    CircularQueue q(K);
    while (Q--) {
        string op;
        cin >> op;
        if (op == "enqueue") {
            int x; cin >> x;
            cout << (q.enqueue(x) ? "ok" : "full") << '\n';
        } else if (op == "size") {
            cout << q.size() << '\n';
        } else if (q.empty()) {
            cout << "empty\n";
        } else if (op == "dequeue") {
            cout << q.front() << '\n';
            q.dequeue();
        } else if (op == "front") {
            cout << q.front() << '\n';
        } else if (op == "rear") {
            cout << q.rear() << '\n';
        }
    }
    return 0;
}
