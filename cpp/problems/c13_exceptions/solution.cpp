#include <climits>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
typedef long long ll;

class CalcError : public runtime_error {
public:
    using runtime_error::runtime_error;
};
class StackUnderflow : public CalcError {
public:
    StackUnderflow() : CalcError("stack underflow") {}
};
class DivisionByZero : public CalcError {
public:
    DivisionByZero() : CalcError("division by zero") {}
};
class Overflow : public CalcError {
public:
    Overflow() : CalcError("overflow") {}
};

class Calculator {
    vector<ll> st;
    void need(size_t k) const { if (st.size() < k) throw StackUnderflow(); }
public:
    void push(ll x) { st.push_back(x); }
    void binary(const string& op) {
        need(2);
        ll a = st[st.size() - 2], b = st.back();   // 先「看」，還不修改
        ll r;
        if (op == "add") { if (__builtin_add_overflow(a, b, &r)) throw Overflow(); }
        else if (op == "sub") { if (__builtin_sub_overflow(a, b, &r)) throw Overflow(); }
        else if (op == "mul") { if (__builtin_mul_overflow(a, b, &r)) throw Overflow(); }
        else if (op == "div") {
            if (b == 0) throw DivisionByZero();
            if (a == LLONG_MIN && b == -1) throw Overflow();
            r = a / b;
        } else {  // mod
            if (b == 0) throw DivisionByZero();
            r = (b == -1) ? 0 : a % b;               // LLONG_MIN % -1 會讓 CPU 當掉
        }
        st.pop_back();                               // 全部確認沒問題，才修改
        st.back() = r;
    }
    void dup() { need(1); st.push_back(st.back()); }
    void pop() { need(1); st.pop_back(); }
    ll top() const { need(1); return st.back(); }
    size_t size() const { return st.size(); }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    Calculator calc;
    int Q, errors = 0;
    cin >> Q;
    while (Q--) {
        string op;
        cin >> op;
        try {
            if (op == "push") { ll x; cin >> x; calc.push(x); }
            else if (op == "dup") calc.dup();
            else if (op == "pop") calc.pop();
            else if (op == "top") cout << calc.top() << '\n';
            else if (op == "size") cout << calc.size() << '\n';
            else calc.binary(op);
        } catch (const CalcError& e) {
            cout << "error: " << e.what() << '\n';
            errors++;
        }
    }
    cout << "errors: " << errors << '\n';
    return 0;
}
