import os, json, itertools

import pandas as pd

from data_core import *
from utils.utils import dates_securities_generator, flags_generator

class multi_experiments_config(object):
    
    # this is for multiple experiments
    
    def __init__(self,
                 market,
                 asset,
                 universe,
                 date_start,
                 date_end,
                 num_sections,
                 num_days_burnin,
                 list_targets,
                 list_exchange_latencies,
                 flags_path = "setup/flags.json",
                 banned_dates = [],
                 run_name = "white",
                 po_strategy = False,
                 list_po_config = ["optCfg.white_PO_test_{}"],
                 po_server_port_start = 1000,
                 po_client_port_start = 6000):
        
        self._mkt = market
        self._ast = asset
        self._univ = universe
        self._date_start = date_start
        self._date_end = date_end
        self._num_sections = num_sections
        self._num_days_burnin = num_days_burnin
        self._list_targets = list_targets
        self._list_exchange_latencies = list_exchange_latencies
        self._run_name = run_name
        self._po_strategy = po_strategy
        self._list_po_config = list_po_config
        self._po_server_port_start = po_server_port_start
        self._po_client_port_start = po_client_port_start
        
        self._dict_extra_flags = flags_generator(flags_path)
        
        with open("cache/experiment_map_{}.json".format(self._run_name), "w+") as _f:
            _f.write(json.dumps(self._dict_extra_flags, indent = 4))
            
        self._banned_dates = banned_dates

        os.makedirs("output/{}".format(self._run_name),
                    exist_ok = True)
        
    def create_config_files(self):
        
        _iter_num = 0
        for _tgt, _lat, _k, _pocfg in itertools.product(self._list_targets,
                                                        self._list_exchange_latencies,
                                                        self._dict_extra_flags.keys(),
                                                        self._list_po_config):
            _per_experiment_config = per_experiment_config(self._mkt,
                                                           self._ast,
                                                           self._univ,
                                                           self._date_start,
                                                           self._date_end,
                                                           self._num_sections,
                                                           self._num_days_burnin,
                                                           _tgt,
                                                           _lat,
                                                           self._dict_extra_flags[_k],
                                                           banned_dates = self._banned_dates,
                                                           experiment_name = _k,
                                                           run_name = self._run_name,
                                                           po_strategy = self._po_strategy,
                                                           po_config = _pocfg,
                                                           po_server_port_start = self._po_server_port_start + self._num_sections * _iter_num,
                                                           po_client_port_start = self._po_client_port_start + self._num_sections * _iter_num)
            
            _per_experiment_config.create_config_files()
            _iter_num += 1
        

class per_experiment_config(object):
    
    # this is for all sections with one set of params
    
    def __init__(self,
                 market,
                 asset,
                 universe,
                 date_start,
                 date_end,
                 num_sections,
                 num_days_burnin,
                 target,
                 exchange_latency,
                 extra_flags,
                 banned_dates = [],
                 experiment_name = "experiment00",
                 run_name = "white",
                 po_strategy = False,
                 po_config = "optCfg.white_PO_test_{}",
                 po_server_port_start = 1000,
                 po_client_port_start = 6000):
        
        self._mkt = market
        self._ast = asset
        self._univ = universe
        self._date_start = date_start
        self._date_end = date_end
        self._num_sections = num_sections
        self._num_days_burnin = num_days_burnin
        self._tgt = target
        self._exchange_latency = exchange_latency
        self._extra_flags = extra_flags
        self._banned_dates = banned_dates
        self._experiment_name = experiment_name
        self._run_name = run_name
        self._po_strategy = po_strategy
        self._po_config = po_config.format("tgt{}".format(self._tgt))
        self._po_server_port_start = po_server_port_start
        self._po_client_port_start = po_client_port_start
        
        _banned_text = ("_banned{}".format("".join([str(bd) for bd in self._banned_dates])) \
                        if len(self._banned_dates) > 0 else "")
        _cache_name = "{}_{}_{}_{}_{}_nsec{}_nburnin{}{}.json".format(self._mkt,
                                                                      self._ast,
                                                                      self._univ,
                                                                      self._date_start,
                                                                      self._date_end,
                                                                      self._num_sections,
                                                                      self._num_days_burnin,
                                                                      _banned_text)
        if _cache_name in os.listdir("cache"):
            with open("cache/{}".format(_cache_name)) as _f:
                self._date_sec_lists = json.load(_f)
        
        else:
            self._date_sec_lists = dates_securities_generator(self._mkt,
                                                              self._ast,
                                                              self._univ,
                                                              self._date_start,
                                                              self._date_end,
                                                              self._num_sections,
                                                              self._num_days_burnin,
                                                              banned_dates = self._banned_dates,
                                                              verbose = True)
            with open("cache/{}".format(_cache_name), "w+") as _f:
                _f.write(json.dumps(self._date_sec_lists, indent = 4))
        
    def create_config_files(self):
        
        _iter_num = 0
        for _k, _v in self._date_sec_lists.items():
            _date_list = _v[0]
            _sec_list = _v[1]
            _per_section_config = per_section_config(self._mkt,
                                                     self._ast,
                                                     self._univ,
                                                     _date_list,
                                                     _sec_list,
                                                     self._tgt,
                                                     exchange_latency = self._exchange_latency,
                                                     extra_flags = self._extra_flags,
                                                     run_name = self._run_name,
                                                     po_strategy = self._po_strategy,
                                                     po_config = self._po_config,
                                                     po_server_port = self._po_server_port_start + _iter_num,
                                                     po_client_port = self._po_client_port_start + _iter_num)
            
            if self._tgt < 10000:
                _tgt_text = "tgt{}".format(self._tgt)
            elif (self._tgt >= 10000) and (self._tgt < 100000000):
                _tgt_text = "tgt{}w".format(self._tgt // 10000)
            else:
                _tgt_text = "tgt{}yi".format(self._tgt // 100000000)
            
            if self._exchange_latency == 0:
                _lat_text = "nolat"
            elif (self._exchange_latency > 0) and (self._exchange_latency < 1000):
                _lat_text = "lat{}micros".format(self._exchange_latency)
            elif (self._exchange_latency >= 1000) and (self._exchange_latency < 1000000):
                _lat_text = "lat{}ms".format(self._exchange_latency // 1000)
            else:
                _lat_text = "lat{}s".format(self._exchange_latency // 1000000)
            
            _per_section_config.create_config("output/{}/{}_{}_{}_{}.json".format(self._run_name,
                                                                                  _tgt_text,
                                                                                  _lat_text,
                                                                                  self._experiment_name,
                                                                                  _k))
            _iter_num += 1

class per_section_config(object):
    
    def __init__(self,
                 market,
                 asset,
                 universe,
                 date_list,
                 sec_list,
                 target,
                 template_path = "config.template.hkg.{}.json",
                 account_id = 199099,
                 dai = "",
                 stock_group_count = 8,
                 exchange_latency = 20000,
                 extra_flags = [],
                 run_name = "white",
                 po_strategy = False,
                 po_config = "optCfg.white_PO_test",
                 po_server_port = 1000,
                 po_client_port = 6000):
        
        self._template_path = template_path.format("po" if po_strategy else "ls")
        
        self._account_id = account_id
        self._mkt = market
        self._ast = asset
        self._univ = universe
        # self._date_start = date_start
        # self._date_end = date_end
        self._tgt = target
        self._dai = dai
        
        self._stock_group_count = stock_group_count
        self._exchange_latency = exchange_latency
        
        #
        self._commission_buy = 0.00155
        self._commission_sell = 0.00155
        
        # ra = constructor_set_region_asset(self._mkt, self._ast)
        # self._date_list = ra.dates.get_trading_dates(self._date_start, self._date_end, fmt = "int")
        # self._sec_list = ra.univs.get_all_jkeys(self._univ, self._date_list[0], self._date_list[-1])
        self._date_list = date_list
        self._sec_list = sec_list
        
        #
        self._extra_flags = extra_flags
        self._run_name = run_name

        self._po_strategy = po_strategy
        self._po_config = po_config
        self._po_server_port = po_server_port
        self._po_client_port = po_client_port
        
    def create_config(self, output_path = "config.output.json"):
        
        with open("config/ceph.json") as _f:
            _ceph = json.load(_f)

        with open("config/logToCeph.json") as _f:
            _logToCeph = json.load(_f)
            _logToCeph["destination"]["pathFormat"] = _logToCeph["destination"]["pathFormat"]%(self._run_name,
                                                                                               output_path.split("/")[-1].split(".")[0])

        with open("config/feed_latency.json") as _f: # micros
            _feed_latency = json.load(_f)

        with open("config/feed_ceph.json") as _f:
            _feed_ceph = json.load(_f)

        with open("config/actor_ceph.json") as _f:
            _actor_ceph = json.load(_f)
        
        _batchMillisecond = 1000
        _groupNumber = self._stock_group_count

        _dates = [int(date) for date in self._date_list]
        _securities = [int(sec) for sec in self._sec_list]

        _latency = {
            "actorTypeLatency": [
                [0, 0, 0],
                [0, 0, 0],
                [0, self._exchange_latency, 0]
            ],
            "actorLocationLatency": [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
        }

        # need the target
        _po_flags = (["sd/white/poExecMode/1",
                      "sd/white/enableWhitePO/1",
                      "sd/white/syncPOResponse/1"] \
                     if self._po_strategy else [])
        _actor_flags = {
            "HkWhiteAlgoActor": [
                "sd/white/runningSimv2/1",
                "sd/white/targetLongMvUnsigned/{}".format(self._tgt),
                "sd/white/targetShortMvUnsigned/{}".format(self._tgt)
            ] + \
            _po_flags + \
            self._extra_flags
        }

        _commissionRateBuy = self._commission_buy
        _commissionRateSell = self._commission_sell

        # accountContext
        _accountId = int(self._account_id)
        _longAccountId = int(self._account_id % (1000 if self._account_id <= 999999 else 100000))
        _longBrokerId = int(self._account_id // (1000 if self._account_id <= 999999 else 100000))
        _cashFreeEquity = _marginFreeEquity = int(1.5 * self._tgt)
        _globalFreeEquity = _cashFreeEquity + _marginFreeEquity

        if self._dai:
            dai = pd.read_csv(self._dai)

            dai["intId"] = dai.secid
            dai["inv_L"] = dai.inv
            dai["inv_S"] = dai.invS

            fillers = ["longPositionCost",
                       "shortPositionCost",
                       "positionProfit",
                       "margin"]
            for col in fillers:
                dai[col] = 0.0

            result = dai[["intId", "inv_L", "inv_S"] + fillers].to_json(orient = "records")
            _inventory = [json.loads(result)]

        else:
            _inventory = []
        
        #
        with open(self._template_path) as _f:
            cfg = json.load(_f)

        # sim setup
        cfg["latency"] = _latency
        cfg["ceph"] = _ceph
        cfg["logToCeph"] = _logToCeph
        cfg["batchMillisecond"] = _batchMillisecond
        cfg["dates"] = _dates
        cfg["groupNumber"] = _groupNumber
        cfg["securities"] = _securities

        # source feeds
        for _feed_type in ["perSecurityFeeds", "universalFeeds"]:
            for _ifeed, _feed in enumerate(cfg["source"][_feed_type]):
                _class = _feed["class"]
                _feed["latencyMicros"] = _feed_latency[_class]
                _feed["init"]["cephLocation"] = _feed_ceph[_class]

                cfg["source"][_feed_type][_ifeed] = _feed

        
        # actors
        for _actor in cfg["actors"]["sharedActors"]:
            _class = _actor["class"]
            # po actor
            if "poactor" in _class.lower():
                _actor["init"]["poServerPort"] = self._po_server_port
                _actor["init"]["poClientPort"] = self._po_client_port
                _actor["init"]["poSimCode"] = self._po_config

            # algo actor
            elif "algoactor" in _class.lower():
                if self._po_strategy:
                    _actor["init"]["useProdPoSender"] = True
                    _actor["init"]["poServerPort"] = self._po_server_port
                    _actor["init"]["poClientPort"] = self._po_client_port

                _actor["init"]["commissionRateBuy"] = _commissionRateBuy
                _actor["init"]["commissionRateSell"] = _commissionRateSell
                _actor["init"]["source"] = _actor_ceph["HkWhiteAlgoActor"]
                _actor["init"]["flags"] = _actor_flags["HkWhiteAlgoActor"]
                _actor["init"]["accountContext"]["accountId"] = _accountId
                _actor["init"]["accountContext"]["longAccountId"] = _longAccountId
                _actor["init"]["accountContext"]["longBrokerId"] = _longBrokerId

                _actor["init"]["accountContext"]["cashFreeEquity"] = _cashFreeEquity
                _actor["init"]["accountContext"]["globalFreeEquity"] = _globalFreeEquity
                _actor["init"]["accountContext"]["marginFreeEquity"] = _marginFreeEquity

                _actor["state"]["inventory"] = _inventory


        #
        with open(output_path, "w+") as _o:
            _o.write(json.dumps(cfg, indent = 4))


if __name__ == "__main__":
    _po_strategy = False
    if _po_strategy:
        with open("config/banned_dates.json") as _f:
            _banned_dates = json.load(_f)
        test = multi_experiments_config("hkg",
                                        "eq",
                                        "HKGUniv.EqTOP500",
                                        20210101,
                                        20220930,
                                        11,
                                        10,
                                        [100000000],
                                        [0, 20000],
                                        banned_dates = _banned_dates["HKG"],
                                        run_name = "white_setup_test",
                                        po_strategy = _po_strategy,
                                        list_po_config = ["optCfg.white_PO_prod_{}"],
                                        po_server_port_start = 16000,
                                        po_client_port_start = 20000)

    else:
        with open("config/banned_dates.json") as _f:
            _banned_dates = json.load(_f)
        test = multi_experiments_config("hkg",
                                        "eq",
                                        "HKGUniv.EqTOP500",
                                        20210101,
                                        20220930,
                                        11,
                                        10,
                                        [50000000],
                                        [20000],
                                        banned_dates = _banned_dates["HKG"],
                                        run_name = "white_setup_test",
                                        po_strategy = _po_strategy)
    
    test.create_config_files()
