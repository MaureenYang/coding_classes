#include <iostream>
using namespace std;
typedef long long ll;

class Matrix {
public:
    int rows, cols;
    ll** a;

    Matrix(int r, int c) : rows(r), cols(c), a(new ll*[r]) {
        for (int i = 0; i < r; i++) a[i] = new ll[c]();
    }
    ~Matrix() {
        for (int i = 0; i < rows; i++) delete[] a[i];
        delete[] a;
    }
    Matrix(const Matrix&) = delete;
    Matrix& operator=(const Matrix&) = delete;

    void read() {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) cin >> a[i][j];
    }
    void print() const {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) cout << a[i][j] << (j + 1 < cols ? ' ' : '\n');
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int r1, c1, r2, c2;
    cin >> r1 >> c1;
    Matrix A(r1, c1);
    A.read();
    cin >> r2 >> c2;
    Matrix B(r2, c2);
    B.read();

    if (r1 != r2 || c1 != c2) cout << "A+B: size mismatch\n";
    else {
        Matrix S(r1, c1);
        for (int i = 0; i < r1; i++)
            for (int j = 0; j < c1; j++) S.a[i][j] = A.a[i][j] + B.a[i][j];
        cout << "A+B:\n";
        S.print();
    }

    if (c1 != r2) cout << "A*B: size mismatch\n";
    else {
        Matrix P(r1, c2);
        for (int i = 0; i < r1; i++)
            for (int k = 0; k < c1; k++) {          // i-k-j 的順序對快取比較友善
                ll x = A.a[i][k];
                for (int j = 0; j < c2; j++) P.a[i][j] += x * B.a[k][j];
            }
        cout << "A*B:\n";
        P.print();
    }

    Matrix T(c1, r1);
    for (int i = 0; i < r1; i++)
        for (int j = 0; j < c1; j++) T.a[j][i] = A.a[i][j];
    cout << "T(A):\n";
    T.print();
    return 0;
}
