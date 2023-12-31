import re
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
from contextlib import contextmanager
import tempfile
import os

cygwin_dir = Path(__file__).parent.resolve() / "bin/cygwin/cygwin/bin"
tcc_path = Path(__file__).parent.resolve() / "bin/tcc/tcc.exe"
w64devkit_path = Path(__file__).parent.resolve() / "bin/w64devkit/bin/sh.exe"

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
    "int": "_np.intc",  # Platform-dependent
    "long": "_np.int_",  # Platform-dependent
    "char": "_np.int8",
    "void": "None",
}

function_pattern = f"(({'|'.join([re.escape(i) for i in type_map])})\\s+(\\w+)\\s*\\((.*?)\\)\\s*(;|\\{{)?)(\\s*/\\*.*?\\*/)?"


@contextmanager
def dll_exported_source(c_dir):
    with tempfile.TemporaryDirectory() as tdir:
        for file in c_dir.rglob("*.c"):
            c_code = file.read_text()

            def replace(match):
                return f"__declspec(dllexport) {match.group(1)}"

            c_code = re.sub(function_pattern, replace, c_code)

            outfile = Path(tdir) / file.relative_to(c_dir)
            outfile.parent.mkdir(exist_ok=True, parents=True)
            outfile.write_text(c_code)

        yield Path(tdir)


def extract_functions(c_code):
    # Add re.DOTALL to make '.' match any character including newlines
    unpacked = [
        [ret_type, func_name, args, docstring]
        for _, ret_type, func_name, args, _, docstring in re.findall(
            function_pattern, c_code, re.DOTALL
        )
    ]
    return unpacked


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
    function_declarations = extract_functions(c_code)

    # Generate header file
    guardname = Path(c_file).stem.upper() + "_H"
    header_code = f"#ifndef {guardname}\n#define {guardname}\n\n"
    for ret_type, func_name, args, docstring in function_declarations:
        header_code += f"{ret_type} {func_name}({args});\n"
    header_code += f"\n#endif // {guardname}"

    # Generate Python wrapper
    python_wrapper_code = f"""import ctypes as _ctypes
from pathlib import Path as _Path
import numpy as _np
_this_dir = _Path(__file__).parent.absolute()
_lib = _ctypes.CDLL(str(_this_dir / 'gcc/{Path(c_file).stem}.dll'))\n\n"""

    for ret_type, func_name, args, docstring in function_declarations:
        ret_type_py = ctype_map[ret_type.strip()]

        args_c = [arg.strip() for arg in args.split(",") if arg]

        typewrap = (
            lambda x, dims: f"_ctypes.POINTER({ctype_map[x]})" if dims else ctype_map[x]
        )

        args_py = []
        for arg in args_c:
            arg_type, pointer, arg_name, dims = extract_arg_type(arg)

            if pointer:
                dims = (1,)

            args_py.append(
                SimpleNamespace(
                    name=arg_name,
                    passname=arg_name,
                    type=arg_type,
                    ctype=typewrap(arg_type, dims),
                    npobj=f"_np.zeros({tuple((int(i) for i in dims))}, dtype={type_map[arg_type]})",
                    pointer=pointer,
                    dims=tuple((int(i) for i in dims)),
                    returns=arg_name.startswith("return_"),
                )
            )

        python_wrapper_code += f"\n"
        python_wrapper_code += f"_lib.{func_name}.argtypes = [{', '.join([arg.ctype for arg in args_py])}]\n"
        if ret_type_py != "None":
            python_wrapper_code += f"_lib.{func_name}.restype = {ret_type_py}\n"
        python_wrapper_code += f"def {func_name}({', '.join([arg.name for arg in args_py if not arg.returns])}):\n"
        if docstring:
            python_wrapper_code += f"    r'''{docstring.strip()[2:-2]}'''\n"

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
        # hack to replace double with float to test precision
        # c_file.write_text(c_file.read_text().replace("double", "float"))
        c_file.write_text(c_file.read_text().replace("float", "double"))
        generate_files(c_file)

    # Tinycc
    # with dll_exported_source(c_dir) as exported_c_dir:
    #    for c_file in exported_c_dir.rglob("*.c"):
    #        subprocess.call(
    #            [
    #                f"{tcc_path}",
    #                f"-I{gcc_dir}",
    #                f"-shared",
    #                f"-o",
    #                f"{gcc_dir / c_file.stem}.dll",
    #                f"{c_file}",
    #            ]
    #        )

    # Cygwin
    # for c_file in c_files:
    #    subprocess.call(
    #        [
    #            rf"{cygwin_dir}\..\..\cygwin-portable.cmd",
    #            rf'cd "{gcc_dir}"; gcc -m64 -shared -o {c_file.stem}.dll "{c_file}"',
    #        ]
    #    )
    # shutil.copy2(f"{cygwin_dir}/cygwin1.dll", gcc_dir / "cygwin1.dll")

    # W64devkit
    os.environ["PATH"] = f"{w64devkit_path.parent};{os.environ['PATH']}"
    for c_file in c_files:
        subprocess.call(
            [
                rf"{w64devkit_path}",
                "-c",
                rf'gcc "-I{gcc_dir}" -m64 -shared -o "{gcc_dir / (c_file.stem+".dll")}" "{c_file}"',
            ]
        )

    Path(py_dir / "__init__.py").write_text(
        "\n".join(
            [
                "import ctypes as _ctypes",
                # "_cygwin_dll = _ctypes.CDLL(__file__+'/../gcc/cygwin1.dll')",
            ]
            + [
                rf"from . import {i.stem}"
                for i in (py_dir).glob("*.py")
                if i.stem != "__init__"
            ]
        )
    )

    # if not all c files have dll files, delete gcc directory and all python files not named __init__.py
    if len(list(gcc_dir.glob("*.dll"))) != len(c_files):
        shutil.rmtree(gcc_dir)
        for file in py_dir.glob("*.py"):
            if file.stem != "__init__":
                file.unlink()

        return False
    
    return True

if __name__ == "__main__":
    compile()
