#include <iostream>
#include <map>
#include <memory>
#include <string>
using namespace std;
typedef long long ll;

class Account {
protected:
    ll balance_ = 0;
public:
    virtual ~Account() = default;
    ll balance() const { return balance_; }
    virtual string type() const = 0;
    virtual bool canWithdraw(ll amt) const = 0;
    virtual void monthEnd() = 0;
    void deposit(ll amt) { balance_ += amt; }
    void withdraw(ll amt) { balance_ -= amt; }   // 呼叫前要先確認 canWithdraw
};

// TODO: class SavingsAccount : public Account
// TODO: class CheckingAccount : public Account

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    map<string, unique_ptr<Account>> bank;
    int Q;
    cin >> Q;
    while (Q--) {
        string op;
        cin >> op;
        // TODO
    }
    return 0;
}
