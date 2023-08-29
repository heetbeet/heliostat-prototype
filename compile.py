import re
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

CYGWIN_PATH = r"C:\Users\simon\Applications\cygwin\bin"


def extract_functions(c_code):
    types = ["double", "float", "int", "char", "void"]
    type_pattern = "|".join(types)
    function_pattern = f"(({type_pattern})\\s+(\\w+)\\s*\\((.*?)\\)\\s*(?=;|\\{{))"

    return re.findall(function_pattern, c_code)

def extract_arg_type(arg_str):
    regex = r"(\w+)\s*(\*?)\s*(\w+)((\[\s*\d+\s*\]\s*)*)"
    match = re.match(regex, arg_str)

    arg_type, pointer, arg_name, all_brackets = match.groups()[:4]

    if all_brackets:
        dims = tuple(int(x) for x in re.findall(r"\[(\d+)\]", all_brackets))
    else:
        dims = ()

    return arg_type, bool(pointer), arg_name, dims


def generate_files(c_file):
    gccdir = Path(c_file).parent.parent / "gcc"
    gccdir.mkdir(exist_ok=True)

    pydir = Path(c_file).parent.parent 
    pydir.mkdir(exist_ok=True)

    # Regular expression for function declarations in C code
    c_code = Path(c_file).read_text()
    regex = r"((?:\w+\s*\*?\s*)+)\s+(\w+)\s*\(([^)]*)\)\s*;"
    function_declarations = extract_functions(c_code)


    # Generate header file
    guardname = Path(c_file).stem.upper() + "_H"
    header_code = f"#ifndef {guardname}\n#define {guardname}\n\n"
    for _, ret_type, func_name, args in function_declarations:
        header_code += f"{ret_type} {func_name}({args});\n"
    header_code += f"\n#endif // {guardname}"

    # Generate Python wrapper
    python_wrapper_code = f"""import ctypes as _ctypes
from pathlib import Path as _Path
import numpy as _np
_this_dir = _Path(__file__).parent.absolute()

# Load the shared library
_lib = _ctypes.CDLL(str(_this_dir / 'gcc/{Path(c_file).stem}.dll'))\n\n"""

    ctype_map = {
        "double": "_ctypes.c_double",
        "float": "_ctypes.c_float",
        "int": "_ctypes.c_int",
        "char": "_ctypes.c_char",
        "void": "None",
    }
    type_map = {
        "double": "_np.float64",
        "float": "_np.float32",
        #"int": "_np.int32",
        "int": "_np.intc",  # Platform-dependent
        "long": "_np.int_",  # Platform-dependent
        "char": "_np.int8",
        "void": "None",
    }

    for _, ret_type, func_name, args in function_declarations:
        ret_type_py = ctype_map[ret_type.strip()]
        
        args_c = [arg.strip() for arg in args.split(",") if arg]

        typewrap = lambda x, dims: f"_ctypes.POINTER({ctype_map[x]})" if dims else ctype_map[x]

        
        args_py = []
        for arg in args_c:
            arg_type, pointer, arg_name, dims = extract_arg_type(arg)
            
            if pointer:
                dims = (1,)

            args_py.append(
                SimpleNamespace(
                name = arg_name,
                passname = arg_name,
                type = arg_type,
                ctype = typewrap(arg_type, dims),
                npobj = f"_np.zeros({tuple((int(i) for i in dims))}, dtype={type_map[arg_type]})",
                pointer = pointer,
                dims = tuple((int(i) for i in dims)),
                returns = arg_name.startswith("return_")
            ))

        python_wrapper_code += f"# Declare argument types for {func_name}\n"
        python_wrapper_code += f"_lib.{func_name}.argtypes = [{', '.join([arg.ctype for arg in args_py])}]\n"
        if ret_type_py != "None":
            python_wrapper_code += f"_lib.{func_name}.restype = {ret_type_py}\n"
        python_wrapper_code += f"def {func_name}({', '.join([arg.name for arg in args_py if not arg.returns])}):\n"

        for arg in [arg for arg in args_py if arg.returns and arg.dims]:
            python_wrapper_code += f"    {arg.name} = {arg.npobj}\n"
        for arg in [arg for arg in args_py if arg.dims]:
            python_wrapper_code += f"    assert {arg.name}.shape == {(arg.dims)}\n"
            python_wrapper_code += f"    {arg.name} = _np.ascontiguousarray({arg.name}).astype({type_map[arg.type]})\n"
            python_wrapper_code += f"    {arg.name}_p = {arg.name}.ctypes.data_as({typewrap(arg.type, True)})\n"
            arg.passname = arg.name + "_p"

        if ret_type_py != "None":
            python_wrapper_code += f"    return _lib.{func_name}({', '.join([arg.passname for arg in args_py])})\n"
        else:
            python_wrapper_code += f"    _lib.{func_name}({', '.join([arg.passname for arg in args_py])})\n"
            python_wrapper_code += f"    return ({', '.join([arg.name + ('[0]' if arg.pointer else '') for arg in args_py if arg.returns])})\n"
        python_wrapper_code += f"\n"
        

    with open(gccdir / (Path(c_file).stem + ".h"), "w") as f:
        f.write(header_code)

    with open(pydir / (Path(c_file).stem + ".py"), "w") as f:
        f.write(python_wrapper_code)


def compile():
    this_dir = Path(__file__).parent.absolute()
    py_dir = this_dir / "helioc"
    c_dir = this_dir / "helioc/c"
    gcc_dir = this_dir / "helioc/gcc"

    for d in [py_dir, c_dir, gcc_dir]:
        d.mkdir(exist_ok=True, parents=True)

    c_files = list(c_dir.glob("*.c"))
    other_files = list(gcc_dir.glob("*")) + list(py_dir.glob("*.py"))

    for file in other_files:
        file.unlink()

    for c_file in c_files:
        generate_files(c_file)

    for c_file in c_files:
        subprocess.call(
            [
                rf"{CYGWIN_PATH}\bash.exe",
                "--login",
                "-c",
                rf'cd "{gcc_dir}"; gcc -m64 -shared -o {c_file.stem}.dll "{c_file}"',
            ]
        )

    shutil.copy2(CYGWIN_PATH + r"/cygwin1.dll", gcc_dir / "cygwin1.dll")

    Path(py_dir / "__init__.py").write_text(
        "\n".join(
            [
                "import ctypes as _ctypes",
                "_cygwin_dll = _ctypes.CDLL(__file__+'/../gcc/cygwin1.dll')",
            ]
            + [
                rf"from . import {i.stem}"
                for i in (py_dir).glob("*.py")
                if i.stem != "__init__"
            ]
        )
    )


if __name__ == "__main__":
    compile()
