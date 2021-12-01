from time import time
from jolang import main
start = time()
main("""
func scoped(){
    %macro a "A"
    print(a)
}
scoped()
print(a)
""")
print(time() - start)