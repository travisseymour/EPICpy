import re
import sys
from typing import Optional

from cppinclude import epiclib_include
import cppyy
from loguru import logger as log
from pprint import pprint
from apputils import LIBNAME
import random
from io import StringIO  ## for Python 3
from epiclibwords import words

# ------------------------------------------------------
# Load Various Include files and objects we will need
# The location of the library depends on OS, this is
# figured out in main.py which sets apputils.LIBNAME
# so that the correct library can be loaded when this
# module is imported.
# ------------------------------------------------------

print(f"{LIBNAME=}")
cppyy.load_library(LIBNAME)

epiclib_include("Framework classes/Parameter.h")
epiclib_include("Utility Classes/Symbol.h")
epiclib_include("Utility Classes/Symbol_utilities.h")
epiclib_include("Utility Classes/Output_tee.h")
epiclib_include("Utility Classes/Geometry.h")
epiclib_include("Utility Classes/Statistics.h")
epiclib_include("Utility Classes/Point.h")
epiclib_include("Utility Classes/Random_utilities.h")
epiclib_include("Standard_Symbols.h")

from cppyy.gbl import Geometry_Utilities as GU
from cppyy.gbl import set_random_number_generator_seed
from cppyy.gbl import Symbol, concatenate_to_Symbol

# set seed so results are reproducible
random.seed(1138)
set_random_number_generator_seed(1138)


def get_marker(key: str) -> str:
    minimum, maximum = 0, 100
    if key in ('int', 'long'):
        return f"{random.randint(minimum, maximum):0.3f}"
    elif key in ('double', 'real'):
        return f'{random.randint(minimum, maximum):0.3f}'
    elif key == 'bool':
        return str(int(random.choice((True, False))))
    elif key == 'str':
        return f'"{random_string()}"'
    elif key == 'GU.Point':
        return f'GU.Point({random.uniform(minimum, maximum):0.3f}, {random.uniform(minimum, maximum):0.3f})'
    elif key == 'GU.Line_segment':
        r1, r2 = random.uniform(minimum, maximum), random.uniform(minimum, maximum)
        dx = random.uniform(minimum, maximum)
        return f'GU.Line_segment(GU.Point({r1:0.3f}, {r2:0.3f}), GU.Point({r1 + dx:0.3f}, {r2 + dx:0.3f}))'
    elif key == 'GU.Polar_vector':
        return f'GU.Polar_vector({random.uniform(minimum, maximum):0.3f}, {random.uniform(minimum, maximum):0.3f})'
    elif key == 'GU.Cartesian_vector':
        return f'GU.Cartesian_vector({random.uniform(minimum, maximum):0.3f}, {random.uniform(minimum, maximum):0.3f})'
    elif key == 'GU.Size':
        return f'GU.Size({random.uniform(minimum, maximum):0.3f},{random.uniform(minimum, maximum):0.3f})'
    elif key == 'GU.Polygon':
        return f'GU.Polygon({random_list("GU.Point", length=3)})'
    elif key == 'Symbol':
        return f'Symbol("{random_string()}")'
    else:
        raise ValueError('unknown marker passed to get_marker()')


def random_list(kind, length:int=2) -> str:
    assert kind in ['int', 'long', 'double', 'GU.Point', 'GU.Line_segment', 'GU.Polar_vector', 'GU.Size',
                    'GU.Cartesian_vector', 'str', 'Symbol', 'bool']

    if length == 1:
        return f'[{get_marker(kind)}]'.replace('(', '{').replace(')', '}').replace(', ', 'zzzz')
    elif length == 2:
        return f'[{get_marker(kind)}zzzz{get_marker(kind)}]'.replace('(', '{').replace(')', '}').replace(', ', 'zzzz')
    else:
        # for polygon
        p1, p2 = get_marker(kind), get_marker(kind)
        return f'[{p1}zzzz{p2}zzzz{p1}]'.replace('(', '{').replace(')', '}').replace(', ', 'zzzz')


def random_symbol(max_words: int = 1, add_number: bool = False) -> Symbol:
    if add_number:
        return concatenate_to_Symbol(''.join(random.sample(words, max_words)), random.randint(0, 99))
    else:
        return Symbol(''.join(random.sample(words, max_words)))


def random_string(max_words: int = 2) -> str:
    return ''.join(random.sample(words, max_words))


def random_point(maximum: float = 100.00) -> GU.Point:
    return GU.Point(
        random.uniform(0.0, maximum),
        random.uniform(0.0, maximum)
    )


def random_size(maximum: float = 100.00) -> GU.Point:
    return GU.Size(random.uniform(0.0, maximum), random.uniform(0.0, maximum))


def random_line_segment(maximum: float = 100.00) -> GU.Line_segment:
    p1 = random_point()
    p2 = GU.Point(p1.x + random.uniform(0.0, maximum), p1.y + random.uniform(0.0, maximum))
    return GU.Line_segment(p1, p2)


def random_polar_vector(kind: str = 'double,double') -> GU.Polar_vector:
    if kind == 'double,double':
        return GU.Polar_vector(random.uniform(0.0, 100.00), random.uniform(0.0, 100.00))
    elif kind == 'point,point':
        return GU.Polar_vector(random_point(), random_point())
    elif kind == 'Cartesian_vector':
        return GU.Polar_vector(random_cartesian_vector('double,double'))
    else:
        raise NotImplementedError(f'no random pv for {kind=}')


def random_cartesian_vector(kind: str = 'double,double') -> GU.Cartesian_vector:
    if kind == 'double,double':
        return GU.Cartesian_vector(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0))
    elif kind == 'point,point':
        return GU.Cartesian_vector(random_point(), random_point())
    elif kind == 'Polar_vector':
        return GU.Cartesian_vector(random_polar_vector('double,double'))
    else:
        raise NotImplementedError(f'no random cv for {kind=}')


def get_help_text(obj) -> str:
    io = StringIO('')
    sys.stdout = io
    help(obj)
    sys.stdout = sys.__stdout__
    return io.getvalue().replace(' |  ', '')


def get_methods_text(help_text: str) -> str:
    txt = help_text.replace('Methods defined here:', '-' * 70)
    sections = txt.split('-' * 70)
    return sections[1].strip()


def get_weakref_properties(help_text: str) -> list:
    top = 'Data descriptors defined here:'
    if top not in help_text:
        return []
    txt = help_text[help_text.find(top):]
    if not txt:
        return []
    txt = txt.replace(top, '')
    sections = txt.split('-' * 70)
    sections = [section for section in sections if '__weakref__' in section]
    if not sections:
        return []
    section = sections[0][sections[0].find('__weakref__'):].replace('__weakref__', '')
    lines = section.splitlines(keepends=False)
    properties = [aline.strip() for aline in lines if aline and not aline.startswith(' ')]
    return list(set(properties))


def get_methods(methods_text: str, namespace: str = '') -> list:
    # split by section so we can remove __assign__(...) and __init__(...) sections
    methods = [method for method in methods_text.strip().split('\n\n') if not method.startswith('__')]
    # put back together for line by line processing
    methods = '\n\n'.join(methods).splitlines(keepends=False)
    # remove stubs
    methods = [aline.removeprefix('    ') for aline in methods if aline.startswith('    ') and not aline.endswith('.')]
    # remove return and namespace
    methods2 = []
    for method in methods:
        left_side, right_side = re.split(r'\(', method, maxsplit=1)  # before and after first left-parens
        left_side = re.sub(r'^\w+ ', '', re.sub(r'\w+::', '', left_side))
        methods2.append(f"{left_side}({right_side}")

    # clean
    methods2 = [cleanup(method, namespace) for method in methods2]
    return list(set(methods2))


def get_initializers(methods_text: str, namespace: str = '') -> list:
    # split by section so we can only accept __init__(...) section
    methods = [method for method in methods_text.strip().split('\n\n') if method.startswith('__init__')]
    # put back together for line by line processing
    methods = '\n\n'.join(methods).splitlines(keepends=False)
    # remove stubs
    methods = [aline.removeprefix('    ') for aline in methods if aline.startswith('    ')]
    # clean
    methods = [cleanup(method, namespace, is_init=True) for method in methods]
    return list(set(methods))


def get_properties(methods_text: str) -> list:
    '''AFAIK, these properties only show up in structs (like Point). Otherwise DK uses get_xxx() methods'''
    # split by section so we can only accept __weakref__(...) section
    methods = [method for method in methods_text.strip().split('\n\n') if method.startswith('__weakref__')]
    # put back together for line by line processing
    properties = '\n\n'.join(methods).splitlines(keepends=False)
    # clean
    properties = [prop.strip() for prop in properties]
    return properties


def cleanup(text: str, namespace: str = '', is_init: bool = False) -> str:
    # removals
    txt = re.sub(r'(&| *const *| *extern *)', '', text).replace('  ', ' ')
    # replacements
    txt = txt.replace('Geometry_Utilities::', 'GU.')
    if is_init:
        txt = re.sub(r"\b(\w+)::\1", rf'{namespace}.\1' if namespace else r'\1',
                     txt)  # initializers may be Point::Point()
    else:
        txt = re.sub(r"\w+::", '', txt)

    txt = txt.replace('std::string', 'str')
    txt = txt.replace('char*', 'str')

    # deal with parameters that are vectors of something
    list_params = re.findall(r'(std::vector\<([\w\.\:]+)\>)', txt)
    for whole, item_type in list_params:
        # OLD
        # itm_typ = item_type.replace(f"{namespace}.", f"{namespace}_")
        # itm_typ = itm_typ.replace('::', '.').replace('*', '').replace('&', '')
        # itm_typ = itm_typ.split('.')[-1]
        # txt = txt.replace(whole, f'random_list[{itm_typ}]')
        # txt = txt.replace(f"{namespace}_", f"{namespace}.")
        # txt = txt.replace('random.list', 'random_list')

        # NEW
        txt = txt.replace(whole, random_list(item_type))

    return txt


def get_func_sig(method_text: str) -> Optional[tuple]:
    try:
        func, params = re.search(r'([^\(]+)\(([^\)]*)\)', method_text).groups()
        func = func.split(' ')[-1]
        func = func.strip()
        params = params.strip()
        if params:
            # We just want the types
            params = [param.split(' ')[0].strip() for param in re.split(r' *, *', params)]

        return func, params

    except Exception as e:
        log.exception(e)
        return None


def brackets2parens(param: str) -> str:
    return param.replace('[', '(').replace(']', ')')


def get_calls(func_sigs: list, prefix: str = '') -> list:
    calls = list()
    for method in func_sigs:
        func, params = get_func_sig(method)
        if not params:
            func_sig = f"{prefix}{func}()"
        else:
            rparams = [param if param.startswith('[') else get_marker(param) for param in params]
            rparams = ', '.join(rparams)
            func_sig = f"{prefix}{func}({rparams})"
        calls.append(func_sig)
    return calls


def exercise_namespace(namespace, ns_name, print_result: bool = False) -> list:
    '''
    Like exercise_object but where you are just exercise staticmethods in a namespace
    '''

    # get all available info about the object
    obj_help_text = get_help_text(namespace)
    methods_text = get_methods_text(obj_help_text)
    the_methods = get_methods(methods_text, namespace)

    # get python calls we can make with eval/exec to exercise initializers and methods
    method_calls = get_calls(the_methods, prefix=f'{ns_name}.')

    print('\n\n*** METHOD CALLS ***')
    pprint(method_calls, width=100)

    print('\nEXERCISING OBJECT...')
    results = []

    for func_call in method_calls:
        res = eval(func_call, globals(), locals())
        res = str(res)
        results.append({'object': ns_name, 'init': 'namespace', 'kind': 'method', 'call': func_call, 'result': res})

    if print_result:
        print(f'\n============================{ns_name}============================')
        pprint(results, width=max(len(str(item)) for item in results) + 5)

    return results


def exercise_object(obj, obj_name: str, init_properties: Optional[list] = None, namespace: str = '',
                    print_result: bool = False) -> list:
    '''
    Given an object, exercise its initializers and methods.
    Note that these are not tests because there is no target.
    We're just asking what a set of code does across a range of inputs
    (currently the idea is to use this infor to test the python version
    of EPICLib against DK's C++ version)

    NOTE: Some objects (e.g., Point) have attributes like .x and .y
    that can be used to make sure initializers are working as expected.
    You can specify the ones you want used as init_properties, e.g.:
    ['x', 'y']
    '''

    # get all available info about the object
    obj_help_text = get_help_text(obj)
    methods_text = get_methods_text(obj_help_text)
    the_inits = get_initializers(methods_text, namespace)
    the_methods = get_methods(methods_text, namespace)
    the_properties = get_weakref_properties(obj_help_text)
    the_properties = [f'obj.{prop}' for prop in the_properties]

    # get python calls we can make with eval/exec to exercise initializers and methods
    init_calls = get_calls(the_inits, prefix='')
    method_calls = get_calls(the_methods, prefix='obj.')

    # random_list() makes lists like this [something{}xxxxsomething{}] instead of [something(), something()] so
    # that the list survives other parsing s. Here we need to fix that:
    def list_fix(text: str) -> str:
        if 'zzzz' in text:
            return text.replace('{', '(').replace('}', ')').replace('zzzz', ', ')
        else:
            return text

    init_calls = [list_fix(item) for item in init_calls]
    method_calls = [list_fix(item) for item in method_calls]

    print('\n\n*** INIT CALLS ***')
    pprint(init_calls, width=100)
    print('\n\n*** METHOD CALLS ***')
    pprint(method_calls, width=100)
    print('\n\n*** OBJECT PROPERTIES ***')
    pprint(the_properties, width=100)

    print('\nEXERCISING OBJECT...')
    results = []

    for init_call in init_calls:
        # initialize obj
        obj = eval(init_call)
        for prop_call in the_properties:
            res = eval(prop_call, globals(), locals())
            res = str(res)
            results.append(
                {'object': obj_name, 'init': init_call, 'kind': 'property', 'call': prop_call, 'result': res})
        for func_call in method_calls:
            try:
                res = eval(func_call, globals(), locals())
                res = str(res)
            except Exception as e:
                res = str(e)
            results.append({'object': obj_name, 'init': init_call, 'kind': 'method', 'call': func_call, 'result': res})

        for comparison in ('==', '!=', '<', '>', '<=', '>='):
            try:
                print(f"{init_call}{comparison}{init_call}")
                res = str(eval(f'{init_call}{comparison}{init_call}'))
            except Exception as e:
                res = str(e)
            results.append({'object': obj_name, 'init': init_call, 'kind': f'comparison{comparison}', 'call': f"{init_call}{comparison}{init_call}", 'result': res})


    if print_result:
        print(f'\n============================{obj_name}============================')
        pprint(results, width=max(len(str(item)) for item in results) + 5)

    return results

def clean_result(res) -> str:
    out = re.sub(r'[ \t\n]{2,}', ' ', str(res))
    return out
