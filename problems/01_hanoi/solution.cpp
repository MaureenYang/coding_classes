#include <iostream>
using namespace std;

void hanoi(int n, char from, char via, char to) {
    if (n == 0) return;
    hanoi(n - 1, from, to, via);
    cout << "move disk " << n << " from " << from << " to " << to << '\n';
    hanoi(n - 1, via, from, to);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    cout << (1 << n) - 1 << '\n';
    hanoi(n, 'A', 'B', 'C');
    return 0;
}
