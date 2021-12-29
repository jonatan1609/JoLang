from jolang import main
main("""
func a(){
if(1){return 8}
print(a)
}
print(a())
""")


# todo: add frames for the main scope, delete the last frame when exiting the function