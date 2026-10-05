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

    ll expr();
    ll term();
    ll unary();
    ll primary();
};

ll Parser::expr() {
    ll v = term();
    while (peek() == '+' || peek() == '-') {
        char op = s[pos++];
        ll r = term();
        v = (op == '+') ? v + r : v - r;
    }
    return v;
}

ll Parser::term() {
    ll v = unary();
    while (peek() == '*' || peek() == '/' || peek() == '%') {
        char op = s[pos++];
        ll r = unary();
        if (op == '*') v *= r;
        else {
            if (r == 0) throw runtime_error("division by zero");
            v = (op == '/') ? v / r : v % r;   // C++ 本身就是向 0 取整
        }
    }
    return v;
}

ll Parser::unary() {
    if (peek() == '-') { pos++; return -unary(); }
    return primary();
}

ll Parser::primary() {
    if (peek() == '(') {
        pos++;
        ll v = expr();
        peek();
        pos++;  // ')'
        return v;
    }
    skip();
    ll v = 0;
    while (pos < s.size() && isdigit((unsigned char)s[pos])) v = v * 10 + (s[pos++] - '0');
    return v;
}

int main() {
    int T;
    cin >> T;
    string line;
    getline(cin, line);
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
