0<0# : ^
r'''
@"%~dp0\venv\scripts\python.exe" "%~dp0\%~n0.cmd" %*
@exit /b %errorlevel%
'''

import compile
import hashlib
from pathlib import Path
import time

this_dir = Path(__file__).parent.resolve()

def get_md5s():
    md5s = {}
    for c_file in Path(this_dir / "helioc/c").rglob("*.c"):
        md5s[c_file] = hashlib.md5(c_file.read_bytes()).hexdigest()
    return md5s

def compare_dicts(a, b):
    return sorted(a.items()) == sorted(b.items())


md5s = {}

def re_compile():
    md5s_update = get_md5s()
    if not compare_dicts(md5s, md5s_update):
        md5s.clear()
        md5s.update(md5s_update)

        print("\n*******************************************")
        print("Recompiling at " + time.strftime("%H:%M:%S"))
        compile.compile()


if __name__ == "__main__":
    while True:
        re_compile()
        time.sleep(0.5)