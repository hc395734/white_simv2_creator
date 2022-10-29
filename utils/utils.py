import json, itertools
import numpy as np

from data_core import *

def dates_securities_generator(market,
                               asset,
                               universe,
                               date_start,
                               date_end,
                               num_sections,
                               num_days_burnin,
                               banned_dates = [],
                               verbose = True):
    
    try:
        ra = constructor_set_region_asset(market, asset)
        date_list = ra.dates.get_trading_dates(date_start, date_end, fmt = "int")
        date_list = sorted(set(date_list) - set(banned_dates))

        _num_total = len(date_list)
        _num_days_each = int(np.ceil(((_num_total - num_days_burnin) + \
                                      num_days_burnin * num_sections) / \
                                     num_sections))

        _values_1 = [list(date_list[_i * (_num_days_each - num_days_burnin)\
                                    : _i  * (_num_days_each - num_days_burnin) + _num_days_each]) \
                     for _i in range(num_sections)]
        _values_2 = [ra.univs.get_all_jkeys(universe, _v[0], _v[-1]) \
                     for _v in _values_1]
        _values_2 = [list(int(sec) for sec in _list_sec) \
                     for _list_sec in _values_2]
        _keys = ["section{}".format(("%i"%i).zfill(2)) \
                 for i in range(len(_values_1))]

        _output = dict(zip(_keys, list(zip(_values_1, _values_2))))

        if verbose:
            print("dates/securities generation successful")
            print(dict(zip(_keys,
                           list(zip(["num_dates = {}".format(len(_v)) for _v in _values_1],
                                    ["num_securities = {}".format(len(_v)) for _v in _values_2])))))

        return _output
    
    except Exception as _e:
        print("dates/securities generation FAILED")
        print(_e)
        return dict()

def flags_generator(setup_path):
    
    try:
        # flags is a dictionary with keys of flag names and values of lists of flag values.
        with open("setup/flags.json") as _f:
            setup = json.load(_f)
        
        flat_flags = []
        for _k, _v in zip(setup.keys(), setup.values()):
            flat_flags.append(list(["sd/white/{}/{}".format(_ki, _vi) \
                                    for _ki, _vi in itertools.product([_k], _v)]))

        _values = [list(_flags) \
                   for _flags in itertools.product(*flat_flags)]
        _keys = ["experiment{}".format(("%i"%i).zfill(2)) \
                 for i in range(len(_values))]

        return dict(zip(_keys, _values))
    
    except:
        return {"experiment00": []}
