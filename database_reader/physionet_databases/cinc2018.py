# -*- coding: utf-8 -*-
"""
"""
import os
import wfdb
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Union, Optional, Any, List, NoReturn
from numbers import Real

from database_reader.utils.common import (
    ArrayLike,
    get_record_list_recursive,
)
from database_reader.base import PhysioNetDataBase


__all__ = [
    "CINC2018",
]


class CINC2018(PhysioNetDataBase):
    """ NOT Finished

    You Snooze You Win - The PhysioNet Computing in Cardiology Challenge 2018

    ABOUT CINC2018:
    ---------------
    1. includes 1,985 subjects, partitioned into balanced training (n = 994), and test sets (n = 989)
    2. signals include
        electrocardiogram (ECG),
        electroencephalography (EEG),
        electrooculography (EOG),
        electromyography (EMG),
        electrocardiology (EKG),
        oxygen saturation (SaO2)
    3. frequency of all signal channels is 200 Hz
    4. units of signals:
        mV for ECG, EEG, EOG, EMG, EKG
        percentage for SaO2
    5. six sleep stages were annotated in 30 second contiguous intervals:
        wakefulness,
        stage 1,
        stage 2,
        stage 3,
        rapid eye movement (REM),
        undefined
    6. annotated arousals were classified as either of the following:
        spontaneous arousals,
        respiratory effort related arousals (RERA),
        bruxisms,
        hypoventilations,
        hypopneas,
        apneas (central, obstructive and mixed),
        vocalizations,
        snores,
        periodic leg movements,
        Cheyne-Stokes breathing,
        partial airway obstructions

    NOTE:
    -----

    ISSUES:
    -------

    Usage:
    ------
    1. sleep stage
    2. sleep apnea

    References:
    -----------
    [1] https://physionet.org/content/challenge-2018/1.0.0/
    """
    def __init__(self, db_dir:str, working_dir:Optional[str]=None, verbose:int=2, **kwargs):
        """
        Parameters:
        -----------
        db_dir: str, optional,
            storage path of the database
        working_dir: str, optional,
            working directory, to store intermediate files and log file
        verbose: int, default 2,
        """
        super().__init__(db_name='CINC2018', db_dir=db_dir, working_dir=working_dir, verbose=verbose, **kwargs)
        self.freq = None
        self.training_dir = os.path.join(self.db_dir, 'training')
        self.test_dir = os.path.join(self.db_dir, 'test')
        self.training_records = []
        self.test_records = []
        self.all_records = []


    def get_subject_id(self, rec) -> int:
        """

        """
        head = '2018'
        mid = rec[2:4]
        tail = rec[-4:]
        pid = int(head+mid+tail)
        return pid


    def database_info(self) -> NoReturn:
        """

        """
        print(self.__doc__)
