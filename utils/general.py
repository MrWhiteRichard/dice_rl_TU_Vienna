# ---------------------------------------------------------------- #

import sys
import os

import numpy as np

import random

# ---------------------------------------------------------------- #

def unpack(d, k):
    if isinstance(d, list): return [ unpack(e, k) for e in d]
    if isinstance(d, dict): return d[k]
    return d

def merge_dicts(*args):
    d = {}

    for arg in args:
        for k, v in arg.items():
            d[k] = v

    return d

def filter_dict(d, blacklist=None, whitelist=None):
    if not isinstance(d, dict): return d

    blacklist_ = blacklist if blacklist is not None else []
    whitelist_ = whitelist if whitelist is not None else d.keys()

    return {
        k: filter_dict(v, blacklist, whitelist)
            for k, v in d.items()
                if k not in blacklist_ and k in whitelist_
    }

def flatten_dict(d):
    d_flattened = {}

    for k, v in d.items():
        if isinstance(v, dict):
            v_flattened = flatten_dict(v)
            d_flattened = merge_dicts(d_flattened, v_flattened)
        else:
            d_flattened[k] = v

    return d_flattened

def dict_to_str(d, blacklist=None, whitelist=None):
    d_filtered = filter_dict(d, blacklist, whitelist)

    s = ""
    for i, (k, v) in enumerate(d_filtered.items()):
        s += f"{k}={v}"
        if i != len(d_filtered)-1: s += ", "
    return s

# ---------------------------------------------------------------- #

def safe_zip(*args):
    args_lens = [len(arg) for arg in args]
    assert len( set(args_lens) ) == 1, args_lens

    return zip(*args)

def list_safe_zip(*args):
    return list( safe_zip(*args) )

def is_list(l):
    A = isinstance(l, list)
    B = isinstance(l, np.ndarray)
    return A or B

def check_have_list(L):
    have_list = False
    list_len = None

    for l in L:
        if is_list(l):
            if have_list:
                check = len(l) == list_len
                msg = "if L has more than one list, the must have the same length"
                assert check, msg
            else:
                have_list = True
                list_len = len(l)

    return have_list, list_len


def list_ify(*args):

    have_list, list_len = check_have_list(args)

    for arg in args:
        if type(arg) is list:
            if have_list:
                check = len(arg) == list_len
                msg = "if args has more than one list, the must have the same length"
                assert check, msg
            else:
                have_list = True
                list_len = len(arg)

    args_list = []
    for arg in args:
        if have_list:
            if isinstance(arg, list):
                arg_list = arg
            else:
                arg_list = [arg] * list_len # type: ignore
        else:
            arg_list = [arg]

        args_list.append(arg_list)

    return tuple(args_list)

# ---------------------------------------------------------------- #

# Function to suppress print statements
class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout  # Save a reference to the original standard output
        sys.stdout = open(os.devnull, 'w')  # Redirect standard output to devnull (discard it)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()  # Close the devnull stream
        sys.stdout = self._original_stdout  # Restore standard output to the original state

# ---------------------------------------------------------------- #

def iterate_print(L, name):
    for l in L:
        print(f"{name}={l}")
        yield l

# ---------------------------------------------------------------- #

def assert_all_are_list(L):
    for l in L:
        assert is_list(l), "all elements of L should be lists"

def shape(l, depth=None):

    if depth is not None:
        s = shape(l)
        assert len(s) == depth
        return s

    else:

        if not is_list(l): return ()
        len_l = len(l)

        have_list, list_len = check_have_list(l)

        if have_list:
            assert_all_are_list(l)
            return len_l, *shape(random.choice(l))

        else:
            return len_l,

# ---------------------------------------------------------------- #
