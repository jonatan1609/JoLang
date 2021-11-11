from sys import path
from pathlib import Path

path.append(str(Path("..").parent))
from jolang import main

print(main("abcd test"))
