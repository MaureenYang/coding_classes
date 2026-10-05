#include <iostream>
#include <string>
#include <stdexcept>
using namespace std;
typedef long long ll;

struct Parser {
    string s;
    size_t pos = 0;

    void skip() { while (pos < s.size() && s[pos] == ' ') pos++; }
    char peek() { skip(); return pos < s.size() ? s[pos] : '\0'; }

    ll expr();     // + -
    ll term();     // * / %
    ll unary();    // 負號
    ll primary();  // 數字、括號
};

ll Parser::expr() {
    // TODO
    return 0;
}

ll Parser::term() {
    // TODO：除以 0 時 throw runtime_error("division by zero");
    return 0;
}

ll Parser::unary() {
    // TODO
    return 0;
}

ll Parser::primary() {
    // TODO
    return 0;
}

int main() {
    int T;
    cin >> T;
    string line;
    getline(cin, line);  // 吃掉第一行剩下的換行（第 12 課會解釋為什麼）
    while (T--) {
        getline(cin, line);
        Parser p{line};
        try {
            cout << p.expr() << '\n';
        } catch (const runtime_error& e) {
            cout << e.what() << '\n';
        }
    }
    return 0;
}
