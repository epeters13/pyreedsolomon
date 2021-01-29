# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Wed Jan 20 17:15:53 2021 (+1100)
#   Email            : edwin.g.w.petersatgmail.com
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Jan 29 16:23:34 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : pyreedsolomon.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : License GPL3
# ------------------------------------------------------------------------------
"""
Uses the C-library https://github.com/tierney/reed-solomon

Enable 
AC_DEFINE(CONFIG_REED_SOLOMON_ENC16, 1, Reed Solomon encoding word length)
AC_DEFINE(CONFIG_REED_SOLOMON_DEC16, 1, Reed Solomon decoding word length)
in configure.ac

configure with prefix=/usr/lib or add default prefix to LD_LIBRARY_PATH
"""

import ctypes
import numpy as np

lib = ctypes.cdll.LoadLibrary('librs.so')

# pointers
c_dat_p8 =  ctypes.POINTER(ctypes.c_ubyte)
c_dat_p16 =  ctypes.POINTER(ctypes.c_ushort)
c_par_p = ctypes.POINTER(ctypes.c_ushort)


lib.init_rs.argtypes = [ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int]
lib.init_rs.restype = ctypes.c_void_p

lib.encode_rs8.argtypes = [ctypes.c_void_p,
                           c_dat_p8,
                           ctypes.c_int,
                           c_par_p,
                           ctypes.c_ushort]


lib.decode_rs8.argtypes = [ctypes.c_void_p,
                           c_dat_p8,
                           c_par_p,
                           ctypes.c_int,
                           c_par_p,
                           ctypes.c_int,
                           ctypes.POINTER(ctypes.c_int),
                           ctypes.c_ushort,
                           c_par_p,
]

lib.decode_rs8.restype = ctypes.c_int

lib.encode_rs16.argtypes = [ctypes.c_void_p,
                           c_dat_p16,
                           ctypes.c_int,
                           c_par_p,
                           ctypes.c_ushort]

lib.decode_rs16.argtypes = [ctypes.c_void_p,
                           c_dat_p16,
                           c_par_p,
                           ctypes.c_int,
                           c_par_p,
                           ctypes.c_int,
                           ctypes.POINTER(ctypes.c_int),
                           ctypes.c_ushort,
                           c_par_p,
]

lib.decode_rs16.restype = ctypes.c_int

lib.free.argtypes = [ctypes.c_void_p]


class Reed_Solomon(object):
    def __init__(self,symsize,message_size,total_size,gfpoly,fcr,prim,nroots):
        """
        symsize - bits pr symbol
        message_size - size of the data
        total_size - size of data + parity
        
        * init_rs - Find a matching or allocate a new rs control structure
        *  @symsize:	the symbol size (number of bits)
        *  @gfpoly:	the extended Galois field generator polynomial coefficients,
        *		with the 0th coefficient in the low order bit. The polynomial
        *		must be primitive;
        *  @fcr:  	the first consecutive root of the rs code generator polynomial
        *		in index form
        *  @prim:	primitive element to generate polynomial roots
        *  @nroots:	RS code generator polynomial degree (number of roots)


        """
        self.symsize = symsize
        self.message_size = message_size
        self.total_size = total_size
        self.par_size = total_size - message_size
        self.obj = lib.init_rs(symsize,gfpoly,fcr,prim,nroots)

        self.par = np.zeros(self.par_size,dtype=np.uint16)
        self.par_p = self.par.ctypes.data_as(c_par_p)


        if symsize > 8:
            self._encode = lib.encode_rs16
            self._decode = lib.decode_rs16
            self.c_dat_p = c_dat_p16
            self.dtype = np.uint16
        else:
            self._encode = lib.encode_rs8
            self._decode = lib.decode_rs8
            self.c_dat_p = c_dat_p8
            self.dtype = np.uint8

            
        self.data_buf = np.empty(self.total_size,dtype=self.dtype)

    def encode_fast(self,dat):
        """
        Fast encoding algorithm
        
        The length of the data array provided should be total_size, such that the data
        and CRC is stored here. 
        dat should be a numpy array with dtype=numpy.uint8

        Returns the data with the checksum appended
        """

        self.par[:] = 0 # needs to be set to zeros
        dat_p = dat.ctypes.data_as(self.c_dat_p)
        
        # lib.encode_rs8(self.obj,dat_p,self.message_size,self.par_p,0)
        self._encode(self.obj,dat_p,self.message_size,self.par_p,0)

        dat[-self.par_size:] = self.par.astype(self.dtype)
        return dat
        # return np.append(dat,self.par.astype(np.uint8))

    def decode_fast(self,dat):
        """
        Input the data array with parity. The length of the data array should be total_size

        returns the decoded data and number of symbol errors or -EBADMSH (-74) if the CRC failed
        """

        self.par[:] = dat[-self.par_size:].astype(np.uint16)

        dat_p = dat.ctypes.data_as(self.c_dat_p)

        # n_errors = lib.decode_rs8(self.obj,dat_p,self.par_p, self.message_size, None,0,None,0,None)
        n_errors = self._decode(self.obj,dat_p,self.par_p, self.message_size, None,0,None,0,None)
        # if n_errors == -74: # -EBADMSG
        #     return dat, n_errors
        
        return dat, n_errors


    def encode(self,dat):
        """
        Encode the provided data
        
        input:
        \tdat -- array with the data in numpy array, bytearray or list
        
        returns:
        \tdat+crc -- data with crc appended in the data type provided

        Supports numpy array, list, bytes and bytearray

        If more encoding performance is required, please use encode_fast
        """

        d_type = type(dat)
        n_symbols = len(dat)
        # do the appropriate mapping based on input data type

        if d_type == np.ndarray:
            if n_symbols > self.message_size:
                raise ValueError(f'input data size {n_symbols} larger than max allowed {self.message_size}')
            self.data_buf[self.message_size-n_symbols:self.message_size] = dat.astype(self.dtype)
        elif d_type == list:
            if n_symbols > self.message_size:
                raise ValueError(f'input data size {n_symbols} larger than max allowed {self.message_size}')

            self.data_buf[self.message_size-n_symbols:self.message_size] = np.array(dat,dtype=self.dtype)
        elif d_type in [bytes, bytearray]:
            if self.symsize > 8:
                n_symbols = n_symbols//2
            if n_symbols > self.message_size:
                raise ValueError(f'input data size {n_symbols//2} larger than max allowed {self.message_size}')

            self.data_buf[self.message_size-n_symbols:self.message_size] = np.frombuffer(dat,dtype=self.dtype)

        self.data_buf[:self.message_size-n_symbols] = 0 # prepend with zeros when the input data is not message_size
        

        self.encode_fast(self.data_buf)

        if d_type == np.ndarray:
            return self.data_buf
        elif d_type == bytes:
            return self.data_buf.tobytes()
        elif d_type == bytearray:
            return bytearray(self.data_buf.tobytes())
        elif d_type == list:
            return self.data_buf.tolist()


    def decode(self,dat):
        """
        decode the provided data
        
        input:
        \tdat -- array with the data and CRC in numpy array, bytearray or list
        
        returns:
        \tdat -- decoded data or original data in case decoding failed
        \tnum_errors -- the number of errors or -EBADMSH (-74) if failed

        Supports numpy array, list, bytes and bytearray

        If more encoding performance is required, please use decode_fast
        """

        d_type = type(dat)
        n_symbols = len(dat)
        # do the appropriate mapping based on input data type

        if d_type == np.ndarray:
            if n_symbols > self.total_size:
                raise ValueError(f'input data size {n_symbols} larger than max allowed {self.message_size}')
            self.data_buf[-n_symbols:] = dat.astype(self.dtype)            
        elif d_type == list:
            if n_symbols > self.total_size:
                raise ValueError(f'input data size {n_symbols} larger than max allowed {self.message_size}')
            self.data_buf[-n_symbols:] = np.array(dat,dtype=self.dtype)
        elif d_type in [bytes, bytearray]:  
            if self.symsize > 8:
                n_symbols = n_symbols//2

            if n_symbols > self.total_size:
                raise ValueError(f'input data size {n_symbols} larger than max allowed {self.message_size}')

            self.data_buf[-n_symbols:] = np.frombuffer(dat,dtype=self.dtype)

        self.data_buf[:self.total_size-n_symbols] = 0 # prepend with zeros when the input data is not message_size


        self.data_buf, n_errors = self.decode_fast(self.data_buf)

        if d_type == np.ndarray:
            return self.data_buf[:self.message_size], n_errors
        elif d_type == bytes:
            return self.data_buf[:self.message_size].tobytes(), n_errors
        elif d_type == bytearray:
            return bytearray(self.data_buf[:self.message_size].tobytes()) , n_errors
        elif d_type == list:
            return self.data_buf[:self.message_size].tolist(), n_errors
