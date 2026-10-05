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
    void withdraw(ll amt) { balance_ -= amt; }
};

class SavingsAccount : public Account {
    ll rate_;
public:
    explicit SavingsAccount(ll rate) : rate_(rate) {}
    string type() const override { return "savings"; }
    bool canWithdraw(ll amt) const override { return balance_ - amt >= 0; }
    void monthEnd() override { balance_ += balance_ * rate_ / 100; }
};

class CheckingAccount : public Account {
    ll limit_;
public:
    explicit CheckingAccount(ll limit) : limit_(limit) {}
    string type() const override { return "checking"; }
    bool canWithdraw(ll amt) const override { return balance_ - amt >= -limit_; }
    void monthEnd() override { if (balance_ < 0) balance_ -= 10; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    map<string, unique_ptr<Account>> bank;
    auto find = [&](const string& id) -> Account* {
        auto it = bank.find(id);
        return it == bank.end() ? nullptr : it->second.get();
    };
    int Q;
    cin >> Q;
    while (Q--) {
        string op;
        cin >> op;
        if (op == "open") {
            string kind, id;
            ll x;
            cin >> kind >> id >> x;
            if (bank.count(id)) { cout << "error: duplicate id\n"; continue; }
            if (kind == "savings") bank[id] = make_unique<SavingsAccount>(x);
            else bank[id] = make_unique<CheckingAccount>(x);
            cout << "ok\n";
        } else if (op == "deposit" || op == "withdraw") {
            string id;
            ll amt;
            cin >> id >> amt;
            Account* a = find(id);
            if (!a) cout << "error: no such account\n";
            else if (amt <= 0) cout << "error: invalid amount\n";
            else if (op == "deposit") { a->deposit(amt); cout << "ok\n"; }
            else if (!a->canWithdraw(amt)) cout << "error: insufficient funds\n";
            else { a->withdraw(amt); cout << "ok\n"; }
        } else if (op == "transfer") {
            string from, to;
            ll amt;
            cin >> from >> to >> amt;
            Account *a = find(from), *b = find(to);
            if (!a || !b) cout << "error: no such account\n";
            else if (amt <= 0) cout << "error: invalid amount\n";
            else if (a == b) cout << "error: same account\n";
            else if (!a->canWithdraw(amt)) cout << "error: insufficient funds\n";
            else { a->withdraw(amt); b->deposit(amt); cout << "ok\n"; }
        } else if (op == "month") {
            for (auto& [id, acc] : bank) acc->monthEnd();
            cout << "ok\n";
        } else if (op == "balance") {
            string id;
            cin >> id;
            Account* a = find(id);
            if (!a) cout << "error: no such account\n";
            else cout << a->balance() << '\n';
        } else if (op == "report") {
            if (bank.empty()) cout << "no accounts\n";
            for (auto& [id, acc] : bank) cout << id << ' ' << acc->type() << ' ' << acc->balance() << '\n';
        }
    }
    return 0;
}
