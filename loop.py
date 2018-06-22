import subprocess
import time
while True:
    timestr = time.strftime("%Y%m%d")
    _file = "%s-FMOYT.log"%timestr
    f = open(_file, 'a')
    p = subprocess.Popen(['python', 'working.config.py'],
            stderr=subprocess.STDOUT,stdout=f).wait()
    if p!=0:
        continue
    else:
        break
