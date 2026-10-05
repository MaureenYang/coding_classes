#include <climits>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
typedef long long ll;

// 所有計算機錯誤的基底類別
class CalcError : public runtime_error {
public:
    using runtime_error::runtime_error;   // 繼承建構子
};
// TODO: class StackUnderflow : public CalcError ...
// TODO: class DivisionByZero : public CalcError ...
// TODO: class Overflow : public CalcError ...

class Calculator {
    vector<ll> st;
public:
    void push(ll x) { st.push_back(x); }
    void binary(const string& op) {
        // TODO: 檢查 → 計算 → 才修改 st
    }
    // TODO: dup, pop, top, size
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
            // TODO
        } catch (const CalcError& e) {
            cout << "error: " << e.what() << '\n';
            errors++;
        }
    }
    cout << "errors: " << errors << '\n';
    return 0;
}
