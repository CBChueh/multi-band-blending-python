
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Multi-Band-blending/FileListOpe'))

import FileListOpe as FLO
filename=''
line=0
frame=0
Enface_part = np.fromfile(filename,dtype='f4',count=line*frame).reshape([line,frame], order='C')
