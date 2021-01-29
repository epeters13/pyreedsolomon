# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Fri Jan 29 15:28:36 2021 (+1100)
#   Email            : edwin.g.w.petersatgmail.com
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Jan 29 16:22:05 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : demo.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : License GPL3
# ------------------------------------------------------------------------------

import sys
sys.path.append('../')
import pyreedsolomon
import numpy as np

rs_dr = pyreedsolomon.Reed_Solomon(8,223,255,0x11D,0,1,32)

data = np.random.randint(0,256,150).astype(np.uint8)

data_enc = rs_dr.encode(data)

# create a few errors
err_idx = [23,53,12,97,102, 200, 250]


data_enc[err_idx] = 255

data_dec, n_errors = rs_dr.decode(data_enc)

verify = np.all(data_dec[-len(data):]==data)

print(f"Decoding succes: {verify}. errors corrected {n_errors}")



