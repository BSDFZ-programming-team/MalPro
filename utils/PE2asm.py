import subprocess
import os
# your IDA path
IDA_PATH=r"D:\LargeFiles\PE\IDA\ida64.exe"
# your PE path
'''
It should be like:
PATH
|    malwarefamily1
|    malwarefamily2
|    malwarefamily3
'''
directory=r"D:\LargeFiles\PE\Downloads"
for malwarefamilies in os.listdir(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(malwarefamilies, directory, filename)
        subprocess.call([IDA_PATH, "-TPortable", "-Sanalysis.idc", filepath])

