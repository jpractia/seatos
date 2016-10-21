#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
from scipy.io.netcdf import netcdf_file
import numpy as np
from datetime import datetime, timedelta
from h5py import File as h5
import os, sys, h5py, argparse
#--- shared libs
from shared.ShiftTimes import ShiftCorrection, ShiftDts
import shared.console_colors as ccl
from shared.shared_funcs import nans, My2DArray


def calc_beta(Temp, Pcc, B):
    """
    Agarramos la definicion de OMNI, de:
     http://omniweb.gsfc.nasa.gov/ftpbrowser/magnetopause/Reference.html
     http://pamela.roma2.infn.it/index.php
    Beta = [(4.16*10**-5 * Tp) + 5.34] * Np/B**2 (B in nT)
    """
    beta = ((4.16*10**-5 * Temp) + 5.34) * Pcc/B**2
    return beta

def dates_from_omni(t):
    time = []
    n = len(t)
    for i in range(n):
        yyyy = t[i][0]
        mm = t[i][1]
        dd = t[i][2]
        HH = t[i][3]
        MM = t[i][4]
        SS = t[i][5]
        uSS = t[i][6]
        time += [datetime(yyyy, mm, dd, HH, MM, SS, uSS)]

    return time

def date_to_utc(fecha):
    utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    sec_utc = (fecha - utc).total_seconds()
    return sec_utc

def utc_from_omni(file):
    t = np.array(file.variables['time'].data)
    dates = dates_from_omni(t)
    n = len(dates)
    time = np.zeros(n)
    for i in range(n):
        time[i] = date_to_utc(dates[i])

    return time

def read_hsts_data(fname, typic, ch_Eds):
    """
    code adapted from ...ch_Eds_smoo2.py
    """
    f   = h5(fname, 'r')

    # initial date
    datestr = f['date_ini'].value
    yyyy, mm, dd = map(int, datestr.split('-'))
    INI_DATE = datetime(yyyy, mm, dd)

    # final date
    datestr = f['date_end'].value
    yyyy, mm, dd = map(int, datestr.split('-'))
    END_DATE = datetime(yyyy, mm, dd)

    date = INI_DATE
    tt, rr = [], []
    ntot, nt = 0, 0
    while date < END_DATE:
        yyyy, mm, dd = date.year, date.month, date.day
        path    = '%04d/%02d/%02d' % (yyyy, mm, dd)
        try:
            dummy = f[path] # test if this exists!
        except:
            date    += timedelta(days=1)    # next day...
            continue

        ntanks  = f['%s/tanks'%path][...]
        cc  = ntanks>150.
        ncc = cc.nonzero()[0].size

        if ncc>1: #mas de un dato tiene >150 tanques
            time    = f['%s/t_utc'%path][...] # utc secs
            cts, typ = np.zeros(96, dtype=np.float64), 0.0
            for i in ch_Eds:
                Ed  =  i*20.+10.
                cts += f['%s/cts_temp-corr_%04dMeV'%(path,Ed)][...]
                typ += typic[i] # escalar

            cts_norm = cts/typ
            #aux  = np.nanmean(cts_norm[cc])
            tt += [ time[cc] ]
            rr += [ cts_norm[cc] ]
            ntot += 1 # files read ok
            nt += ncc # total nmbr ok elements

        date    += timedelta(days=1)        # next day...

    #--- converting tt, rr to 1D-numpy.arrays
    t, r = nans(nt), nans(nt)
    ini, end = 0, 0
    for i in range(ntot):
        ni = len(tt[i])
        t[ini:ini+ni] = tt[i]
        r[ini:ini+ni] = rr[i]
        ini += ni

    f.close()
    return t, r

class _read_auger_scals(object):
    """
    reads different versions of corrected-scalers
    """
    def __init__(self, fname_inp, data_name):
        self.fname_inp  = fname_inp
        self.data_name  = data_name

    def read(self):
        with h5py.File(self.fname_inp,'r') as f:
            if 'auger' in f.keys():
                return self.read_i()
            elif 't_utc' in f.keys():
                return self.read_ii()
            else:
                raise SystemExit('\
                 ---> no reader setup for this version scaler file!\
                ')

    def read_i(self):
        """
        read first version of processed 
        corrected-scalers.
        """
        f5  = h5py.File(self.fname_inp, 'r')
        t_utc = f5['auger/time_seg_utc'][...].copy() #data_murdo[:,0]
        CRs   = f5['auger/sc_wAoP_wPres'][...].copy() #data_murdo[:,1]
        print " -------> variables leidas!"

        VARS = {
            'CRs.'+self.data_name : {
                'value' : CRs,
                'lims'  : [-1.0, 1.0],
                'label' : 'Auger Scaler rate [%]',
                },
        }
        return t_utc, VARS

    def _pair_yyyymm(self, f, kname):
        years = map(int, f[kname].keys())
        ly, lm = [], []
        for year in years:
            months = map(int, f[kname+'/%04d'%year].keys())
            nm     = len(months)
            ly     += [year]*nm
            lm     += months
        return zip(ly,lm)

    def read_ii(self):
        """
        read 2nd version of processed correctd-scalers.
        We do NOT read the geop-height-corrected scalers, because
        seems unphysical (i.e. geop height is not a parameter
        for scalers correction!). So just use pressure-corrected ones.
        """
        f = h5py.File(self.fname_inp,'r')
        years_and_months = self._pair_yyyymm(f, 't_utc')
        t_utc = My2DArray((3,), dtype=np.float32)
        CRs   = My2DArray((3,), dtype=np.float32)
        n = 0
        for yyyy, mm in years_and_months:
            nt = f['t_utc/%04d/%02d'%(yyyy,mm)].size
            t_utc[n:n+nt] = f['t_utc/%04d/%02d'%(yyyy,mm)][...]
            CRs[n:n+nt]   = f['wAoP_wPrs/%04d/%02d'%(yyyy,mm)][...]
            n             += nt

        print " --> Auger scalers leidos!"
        VARS = {
            'CRs.'+self.data_name : {
                'value' : CRs[:n],
                'lims'  : [-1.0, 1.0],
                'label' : 'Auger Scaler rate [%]',
                },
        }
        return t_utc[:n], VARS



#------- data parsers -------
class _data_ACE(object):
    """
    to read the .nc file of ACE data, built from ASCII versions
    """
    def __init__(self, fname_inp, tshift=False):
        """
        if tshift==True, we return shifted versions of
        the `tb` and `bd` in load() method.
        """
        self.fname_inp = fname_inp
        self.tshift    = tshift

    def load(self, data_name, **kws):
        f_sc   = netcdf_file(self.fname_inp, 'r')
        print " leyendo tiempo..."
        t_utc   = utc_from_omni(f_sc)
        print " Ready."

        tb = kws['tb']  # datetimes of borders of all structures
        bd = kws['bd']  # borders of the structures we will use

        #++++++++++ CORRECTION OF BORDERS ++++++++++
        # IMPORTANTE:
        # Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
        # NOTA: dan saltos de shock mas marcados con True.
        # TODO: make a copy/deepcopy of `tb` and `bd`, so that we don't 
        # bother the rest of data_names (i.e. Auger_scals, Auger_BandMuons, 
        # etc.)
        if self.tshift:
            ShiftCorrection(ShiftDts, tb.tshck)
            ShiftCorrection(ShiftDts, tb.tini_icme)
            ShiftCorrection(ShiftDts, tb.tend_icme)
            ShiftCorrection(ShiftDts, tb.tini_mc)
            ShiftCorrection(ShiftDts, tb.tend_mc)
            ShiftCorrection(ShiftDts, bd.tini)
            ShiftCorrection(ShiftDts, bd.tend)

        #+++++++++++++++++++++++++++++++++++++++++++
        B       = f_sc.variables['Bmag'].data.copy()
        Vsw     = f_sc.variables['Vp'].data.copy()
        Temp    = f_sc.variables['Tp'].data.copy()
        Pcc     = f_sc.variables['Np'].data.copy()
        rmsB    = f_sc.variables['dBrms'].data.copy()
        alphar  = f_sc.variables['Alpha_ratio'].data.copy()
        beta    = calc_beta(Temp, Pcc, B)
        rmsBoB  = rmsB/B
        print " -------> variables leidas!"

        #------------------------------------ VARIABLES
        VARS = {}
        # variable, nombre archivo, limite vertical, ylabel
        VARS['B.'+data_name] = {
            'value' : B,
            'lims'  : [5., 18.],
            'label' : 'B [nT]'
        }
        VARS['V.'+data_name] = {
            'value' : Vsw,
            'lims'  : [300., 650.],
            'label' : 'Vsw [km/s]'
        }
        VARS['rmsBoB.'+data_name] = {
            'value' : rmsBoB,
            'lims'  : [0.01, 0.2],
            'label' : 'rms($\hat B$/|B|) [1]'
        }
        VARS['rmsB.'+data_name] = {
            'value' : rmsB,
            'lims'  : [0.05, 2.0],
            'label' : 'rms($\hat B$) [nT]'
        }
        VARS['beta.'+data_name] = {
            'value' : beta,
            'lims'  : [0.001, 5.],
            'label' : '$\\beta$ [1]'
        }
        VARS['Pcc.'+data_name] = {
            'value' : Pcc,
            'lims'  : [2, 17.],
            'label' : 'proton density [#/cc]'
        }
        VARS['Temp.'+data_name] = {
            'value' : Temp,
            'lims'  : [1e4, 4e5],
            'label' : 'Temp [K]'
        }
        VARS['AlphaRatio.'+data_name] = {
            'value' : alphar,
            'lims'  : [1e-3, 0.1],
            'label' : 'alpha ratio [1]'
        }

        #self.nvars = len(VARS.keys())
        #---------
        #self.aux = aux = {}
        #aux['SELECC']    = self.SELECC

        """
        NOTE: `bd` and `tb` have been shifted if
        `selg.tshift`==True.
        """
        return {
        't_utc' : t_utc,
        'VARS'  : VARS,
        }


class _data_Auger_BandMuons(object):
    """
    for muon band of Auger charge histograms
    """
    def __init__(self, fname_inp, tshift=False):
        self.fname_inp  = fname_inp
        self.tshift     = tshift


    def load(self, data_name):
        """
        para leer la data de histogramas Auger
        """
        f5          = h5(self.fname_inp, 'r')
        ch_Eds      = (10, 11, 12, 13)
        # get the global-average histogram
        nEd   = 50
        typic = np.zeros(nEd, dtype=np.float32)
        for i in range(nEd):
            Ed = i*20.+10.
            typic[i] = f5['mean/corr_%04dMeV'%Ed].value

        t_utc, CRs = read_hsts_data(self.fname_inp,  typic, ch_Eds)
        print " -------> variables leidas!"

        VARS = {} #[]
        VARS['CRs.'+data_name] = {
            'value' : CRs,
            'lims'  : [-1.0, 1.0],
            'label' : 'Auger (muon band) [%]'
        }

        return {
        't_utc'  : t_utc,
        'VARS'   : VARS,
        }


class _data_Auger_BandScals(object):
    """
    for muon band of Auger charge histograms
    """
    def __init__(self, fname_inp, tshift=False):
        self.fname_inp  = fname_inp
        self.tshift     = tshift


    def load(self, data_name):
        """
        para leer la data de histogramas Auger
        """
        f5          = h5(self.fname_inp, 'r')
        ch_Eds      = (3, 4, 5)
        # get the global-average histogram
        nEd   = 50
        typic = np.zeros(nEd, dtype=np.float32)
        for i in range(nEd):
            Ed = i*20.+10.
            typic[i] = f5['mean/corr_%04dMeV'%Ed].value

        t_utc, CRs = read_hsts_data(self.fname_inp,  typic, ch_Eds)
        print " -------> variables leidas!"

        VARS = {} #[]
        VARS['CRs.'+data_name] = {
            'value' : CRs,
            'lims'  : [-1.0, 1.0],
            'label' : 'Auger (muon band) [%]'
        }

        return {
        't_utc'  : t_utc,
        'VARS'   : VARS,
        }


class _data_ACE_o7o6(object):
    def __init__(self, fname_inp, tshift=False):
        self.fname_inp  = fname_inp
        self.tshift     = tshift

    def load(self, data_name, **kws):
        tb          = self.tb
        nBin        = self.nBin
        bd          = self.bd
        day         = 86400.
        self.f_sc   = netcdf_file(self.fname_inp, 'r')
        print " leyendo tiempo..."
        t_utc   = utc_from_omni(self.f_sc)
        print " Ready."

        #++++++++++++++++++++ CORRECCION DE BORDES +++++++++++++++++++++++++++
        # IMPORTANTE:
        # El shift es necesario, pero ya lo hice en la corrida del
        # primer 'self.data_name' (i.e. `_data_ACE()`). Si lo hago aqui, 
        # estaria haciendo doble shift.
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        o7o6    = self.f_sc.variables['O7toO6'].data.copy()
        print " -------> variables leidas!"
        #------------------------------------ VARIABLES
        self.t_utc  = t_utc
        self.VARS = VARS = {}
        # variable, nombre archivo, limite vertical, ylabel
        VARS['o7o6'] = {
            'value' : o7o6,
            'lims'  : [0.0, 1.5],
            'label' : 'O7/O6 [1]'
        }
        return {
        't_utc'  : t_utc,
        'VARS'   : VARS,
        }


class _data_Auger_scals(object):
    def __init__(self, fname_inp):
        self.fname_inp  = fname_inp

    def load(self, data_name):
        """
        solo cargamos Auger Scalers
        """
        opt = {
        'fname_inp' : self.fname_inp,
        'data_name' : data_name,
        }

        """
        the class `_read_auger_scals` reads both versions of
        scalers (old & new).
        """
        sc = _read_auger_scals(**opt)
        t_utc, VARS = sc.read()

        return {
        't_utc'  : t_utc,
        'VARS'   : VARS,
        }


class _data_McMurdo(object):
    def __init__(self, fname_inp):
        self.fname_inp = fname_inp

    def load(self, data_name):
        fname_inp   = self.fname_inp
        data_murdo  = np.loadtxt(fname_inp)
        t_utc       = t_utc = data_murdo[:,0]
        CRs         = data_murdo[:,1]
        print " -------> variables leidas!"

        VARS = {} 
        VARS['CRs.'+data_name] = {
            'value' : CRs,
            'lims'  : [-8.0, 1.0],
            'label' : 'mcmurdo rate [%]'
        }
        return {
        't_utc'  : t_utc,
        'VARS'   : VARS,
        }


#EOF