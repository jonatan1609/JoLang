from jolang import main
main("""
func a(e) {
    func c(n) {
        return e(e)(n)
    }
    return c
}

func b(e) {
    func d(n) {
        return n == 0 || n * e(e)(n - 1)
    }
    return d
}

print(a(b)(5))
""")
