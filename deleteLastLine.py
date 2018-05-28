output_dir_30 = "C:/KeLiQuant/30_min_data/"
output_dir_60 = "C:/KeLiQuant/60_min_data/"
output_dir_30 = "C:/KeLiQuant/test/"

import os
from pathlib import Path
#add header to new file
filename = output_dir_30 + '00000'
if not Path(filename).is_file():
    header = 'date,close'
    fd = open(filename, 'a')
    fd.write(header)
    fd.write('\n')
    fd.close()
    fd = open(filename, 'a')
    fd.write('aaaaaa,bbbbbb')
    fd.write('\n')
    fd.close()
    # print ('yes')
exit(0)
#delete last line
for root, dirs, files in os.walk(output_dir_60):
    for file in files:
        print (file)
        readFile = open(output_dir_60 + file)
        lines = readFile.readlines()
        readFile.close()
        w = open(output_dir_60 + file, 'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
