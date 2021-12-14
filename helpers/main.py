from jolang import main
main("""
for(;;){
    func a(){}
    a()
}
""")
# todo do not pass continue/break tokens to functions