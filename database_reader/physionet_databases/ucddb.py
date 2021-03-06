# -*- coding: utf-8 -*-
"""
"""
import os
from pyedflib import EdfReader
from datetime import datetime
from typing import Union, Optional, Any, List, NoReturn
from numbers import Real

import wfdb
import numpy as np
np.set_printoptions(precision=5, suppress=True)
import pandas as pd

from ..utils.common import (
    ArrayLike,
    get_record_list_recursive,
)
from ..base import PhysioNetDataBase


__all__ = [
    "UCDDB",
]


class UCDDB(PhysioNetDataBase):
    """ NOT finished,

    St. Vincent"s University Hospital / University College Dublin Sleep Apnea Database

    ABOUT ucddb:
    ------------
    1. contains 25 full overnight polysomnograms (PSGs) with simultaneous three-channel Holter ECGs
        *.rec --- PSG data in EDF format
        *_lifecard.edf --- ECG data in EDF format 
    2. PSG signals recorded were:
        EEG (C3-A2),
        EEG (C4-A1),
        left EOG,
        right EOG,
        submental EMG,
        ECG (modified lead V2),
        oro-nasal airflow (thermistor),
        ribcage movements,
        abdomen movements (uncalibrated strain gauges),
        oxygen saturation (finger pulse oximeter),
        snoring (tracheal microphone),
        body position
    3. holter ECG leads: V5, CC5, V5R
    4. sleep stage annotations:
        0 - Wake
        1 - REM
        2 - Stage 1
        3 - Stage 2
        4 - Stage 3
        5 - Stage 4
        6 - Artifact
        7 - Indeterminate
    5. respiratory events:
        O - obstructive, apneas,
        C - central apneas,
        M - mixed apneas,
        HYP - hypopneas,
        PB - periodic breathing episodes
        CS - Cheynes-Stokes
        Bradycardia / Tachycardia

    NOTE:
    -----
    1. this dataset is NOT in the standard wfdb format, but rather in EDF format
    2. in record ucddb002, only two distinct ECG signals were recorded; the second ECG signal was also used as the third signal.

    ISSUES:
    -------

    Usage:
    ------
    1. sleep stage
    2. sleep apnea

    References:
    -----------
    [1] https://physionet.org/content/ucddb/1.0.0/
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
        """
        super().__init__(db_name="ucddb", db_dir=db_dir, working_dir=working_dir, verbose=verbose, **kwargs)
        self.data_ext = "rec"
        self.extra_data_ext = "_lifecard.edf"
        self.ann_ext = None
        self.stage_ann_ext = "_stage.txt"
        self.event_ann_ext = "_stage.txt"
        
        self._ls_rec()
        
        self.fs = None
        self.file_opened = None


    def safe_edf_file_operation(self, operation:str="close", full_file_path:Optional[str]=None) -> Union[EdfReader, NoReturn]:
        """ finished, checked,

        Parameters:
        -----------
        operation: str, default "close",
            operation name, can be "open" and "close"
        full_file_path: str, optional,
            path of the file which contains the psg data,
            if not given, default path will be used
        
        Returns:
        --------

        """
        if operation == "open":
            if self.file_opened is not None:
                self.file_opened._close()
            self.file_opened = EdfReader(full_file_path)
        elif operation =="close":
            if self.file_opened is not None:
                self.file_opened._close()
                self.file_opened = None
        else:
            raise ValueError("Illegal operation")


    def get_subject_id(self, rec) -> int:
        """

        """
        raise NotImplementedError


    def database_info(self) -> NoReturn:
        """

        """
        print(self.__doc__)
