# -*- coding: utf-8 -*-
"""
"""
import os
from datetime import datetime
from typing import Union, Optional, Any, List, NoReturn
from numbers import Real

import wfdb
import numpy as np
np.set_printoptions(precision=5, suppress=True)
import pandas as pd
from easydict import EasyDict as ED

from ..utils.common import (
    ArrayLike,
    get_record_list_recursive,
    get_record_list_recursive3,
)
from ..base import PhysioNetDataBase


__all__ = [
    "MIMIC3WDB",
]


class MIMIC3WDB(PhysioNetDataBase):
    """ NOT Finished,

    MIMIC-III Waveform Database

    ABOUT mimic3wdb:
    ----------------
    1. contains 67,830 record sets (totally 6.7 TB) for approximately 30,000 ICU patients
    2. almost all record sets include a waveform record (usually multi-record consisting of multiple continuous segments) containing digitized signals (typically including ECG, ABP, respiration, and PPG, and frequently other signals) digitized at 125 Hz with 8-, 10-, or (occasionally) 12-bit resolution and a "numerics" record containing time series of vital signs (HR, RESP, SpO2, BP, etc.) of periodic measurements sampled once per second or once per minute
    3. a subset (the matched subset) of mimic3wdb contains waveform and numerics records that have been matched and time-aligned with MIMIC-III Clinical Database records
    4. each recording comprises two records (a waveform record, usually multi-record consisting of multiple continuous segments, and a matching numerics record) in a single record directory ("folder") with the name of the record.
    5. the record directories are distributed among ten intermediate-level directories (30-39)
    6. in each record directory, there are files of patterns "3[\d]{6}.hea", "3[\d]{6}_[\d]{4}.dat", "3[\d]{6}_[\d]{4}.hea", "3[\d]{6}n.dat", "3[\d]{6}n.hea", "3[\d]{6}_layout.hea"

    NOTE:
    -----

    ISSUES:
    -------
    ref. [3]

    Usage:
    ------
    1. 

    References:
    -----------
    [1] https://mimic.physionet.org/
    [2] https://github.com/MIT-LCP/mimic-code
    [3] https://www.physionet.org/content/mimiciii/1.4/
    [4] https://physionet.org/content/mimic3wdb/1.0/
    [5] https://physionet.org/content/mimic3wdb-matched/1.0/
    """
    def __init__(self, db_dir:Optional[str]=None, working_dir:Optional[str]=None, verbose:int=2, **kwargs):
        """
        Parameters:
        -----------
        db_dir: str, optional,
            storage path of the database
            if not specified, data will be fetched from Physionet
        working_dir: str, optional,
            working directory, to store intermediate files and log file
        verbose: int, default 2,
            print verbosity
        kwargs:
        """
        super().__init__(db_name="mimic3wdb", db_dir=db_dir, working_dir=working_dir, verbose=verbose, **kwargs)
        self.metadata_files = ED(
            all_records=os.path.join(self.db_dir, "RECORDS"),
            waveforms=os.path.join(self.db_dir, "RECORDS-waveforms"),
            numerics=os.path.join(self.db_dir, "RECORDS-numerics"),
            adults=os.path.join(self.db_dir, "RECORDS-adults"),
            neonates=os.path.join(self.db_dir, "RECORDS-neonates"),
        )
        self.rec_pattern = "3[\d]{6}"
        self.sub_dir_pattern = "3[\d]"
        self.fs = 125   # sampling frequency of digitized signals
        
        self.data_ext = "dat"
        self.ann_ext = "hea"
        self._ls_rec()


    def load_data(self, rec:str, ):
        """
        """
        raise NotImplementedError


    def _ls_rec(self) -> NoReturn:
        """
        """
        try:
            tmp = wfdb.get_record_list(self.db_name)
        except:
            with open(self.metadata_files["all_records"], "r") as f:
                tmp = f.read().splitlines()
        self._all_records = {}
        for l in tmp:
            gp, sb = l.strip("/").split("/")
            # add only those which are in local disc
            if os.path.isdir(os.path.join(self.db_dir, gp, sb)):
                if gp in self._all_records.keys():
                    self._all_records[gp].append(sb)
                else:
                    self._all_records[gp] = [sb]
        self._all_records = {k:sorted(v) for k,v in self._all_records.items()}


    def _get_sub_dir(self, rec:str) -> str:
        """
        """
        sub_dir = rec[:2]
        return sub_dir


    def _get_filepath(self, rec:str) -> str:
        """
        """
        sub_dir = self._get_sub_dir(rec)
        fp = os.path.join(self.db_dir, sub_dir, rec)
        return fp


    def get_subject_id(self, rec) -> int:
        """

        """
        raise NotImplementedError
