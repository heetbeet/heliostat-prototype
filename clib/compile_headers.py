import re
from pathlib import Path

def extract_functions(c_code):
    types = ['double', 'float', 'int', 'char', 'void']
    type_pattern = "|".join(types)
    function_pattern = f"(({type_pattern})\\s+(\\w+)\\s*\\((.*?)\\)\\s*(?=;|\\{{))"

    return re.findall(function_pattern, c_code)


def generate_files(c_file):
    # Regular expression for function declarations in C code
    c_code = Path(c_file).read_text()
    regex = r'((?:\w+\s*\*?\s*)+)\s+(\w+)\s*\(([^)]*)\)\s*;'
    function_declarations = extract_functions(c_code)
    
    # Verify if the regex is capturing the function declarations correctly
    #print("Function Declarations found:")
    #print(function_declarations)
    
    # Generate header file
    guardname = Path(c_file).stem.upper()+"_H"
    header_code = f"#ifndef {guardname}\n#define {guardname}\n\n"
    for _, ret_type, func_name, args in function_declarations:
        header_code += f"{ret_type} {func_name}({args});\n"
    header_code += f"\n#endif // {guardname}"

    # Generate Python wrapper
    python_wrapper_code = f'''import ctypes as _ctypes
from pathlib import Path as _Path
_this_dir = _Path(__file__).parent.absolute()

# Load the shared library
_cygwin_dll = _ctypes.CDLL(r'C:\\Users\\simon\\Applications\\cygwin\\bin\\cygwin1.dll')
_lib = _ctypes.CDLL(str(_this_dir / '{Path(c_file).stem}.dll'))\n\n'''

    type_map = {
        'double': '_ctypes.c_double',
        'float': '_ctypes.c_float',
        'int': '_ctypes.c_int',
        'char': '_ctypes.c_char',
        'void': 'None'
    }

    for _, ret_type, func_name, args in function_declarations:
        ret_type_py = type_map[ret_type.strip()]
        args_py = [type_map[arg.split()[0].strip()] for arg in args.split(',') if arg]
        python_wrapper_code += f"# Declare argument types for {func_name}\n"
        python_wrapper_code += f"_lib.{func_name}.argtypes = [{', '.join(args_py)}]\n"
        python_wrapper_code += f"_lib.{func_name}.restype = {ret_type_py}\n"
        python_wrapper_code += f"{func_name} = _lib.{func_name}\n\n"

    # Save to files
    with open((Path(c_file).with_suffix(".h")), 'w') as f:
        f.write(header_code)

    with open((Path(c_file).with_suffix(".py")), 'w') as f:
        f.write(python_wrapper_code)


for c_file in Path("clib").glob("*.c"):
    print(generate_files(c_file))

