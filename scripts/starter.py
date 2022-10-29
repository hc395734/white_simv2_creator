import os, shutil

def starter(auto_start = False):

    '''
    For starting on hpc.
    '''
    shutil.copy("/tmp/simv2/hpcsim_release.sif", ".")
    _parent = os.getcwd()

    try:
        for _dir in os.listdir():
            if os.path.isdir(_dir):
                os.chdir(_dir)
                os.system("ln -s libwhite_algo_so.debug libwhite_algo.so")
                os.chdir(_parent)

        if auto_start:
            os.system("chmod +x run.sh")
            os.system("./run.sh hpcsim_release.sif")

        return True

    except Exception as _e:
        print(_e)
        return False

if __name__ == "__main__":
    print(starter(auto_start = False))
