from setuptools import setup
import os

def get_package_info(module_name):
    '''
    Read info about package version, author etc
    from <module_name>/package.py

    Return:
        dict {'version': '1.2.3', 'author': 'John Doe', ...}
    '''
    here = os.path.dirname(os.path.abspath(__file__))
    code_globals = {}
    code_locals = {}
    with open(os.path.join(here, module_name, 'package.py')) as f:
        line = f.read()
        code = compile(line, "package.py", 'exec')
        exec(code, code_globals, code_locals)
    
    fixed = {}
    for k, v in code_locals.items():
        if isinstance(v, tuple) and len(v) == 1:
            fixed[k] = v[0]
        else:
            fixed[k] = v
    return fixed

pkg_info = get_package_info('src')

setup(**pkg_info)