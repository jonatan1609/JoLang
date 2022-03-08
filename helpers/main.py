from jolang import main

main("""
k = [print()]
k.append(1)
k.append(print())
k.append([k])
print(k)
""")

# todo: add frames for the main scope, delete the last frame when exiting the function