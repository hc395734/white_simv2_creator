# white_simv2_creator
The repo is currently only compatible with refactored HKG LS and HKG PO simulations.  The DFS and HPC confidentials are still Hope's.  This will be modified soon.

To use it, first modify `setup/flags.json`, fill in the rest of the setup parameters in `main.py` and run it.
```python
python main.py
```
This will create all the config json files in `output`.

`deploy.py` contains code to copy the files to the HPC via `scp`.

The `dynamics` is for storing so and image files (that are not on the HPC).
```
dynamics
├── image
│   └── po_hkg.sif
├── ls
│   ├── dfs_config
│   ├── keys
│   │   ├── fn_log_priv_key
│   │   ├── sim_fn_log.key
│   │   ├── sim_order_log.key
│   │   ├── strategy_action_priv_key
│   │   └── white_algo_log_priv_key
│   ├── libceph-client.so
│   ├── libceph-common.so.2
│   ├── librados.so.2
│   ├── libradosstriper.so.1
│   ├── libwhite_algo_actor.so
│   ├── libwhite_algo.so.debug
│   ├── libwhite_simv2_me.so
│   ├── loggerKeys.json
│   └── Logs
└── po
    ├── dfs_config
    ├── keys
    │   ├── fn_log_priv_key
    │   ├── sim_fn_log.key
    │   ├── sim_order_log.key
    │   ├── strategy_action_priv_key
    │   └── white_algo_log_priv_key
    ├── libceph-client.so
    ├── libparquet_parser.so
    ├── libunwind.so
    ├── libunwind.so.8
    ├── libwhite_algo_actor.so
    ├── libwhite_algo.so.debug
    ├── libwhite_simv2_me.so
    ├── libwhite_simv2_po.so
    ├── loggerKeys.json
    ├── Logs
    └── po_server
```
