import subprocess
import glob
import errno
import os

data = {}
path = 'test/regalloc/*.out'
files = glob.glob(path)
N = 10

for i in range(N):
    MyOut = subprocess.Popen(['make', 'save'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()
    if stderr:
        print(stderr)

    for name in files:
        try:
            with open(name) as f:
                filename, fileext = os.path.splitext(os.path.basename(name))
                for line in f.readlines():
                    if '#load' in line:
                        loadrd = [int(i) for i in line.split() if i.isdigit()]
                        try:
                            loads = loadrd[0] + data[filename]['loads']
                            data[filename]['loads'] = loads
                        except KeyError:    
                            loads = loadrd[0]
                            data[filename] = {'loads': loads}
                    #if '#store' in line:
                    #    storerd = [int(i) for i in line.split() if i.isdigit()]
                    #    try:
                    #        stores = storerd[0] + data[filename]['stores']
                    #        data[filename]['stores'] = stores
                    #    except KeyError:    
                    #        stores = storerd[0]
                    #        data[filename] = {'stores': stores}

        except IOError as exc:
            if exc.errno != errno.EISDIR:
                raise

for name in files:
    try:
        with open(name) as f:
            filename, fileext = os.path.splitext(os.path.basename(name))
            load_count = data[filename]['loads']/N
            print("{} - {}".format(filename,load_count));
            #store_count = data[filename]['stores']/N
            #print("{} - {}".format(filename,store_count));
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise
