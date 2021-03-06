# -*- coding: utf-8 -*-
"""
"""
import os, json
from datetime import datetime
from typing import Union, Optional, Any, List, Dict, Sequence, NoReturn
from numbers import Real

import numpy as np
np.set_printoptions(precision=5, suppress=True)
import pandas as pd
from scipy.io import loadmat

from ..utils.common import (
    ArrayLike,
    get_record_list_recursive,
    DEFAULT_FIG_SIZE_PER_SEC,
)
from ..base import OtherDataBase


__all__ = [
    "CPSC2019",
    "compute_metrics",
]


class CPSC2019(OtherDataBase):
    """

    The 2nd China Physiological Signal Challenge (CPSC 2019):
    Challenging QRS Detection and Heart Rate Estimation from Single-Lead ECG Recordings

    ABOUT CPSC2019:
    ---------------
    1. Training data consists of 2,000 single-lead ECG recordings collected from patients with cardiovascular disease (CVD)
    2. Each of the recording last for 10 s
    3. Sampling rate = 500 Hz

    NOTE:
    -----

    ISSUES:
    -------
    1. there're 13 records with unusual large values (> 20 mV):
        data_00098, data_00167, data_00173, data_00223, data_00224, data_00245, data_00813,
        data_00814, data_00815, data_00833, data_00841, data_00949, data_00950
    >>> for rec in dr.all_records:
    >>>     data = dr.load_data(rec)
    >>>     if np.max(data) > 20:
    >>>         print(f"{rec} has max value ({np.max(data)} mV) > 20 mV")
    ... data_00173 has max value (32.72031811111111 mV) > 20 mV
    ... data_00223 has max value (32.75516713333333 mV) > 20 mV
    ... data_00224 has max value (32.7519272 mV) > 20 mV
    ... data_00245 has max value (32.75305293939394 mV) > 20 mV
    ... data_00813 has max value (32.75865595876289 mV) > 20 mV
    ... data_00814 has max value (32.75865595876289 mV) > 20 mV
    ... data_00815 has max value (32.75558282474227 mV) > 20 mV
    ... data_00833 has max value (32.76330123809524 mV) > 20 mV
    ... data_00841 has max value (32.727626558139534 mV) > 20 mV
    ... data_00949 has max value (32.75699667692308 mV) > 20 mV
    ... data_00950 has max value (32.769551661538465 mV) > 20 mV
    2. rpeak references (annotations) loaded from files has dtype = uint16,
    which would produce unexpected large positive values when subtracting values larger than it,
    rather than the correct negative value.
    This might cause confusion in computing metrics when using annotations subtracting
    (instead of being subtracted by) predictions.
    3. official scoring function has errors, 
    which would falsely omit the interval between the 0-th and the 1-st ref rpeaks,
    thus potentially missing false positive

    Usage:
    ------
    1. ecg wave delineation

    References:
    -----------
    [1] http://2019.icbeb.org/Challenge.html
    """
    def __init__(self, db_dir:str, working_dir:Optional[str]=None, verbose:int=2, **kwargs):
        """ finished, to be improved,

        Parameters:
        -----------
        db_dir: str,
            storage path of the database
        working_dir: str, optional,
            working directory, to store intermediate files and log file
        verbose: int, default 2,
        """
        super().__init__(db_name="CPSC2019", db_dir=db_dir, working_dir=working_dir, verbose=verbose, **kwargs)
        
        self.fs = 500
        self.spacing = 1000 / self.fs

        self.rec_ext = ".mat"
        self.ann_ext = ".mat"

        # self.all_references = self.all_annotations
        self.rec_dir = os.path.join(self.db_dir, "data")
        self.ann_dir = os.path.join(self.db_dir, "ref")

        self.nb_records = 2000
        self._all_records = [f"data_{i:05d}" for i in range(1,1+self.nb_records)]
        self._all_annotations = [f"R_{i:05d}" for i in range(1,1+self.nb_records)]
        self._ls_rec()

        # aliases
        self.data_dir = self.rec_dir
        self.ref_dir = self.ann_dir


    def _ls_rec(self) -> NoReturn:
        """ finished, checked,
        """
        records_fn = os.path.join(self.db_dir, "records.json")
        if os.path.isfile(records_fn):
            with open(records_fn, "r") as f:
                records_json = json.load(f)
                self._all_records = records_json["rec"]
                self._all_annotations = records_json["ann"]
            return
        print(f"Please allow some time for the reader to confirm the existence of corresponding data files and annotation files...")
        self._all_records = [
            rec for rec in self._all_records \
                if os.path.isfile(os.path.join(self.rec_dir, f"{rec}{self.rec_ext}"))
        ]
        self._all_annotations = [
            ann for ann in self._all_annotations \
                if os.path.isfile(os.path.join(self.ann_dir, f"{ann}{self.ann_ext}"))
        ]
        common = set([rec.split("_")[1] for rec in self._all_records]) \
            & set([ann.split("_")[1] for ann in self._all_annotations])
        common = sorted(list(common))
        self._all_records = [f"data_{item}" for item in common]
        self._all_annotations = [f"R_{item}" for item in common]
        with open(records_fn, "w") as f:
            records_json = {"rec": self._all_records, "ann": self._all_annotations}
            json.dump(records_json, f, ensure_ascii=False)


    @property
    def all_annotations(self):
        """
        """
        return self._all_annotations

    @property
    def all_references(self):
        """
        """
        return self._all_annotations


    def get_subject_id(self, rec_no:int) -> int:
        """ not finished,

        Parameters:
        -----------
        rec_no: int,
            number of the record, NOTE that rec_no starts from 1

        Returns:
        --------
        pid: int,
            the `subject_id` corr. to `rec_no`
        """
        pid = 0
        raise NotImplementedError


    def database_info(self, detailed:bool=False) -> NoReturn:
        """ not finished,

        print the information about the database

        Parameters:
        -----------
        detailed: bool, default False,
            if False, an short introduction of the database will be printed,
            if True, then docstring of the class will be printed additionally
        """
        raw_info = {}

        print(raw_info)
        
        if detailed:
            print(self.__doc__)

    
    def load_data(self, rec:Union[int,str], units:str="mV", keep_dim:bool=True) -> np.ndarray:
        """ finished, checked,

        Parameters:
        -----------
        rec_no: int,
            number of the record, NOTE that rec_no starts from 1
        keep_dim: bool, default True,
            whether or not to flatten the data of shape (n,1)
        
        Returns:
        --------
        data: ndarray,
            the ecg data
        """
        fp = os.path.join(self.data_dir, f"{self._get_rec_name(rec)}{self.rec_ext}")
        data = loadmat(fp)["ecg"]
        if units.lower() in ["uv", "μv",]:
            data = (1000 * data).astype(int)
        if not keep_dim:
            data = data.flatten()
        return data


    def load_ann(self, rec:Union[int,str], keep_dim:bool=True) -> Dict[str, np.ndarray]:
        """ finished, checked,

        Parameters:
        -----------
        rec: int or str,
            number of the record, NOTE that rec_no starts from 1,
            or the record name
        keep_dim: bool, default True,
            whether or not to flatten the data of shape (n,1)
        
        Returns:
        --------
        ann: dict,
            with items "SPB_indices" and "PVC_indices", which record the indices of SPBs and PVCs
        """
        fp = os.path.join(self.ann_dir, f"{self._get_ann_name(rec)}{self.ann_ext}")
        ann = loadmat(fp)["R_peak"].astype(int)
        if not keep_dim:
            ann = ann.flatten()
        return ann


    def load_rpeaks(self, rec:Union[int,str], keep_dim:bool=True) -> Dict[str, np.ndarray]:
        """
        alias of `self.load_ann`
        """
        return self.load_ann(rec=rec, keep_dim=keep_dim)


    def _get_rec_name(self, rec:Union[int,str]) -> str:
        """ finished, checked,

        Parameters:
        -----------
        rec: int or str,
            number of the record, NOTE that rec_no starts from 1,
            or the record name

        Returns:
        --------
        rec_name: str,
            filename of the record
        """
        if isinstance(rec, int):
            assert rec in range(1, self.nb_records+1), f"rec should be in range(1,{self.nb_records+1})"
            rec_name = self.all_records[rec-1]
        elif isinstance(rec, str):
            assert rec in self.all_records, f"rec {rec} not found"
            rec_name = rec
        return rec_name


    def _get_ann_name(self, rec:Union[int,str]) -> str:
        """ finished, checked,

        Parameters:
        -----------
        rec: int or str,
            number of the record, NOTE that rec_no starts from 1,
            or the record name

        Returns:
        --------
        ann_name: str,
            filename of annotations of the record `rec`
        """
        rec_name = self._get_rec_name(rec)
        ann_name = rec_name.replace("data", "R")
        return ann_name


    def plot(self, rec:Union[int,str], data:Optional[np.ndarray]=None, ann:Optional[np.ndarray]=None, ticks_granularity:int=0) -> NoReturn:
        """ finished, checked,

        Parameters:
        -----------
        rec: int or str,
            number of the record, NOTE that rec_no starts from 1,
            or the record name
        data: ndarray, optional,
            ecg signal to plot,
            if given, data of `rec` will not be used,
            this is useful when plotting filtered data
        ann: ndarray, optional,
            annotations (rpeak indices) for `data`,
            ignored if `data` is None
        ticks_granularity: int, default 0,
            the granularity to plot axis ticks, the higher the more,
            0 (no ticks) --> 1 (major ticks) --> 2 (major + minor ticks)
        """
        if "plt" not in dir():
            import matplotlib.pyplot as plt

        if data is None:
            _data = self.load_data(rec, units="μV", keep_dim=False)
        else:
            units = self._auto_infer_units(data)
            if units == "mV":
                _data = data * 1000
            elif units == "μV":
                _data = data.copy()

        duration = len(_data) / self.fs
        secs = np.linspace(0, duration, len(_data))
        if ann is None or data is None:
            rpeak_secs = self.load_rpeaks(rec, keep_dim=False) / self.fs
        else:
            rpeak_secs = np.array(ann) / self.fs

        fig_sz_w = int(DEFAULT_FIG_SIZE_PER_SEC * duration)
        y_range = np.max(np.abs(_data))
        fig_sz_h = 6 * y_range / 1500
        fig, ax = plt.subplots(figsize=(fig_sz_w, fig_sz_h))
        ax.plot(secs, _data, color="black")
        ax.axhline(y=0, linestyle="-", linewidth="1.0", color="red")
        if ticks_granularity >= 1:
            ax.xaxis.set_major_locator(plt.MultipleLocator(0.2))
            ax.yaxis.set_major_locator(plt.MultipleLocator(500))
            ax.grid(which="major", linestyle="-", linewidth="0.5", color="red")
        if ticks_granularity >= 2:
            ax.xaxis.set_minor_locator(plt.MultipleLocator(0.04))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(100))
            ax.grid(which="minor", linestyle=":", linewidth="0.5", color="black")
        for r in rpeak_secs:
            ax.axvspan(r-0.01, r+0.01, color="green", alpha=0.9)
            ax.axvspan(r-0.075, r+0.075, color="green", alpha=0.3)
        ax.set_xlim(secs[0], secs[-1])
        ax.set_ylim(-y_range, y_range)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Voltage [μV]")
        plt.show()



def compute_metrics(rpeaks_truth:Sequence[Union[np.ndarray,Sequence[int]]], rpeaks_pred:Sequence[Union[np.ndarray,Sequence[int]]], fs:Real, thr:float=0.075, verbose:int=0) -> float:
    """ finished, checked,

    metric (scoring) function modified from the official one, with errors fixed

    Parameters:
    -----------
    rpeaks_truth: sequence,
        sequence of ground truths of rpeaks locations from multiple records
    rpeaks_pred: sequence,
        predictions of ground truths of rpeaks locations for multiple records
    fs: real number,
        sampling frequency of ECG signal
    thr: float, default 0.075,
        threshold for a prediction to be truth positive,
        with units in seconds,
    verbose: int, default 0,
        print verbosity

    Returns:
    --------
    rec_acc: float,
        accuracy of predictions
    """
    assert len(rpeaks_truth) == len(rpeaks_pred), \
        f"number of records does not match, truth indicates {len(rpeaks_truth)}, while pred indicates {len(rpeaks_pred)}"
    n_records = len(rpeaks_truth)
    record_flags = np.ones((len(rpeaks_truth),), dtype=float)
    thr_ = thr * fs
    if verbose >= 1:
        print(f"number of records = {n_records}")
        print(f"threshold in number of sample points = {thr_}")
    for idx, (truth_arr, pred_arr) in enumerate(zip(rpeaks_truth, rpeaks_pred)):
        false_negative = 0
        false_positive = 0
        true_positive = 0
        extended_truth_arr = np.concatenate((truth_arr.astype(int), [int(9.5*fs)]))
        for j, t_ind in enumerate(extended_truth_arr[:-1]):
            next_t_ind = extended_truth_arr[j+1]
            loc = np.where(np.abs(pred_arr - t_ind) <= thr_)[0]
            if j == 0:
                err = np.where((pred_arr >= 0.5*fs + thr_) & (pred_arr <= t_ind - thr_))[0]
            else:
                err = np.array([], dtype=int)
            err = np.append(
                err,
                np.where((pred_arr >= t_ind+thr_) & (pred_arr <= next_t_ind-thr_))[0]
            )

            false_positive += len(err)
            if len(loc) >= 1:
                true_positive += 1
                false_positive += len(loc) - 1
            elif len(loc) == 0:
                false_negative += 1

        if false_negative + false_positive > 1:
            record_flags[idx] = 0
        elif false_negative == 1 and false_positive == 0:
            record_flags[idx] = 0.3
        elif false_negative == 0 and false_positive == 1:
            record_flags[idx] = 0.7

        if verbose >= 2:
            print(f"for the {idx}-th record,\ntrue positive = {true_positive}\nfalse positive = {false_positive}\nfalse negative = {false_negative}")

    rec_acc = round(np.sum(record_flags) / n_records, 4)
    print(f"QRS_acc: {rec_acc}")
    print("Scoring complete.")

    return rec_acc
