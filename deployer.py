import os, shutil
from pathlib import Path

def deployer(po_strategy_map,
             parent_path = "simDriver/sim/HKG/experiments/{}",
             remote_home = "/home/hopec"):
    
    '''
    This is for deploying to local and remote folders (on HPC).
    '''
    
    try:
        for _run_name in os.listdir("output"):
            if _run_name not in po_strategy_map.keys():
                continue

            po_strategy = po_strategy_map[_run_name]
            _parent_path = os.path.join(os.getenv("HOME"), parent_path.format(_run_name))
            os.makedirs(_parent_path, exist_ok = True)

            for _file in os.listdir("output/{}".format(_run_name)):
                
                _subfolder = Path(_parent_path).joinpath(_file.split(".")[0])
                shutil.copytree("dynamics/{}".format("po" if po_strategy else "ls"),
                                _subfolder)
                shutil.copy("output/{}/{}".format(_run_name, _file),
                            _subfolder.joinpath("config.json"))
                
                # the command below is only needed to run locally
                # os.system("ln -s libwhite_algo_so.debug {}/libwhite_algo.so"\
                #           .format(_subfolder, _subfolder))
        
            # copy to remote
            _parent_path_remote = os.path.join(remote_home, "/".join(parent_path.format(_run_name).split("/")[:-1]))
            os.system("scp -r {} hopec@10.8.64.176:{}"\
                      .format(_parent_path, _parent_path_remote))
            os.system("scp cache/experiment_map_{}.json hopec@10.8.64.176:{}"\
                      .format(_run_name,
                              Path(_parent_path_remote).joinpath(parent_path.format(_run_name).split("/")[-1])))
            os.system("scp scripts/run.sh hopec@10.8.64.176:{}"\
                      .format(Path(_parent_path_remote).joinpath(parent_path.format(_run_name).split("/")[-1])))
            os.system("scp scripts/starter.py hopec@10.8.64.176:{}"\
                      .format(Path(_parent_path_remote).joinpath(parent_path.format(_run_name).split("/")[-1])))
            if po_strategy:
                os.system("scp dynamics/image/po_hkg.sif hopec@10.8.64.176:{}"\
                          .format(Path(_parent_path_remote).joinpath(parent_path.format(_run_name).split("/")[-1])))
            
        return True
        
    except Exception as _e:
        print(_e)
        return False
    
if __name__ == "__main__":
    po_strategy_map = {
        "white_setup_test": False
    }
    print(deployer(po_strategy_map))
