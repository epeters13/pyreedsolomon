# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Wed Jan 20 18:06:12 2021 (+1100)
#   Email            : edwin.g.w.petersatgmail.com
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Jan 29 19:55:30 2021 (+1100)
#           By       : Edwin G.W. Peters @ mugpahug-pc
# ------------------------------------------------------------------------------
# File Name          : bench.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : License GPL3
# ------------------------------------------------------------------------------
"""
Test the functions with different encoders data types

Compare to two common python libraries if they are installed.

"""

import sys
sys.path.append('..')
import numpy as np
import pyreedsolomon
import time

try:
    import reedsolo
    HAS_REEDSOLO = True
except:
    print(f"python library 'reedsolo' not found, skipping")
    HAS_REEDSOLO = False

try:
    import unireedsolomon
    HAS_UNIREEDSOLOMON = True
except:
    print(f"python library 'unireedsolomon' not found, skipping")
    HAS_UNIREEDSOLOMON = False

rs_params = []
rs_p = dict()
# # RS 973,935
rs_p['msg_len']    = 935
rs_p['par_len']    = 38
rs_p['total_len']  = rs_p['msg_len'] + rs_p['par_len']
rs_p['sym_size']   = 10
rs_p['pol']        = 0x409
rs_p['data_dtype'] = np.uint16 # for the generation of input data
rs_p['N_TESTS']    = 1000
rs_params.append(rs_p)

# RS 255
rs_p = dict()
rs_p['msg_len']    = 223
rs_p['par_len']    = 32
rs_p['total_len']  = rs_p['msg_len'] + rs_p['par_len']
rs_p['sym_size']   = 8
rs_p['pol']        = 0x11D
rs_p['data_dtype'] = np.uint8
rs_p['N_TESTS']    = 10000
rs_params.append(rs_p)

# RS 4
rs_p = dict()
rs_p['msg_len']    = 11
rs_p['par_len']    = 4
rs_p['total_len']  = rs_p['msg_len'] + rs_p['par_len']
rs_p['sym_size']   = 4
rs_p['pol']        = 0x13
rs_p['data_dtype'] = np.uint8
rs_p['N_TESTS']    = 100000
rs_params.append(rs_p)


padding_symbols = 0 # number of digits to zero pad up front (up to msg_len)

for rs_p in rs_params:
    msg_len = rs_p['msg_len']
    par_len = rs_p['par_len']
    total_len = rs_p['total_len']
    sym_size = rs_p['sym_size']
    pol = rs_p['pol']
    data_dtype = rs_p['data_dtype']
    N_TESTS = rs_p['N_TESTS']

    rs_dr = pyreedsolomon.Reed_Solomon(sym_size,msg_len,total_len,pol,0,1,par_len)

    test_names  = []
    encoding_times = []
    decoding_times = []

    dtypes = [np.ndarray, list,bytearray, bytes]


    print(f'RS ({total_len}, {msg_len}, {sym_size}) -- encoding and decoding {N_TESTS} runs\n')

    print('| test name | encoding | decoding | num errors|\n| :------- | -------: | ------: | :----: |')

    for dtype in dtypes:
        # bench:
        # np.random.seed(seed)
        if dtype == bytearray:
            data = [bytearray(np.random.randint(0,16,msg_len-padding_symbols).astype(data_dtype).tobytes()) for n in range(N_TESTS)]
        elif dtype == bytes:
            data = [np.random.randint(0,16,msg_len-padding_symbols).astype(data_dtype).tobytes() for n in range(N_TESTS)]
        elif dtype == list:
            data = [np.random.randint(0,16,msg_len-padding_symbols).astype(data_dtype).tolist() for n in range(N_TESTS)]
        elif dtype == np.ndarray:
            data = [np.random.randint(0,16,msg_len-padding_symbols).astype(data_dtype) for n in range(N_TESTS)]
        else:
            raise TypeError(f'data type {dtype} not supported')


        d_enc = N_TESTS * [None]
        d_dec = N_TESTS * [None]
        n_errors = np.zeros(N_TESTS)
        t_b1 = time.time()
        for i,d in enumerate(data):
            d_enc[i] = rs_dr.encode(d)
        t_e1 = time.time()

        # for i, d in enumerate(d_enc):
        #     d[3] = 5
        #     d[7] = 5

        t_b2 = time.time()
        for i,d in enumerate(d_enc):
            d_dec[i], n_errors[i] = rs_dr.decode(d)
        t_e2 = time.time()

        assert isinstance(d_dec[0],dtype), f'expected {dtype}, returned data is {type(d_dec[0])} instead'

        test_names.append(str(dtype)[8:-2])
        encoding_times.append((t_e1-t_b1)/N_TESTS*1000000)
        decoding_times.append((t_e2-t_b2)/N_TESTS*1000000)
        print(f'| pyreedsolomon {str(dtype)[8:-2]:15} | {t_e1-t_b1:.3f} s {(t_e1-t_b1)/N_TESTS*1000:.3f} ms each | {t_e2-t_b2:.3f} s {(t_e2-t_b2)/N_TESTS*1000:.3f} ms each | {np.sum(n_errors<0)} |')
        # print(f'dtype {str(dtype)[8:-2]:15} -- encoding time {t_e1-t_b1:.3f} s {(t_e1-t_b1)/N_TESTS*1000:.3f} ms each - decoding time {t_e2-t_b2:.3f} s {(t_e2-t_b2)/N_TESTS*1000:.3f} ms each - num_errors: {np.sum(n_errors<0)}')

    # np.random.seed(seed)
    data = [np.concatenate((np.zeros(padding_symbols),np.random.randint(0,16,total_len-padding_symbols))).astype(data_dtype) for n in range(N_TESTS)]

    d_enc2 = N_TESTS * [None]
    d_dec2 = N_TESTS * [None]
    n_errors2 = np.zeros(N_TESTS)
    t_b1 = time.time()
    for i,d in enumerate(data):
        d_enc2[i] = rs_dr.encode_fast(d)
    t_e1 = time.time()

    # for i, d in enumerate(d_enc):
    #     d[3] = 5
    #     d[7] = 5

    t_b2 = time.time()
    for i,d in enumerate(d_enc2):
        d_dec2[i], n_errors2[i] = rs_dr.decode_fast(d)
    t_e2 = time.time()

    test_names.append('fast')
    encoding_times.append((t_e1-t_b1)/N_TESTS*1000000)
    decoding_times.append((t_e2-t_b2)/N_TESTS*1000000)

    print(f'| {"pyreedsolomon fast":29} | {t_e1-t_b1:.3f} s {(t_e1-t_b1)/N_TESTS*1000:.3f} ms each | {t_e2-t_b2:.3f} s {(t_e2-t_b2)/N_TESTS*1000:.3f} ms each | {np.sum(n_errors2<0)} |')
    # print(f'{"fast":21} -- encoding time {t_e1-t_b1:.3f} s {(t_e1-t_b1)/N_TESTS*1000:.3f} ms each - decoding time {t_e2-t_b2:.3f} s {(t_e2-t_b2)/N_TESTS*1000:.3f} ms each - num_errors: {np.sum(n_errors2<0)}')



    if HAS_UNIREEDSOLOMON:

        rs_dr_u = unireedsolomon.rs.RSCoder(total_len,msg_len,generator=2,prim=pol,c_exp=sym_size,fcr=0) 
        def rs_enc(data_symbols):
            if sym_size <= 8:
                return np.array([ord(c) for c in rs_dr_u.encode_fast(data_symbols)][-len(data_symbols)-par_len:])
            else:
                return np.array([np.uint16(c) for c in rs_dr_u.encode_fast(data_symbols)][-len(data_symbols)-par_len:])

        def rs_dec(data,erasures_loc = []):
            dec_data_str,crc = rs_dr_u.decode_fast(data,nostrip=True,erasures_pos=erasures_loc) # do not strip leading zeros
            if sym_size <= 8:
                dec_dat = np.concatenate((np.array([ord(c) for c in dec_data_str],dtype=np.uint8), np.array([ord(c) for c in crc],dtype=np.uint8)))
            else:
                dec_dat = np.concatenate((np.array([np.uint16(c) for c in dec_data_str],dtype=np.uint16), np.array([np.uint8(c) for c in crc],dtype=np.uint16)))

            return dec_dat, 0

        d_enc_py = N_TESTS * [None]
        d_dec_py = N_TESTS * [None]
        n_errors_py = np.zeros(N_TESTS)
        t_pb1 = time.time()
        for i,d in enumerate(data):
            d_enc_py[i] = rs_enc(d[:msg_len])

        t_pe1 = time.time()
        t_pb2 = time.time()
        for i,d in enumerate(d_enc_py):
            d_dec_py[i], n_errors_py[i] = rs_dec(d)
        t_pe2 = time.time()

        test_names.append('py unireedsolomon')
        encoding_times.append((t_pe1-t_pb1)/N_TESTS*1000000)
        decoding_times.append((t_pe2-t_pb2)/N_TESTS*1000000)

        print(f'| {"py unireedsolomon":29} | {t_pe1-t_pb1:.3f} s {(t_pe1-t_pb1)/N_TESTS*1000:.3f} ms each | {t_pe2-t_pb2:.3f} s {(t_pe2-t_pb2)/N_TESTS*1000:.3f} ms each | {np.sum(n_errors_py<0)} |')

        # print(f'{"py unireedsolomon":21} -- encoding time {t_pe1-t_pb1:.3f} s {(t_pe1-t_pb1)/N_TESTS*1000:.3f} ms each - decoding time {t_pe2-t_pe1:.3f} s {(t_pe2-t_pe1)/N_TESTS*1000:.3f} ms each - num_errors: {np.sum(n_errors_py!=0)}')

    ## reedsolo
    if HAS_REEDSOLO and  sym_size <= 8: # only works for symbol sizes up to 8

        rs_dr_rs = reedsolo.RSCodec(par_len,total_len,prim=pol,c_exp=sym_size,fcr=0,generator=2) # n

        def rs_enc_rs(data):
            return np.frombuffer(rs_dr_rs.encode(data.astype(np.uint8)),dtype=data_dtype)

        def rs_dec_rs(data):
            return np.frombuffer(rs_dr_rs.decode(data)[0],dtype=data_dtype)


        d_enc_py = N_TESTS * [None]
        d_dec_py = N_TESTS * [None]
        n_errors_py = np.zeros(N_TESTS)
        t_pb1 = time.time()
        for i,d in enumerate(data):
            d_enc_py[i] = rs_enc_rs(d[:msg_len])

        t_pe1 = time.time()
        t_pb2 = time.time()
        for i,d in enumerate(d_enc_py):
            d_dec_py[i] = rs_dec_rs(d)
        t_pe2 = time.time()

        test_names.append('py reedsolo')
        encoding_times.append((t_pe1-t_pb1)/N_TESTS*1000000)
        decoding_times.append((t_pe2-t_pb2)/N_TESTS*1000000)


        print(f'| {"py reedsolo":29} | {t_pe1-t_pb1:.3f} s {(t_pe1-t_pb1)/N_TESTS*1000:.3f} ms each | {t_pe2-t_pb2:.3f} s {(t_pe2-t_pb2)/N_TESTS*1000:.3f} ms each | {np.sum(n_errors_py<0)} |')
        # print(f'{"py reedsolo":21} -- encoding time {t_pe1-t_pb1:.3f} s {(t_pe1-t_pb1)/N_TESTS*1000:.3f} ms each - decoding time {t_pe2-t_pe1:.3f} s {(t_pe2-t_pe1)/N_TESTS*1000:.3f} ms each - num_errors: {np.sum(n_errors_py!=0)}')







    ### plot results

    try:
        import matplotlib.pyplot as plt

        x = np.arange(len(test_names))  # the label locations
        width = 0.35  # the width of the bars
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, encoding_times, width, label='encoding')
        rects2 = ax.bar(x + width/2, decoding_times, width, label='decoding')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('time [us]')
        ax.set_title(f'RS ({total_len}, {msg_len}, {sym_size}) -- average times over {N_TESTS} runs')
        ax.set_xticks(x)
        plt.xticks(rotation=45)
        ax.set_xticklabels(test_names)
        ax.legend()


        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{:.2f}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            rotation=45)


        autolabel(rects1)
        autolabel(rects2)

        fig.tight_layout()

        plt.savefig(f'rs{total_len}_{msg_len}_{sym_size}.png')

    except:
        pass

try:
    plt.show()
except:
    print(f'No graphs generated since matplotlib could not be imported')





