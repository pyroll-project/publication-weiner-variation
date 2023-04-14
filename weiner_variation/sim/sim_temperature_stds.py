#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xed48bd93

# Compiled with Coconut version 2.2.0

# Coconut Header: -------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division
import sys as _coconut_sys
_coconut_header_info = ('2.2.0', '', False, False, False)
import os as _coconut_os
_coconut_cached__coconut__ = _coconut_sys.modules.get(str('__coconut__'))
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.abspath(__file__))
_coconut_pop_path = False
if _coconut_cached__coconut__ is None or getattr(_coconut_cached__coconut__, "_coconut_header_info", None) != _coconut_header_info and _coconut_os.path.dirname(_coconut_cached__coconut__.__file__ or "") != _coconut_file_dir:
    if _coconut_cached__coconut__ is not None:
        _coconut_sys.modules[str('_coconut_cached__coconut__')] = _coconut_cached__coconut__
        del _coconut_sys.modules[str('__coconut__')]
    _coconut_sys.path.insert(0, _coconut_file_dir)
    _coconut_pop_path = True
    _coconut_module_name = _coconut_os.path.splitext(_coconut_os.path.basename(_coconut_file_dir))[0]
    if _coconut_module_name and _coconut_module_name[0].isalpha() and all(c.isalpha() or c.isdigit() for c in _coconut_module_name) and "__init__.py" in _coconut_os.listdir(_coconut_file_dir):
        _coconut_full_module_name = str(_coconut_module_name + ".__coconut__")
        import __coconut__ as _coconut__coconut__
        _coconut__coconut__.__name__ = _coconut_full_module_name
        for _coconut_v in vars(_coconut__coconut__).values():
            if getattr(_coconut_v, "__module__", None) == str('__coconut__'):
                try:
                    _coconut_v.__module__ = _coconut_full_module_name
                except AttributeError:
                    _coconut_v_type = type(_coconut_v)
                    if getattr(_coconut_v_type, "__module__", None) == str('__coconut__'):
                        _coconut_v_type.__module__ = _coconut_full_module_name
        _coconut_sys.modules[_coconut_full_module_name] = _coconut__coconut__
from __coconut__ import *
from __coconut__ import _coconut_tail_call, _coconut_tco, _coconut_call_set_names, _coconut_handle_cls_kwargs, _coconut_handle_cls_stargs, _namedtuple_of, _coconut, _coconut_super, _coconut_Expected, _coconut_MatchError, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_multi_dim_arr, _coconut_mk_anon_namedtuple, _coconut_matmul, _coconut_py_str, _coconut_flatten, _coconut_multiset, _coconut_back_none_pipe, _coconut_back_none_star_pipe, _coconut_back_none_dubstar_pipe, _coconut_forward_none_compose, _coconut_back_none_compose, _coconut_forward_none_star_compose, _coconut_back_none_star_compose, _coconut_forward_none_dubstar_compose, _coconut_back_none_dubstar_compose
if _coconut_pop_path:
    _coconut_sys.path.pop(0)

# Compiled Coconut: -----------------------------------------------------------

# ---
# jupyter:
#   jupytext:
#     formats: ipynb,coco:percent
#     text_representation:
#       extension: .coco
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Coconut
#     language: coconut
#     name: coconut
# ---

# %%
from weiner_variation.sim.data_structures import DrawInput
from weiner_variation.sim.process import PASS_SEQUENCE
from weiner_variation.sim.process import DIAMETER
from weiner_variation.sim.process import TEMPERATURE
from weiner_variation.sim.process import create_in_profile
from weiner_variation.sim.config import SAMPLE_COUNT
from weiner_variation.sim.config import FIELDS
from weiner_variation.sim.config import SEED
from weiner_variation.config import DATA_DIR
from weiner_variation.sim.task_sim_temperature_stds import FACTORS

import pandas as pd
import numpy as np
from scipy.stats import norm
from copy import deepcopy
import tqdm
from multiprocessing import Pool

# %%
import pyroll.basic as pr

# %%
nominal = DrawInput(DIAMETER, TEMPERATURE)

# %%
input_dist = pd.read_csv(DATA_DIR / "input_dist.csv", index_col=0, header=0)
input_dist

# %%
def worker(draw  # type: DrawInput
    ):
    ip = create_in_profile(diameter=draw.diameter, temperature=draw.temperature)

    sequence = deepcopy(PASS_SEQUENCE)
    sequence.solve(ip)

    return ((dict)((map)(lambda t: (("draw", t[0]), t[1]), draw.__dict__.items()))) | ((dict)((flatten)((starmap)(lambda key, extractor: ((filter)(lambda t: t[1] is not None, (map)(lambda u: ((key, u.label), extractor(u)), (filter)(lambda u: isinstance(u, pr.RollPass), sequence.units)))), FIELDS.items()))))

# %%

for f in FACTORS:
    diameter_dist = norm(loc=input_dist.loc["diameter", "mean"], scale=input_dist.loc["diameter", "std"])
    temperature_dist = norm(loc=input_dist.loc["temperature", "mean"], scale=input_dist.loc["temperature", "std"] * f)

    RNG = np.random.default_rng(SEED)
    diameters = diameter_dist.rvs(random_state=RNG, size=SAMPLE_COUNT)
    temperatures = temperature_dist.rvs(random_state=RNG, size=SAMPLE_COUNT)

    draws = [nominal,] + [DrawInput(d, t) for d, t in zip(diameters, temperatures)]
    results = (list)(tqdm.tqdm(Pool().imap(worker, draws), total=SAMPLE_COUNT))
    df = (((pd.DataFrame)((dict)((enumerate)(results)))).T).infer_objects()
    df.to_csv(DATA_DIR / "sim_temperature_stds_results" / "{_coconut_format_0}.csv".format(_coconut_format_0=(f)))
