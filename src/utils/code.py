import ast

def does_compile(code):
    return get_ast(code) is not None

def get_ast(code):
    try:
        return ast.parse(code)
    except:
        return None 