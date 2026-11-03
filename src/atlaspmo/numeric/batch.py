"""Monte Carlo passes. One numba loop over iterations, or Python while coverage traces."""

from __future__ import annotations

import sys

import numpy as np

from atlaspmo.calendars.worktime import CalendarLimitError
from atlaspmo.numeric.kernels import execute, run_passes

try:
    from numba import get_num_threads, get_thread_id, njit, prange
except ImportError:  # pragma: no cover - numba is installed with the project
    get_num_threads = None
    get_thread_id = None
    njit = None
    prange = range

_COMPILED = False


def batch_passes(  # noqa: PLR0913
    cal: np.ndarray,
    base_duration: np.ndarray,
    started: np.ndarray,
    finished: np.ndarray,
    act_start: np.ndarray,
    act_end: np.ndarray,
    task_type: np.ndarray,
    cstr_a: np.ndarray,
    cstr_a_at: np.ndarray,
    cstr_b: np.ndarray,
    cstr_b_at: np.ndarray,
    pred_ptr: np.ndarray,
    pred_from: np.ndarray,
    pred_type: np.ndarray,
    pred_lag: np.ndarray,
    pred_lag_cal: np.ndarray,
    succ_ptr: np.ndarray,
    succ_to: np.ndarray,
    succ_type: np.ndarray,
    succ_lag: np.ndarray,
    succ_lag_cal: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    cum: np.ndarray,
    cum_end: np.ndarray,
    off: np.ndarray,
    base_cum: np.ndarray,
    window_lo: int,
    window_hi: int,
    data_date: int,
    progress: int,
    float_kind: int,
    critical_minutes: int,
    rule: int,
    drive_n: int,
    varied_index: np.ndarray,
    row_minutes: np.ndarray,
    watch: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return finish minutes, critical sums, flags, watched ef, and pass codes."""
    n = base_duration.shape[0]
    n_iter = row_minutes.shape[0]
    nthreads = get_num_threads()
    finishes = np.empty(n_iter, dtype=np.int64)
    codes = np.zeros(n_iter, dtype=np.int64)
    flags = np.zeros((n_iter, n), dtype=np.uint8)
    watched = np.zeros((n_iter, watch.shape[0]), dtype=np.int64)
    crit = np.zeros((nthreads, n), dtype=np.int64)
    i64 = np.empty((nthreads, 13, n), dtype=np.int64)
    u8 = np.empty((nthreads, 8, n), dtype=np.uint8)
    drive = np.empty((nthreads, drive_n), dtype=np.uint8)
    for i in prange(n_iter):
        tid = get_thread_id()
        dur = i64[tid, 0]
        dur[:] = base_duration
        if varied_index.shape[0] > 0:
            dur[varied_index] = row_minutes[i]
        codes[i] = run_passes(
            cal,
            dur,
            started,
            finished,
            act_start,
            act_end,
            task_type,
            cstr_a,
            cstr_a_at,
            cstr_b,
            cstr_b_at,
            pred_ptr,
            pred_from,
            pred_type,
            pred_lag,
            pred_lag_cal,
            succ_ptr,
            succ_to,
            succ_type,
            succ_lag,
            succ_lag_cal,
            starts,
            ends,
            cum,
            cum_end,
            off,
            base_cum,
            window_lo,
            window_hi,
            data_date,
            progress,
            float_kind,
            critical_minutes,
            rule,
            i64[tid, 1],
            i64[tid, 2],
            i64[tid, 3],
            i64[tid, 4],
            i64[tid, 5],
            i64[tid, 6],
            i64[tid, 7],
            i64[tid, 8],
            u8[tid, 0],
            drive[tid],
            u8[tid, 1],
            u8[tid, 2],
            u8[tid, 3],
            u8[tid, 4],
            u8[tid, 5],
            u8[tid, 6],
            i64[tid, 9],
            i64[tid, 10],
            i64[tid, 11],
            i64[tid, 12],
            u8[tid, 7],
        )
        finishes[i] = np.max(i64[tid, 5])
        flags[i] = u8[tid, 0]
        crit[tid] += u8[tid, 0].astype(np.int64)
        watched[i] = i64[tid, 2][watch]
    return finishes, crit.sum(axis=0), flags, watched, codes


if njit is not None:
    batch_passes = njit(cache=True, parallel=True)(batch_passes)  # type: ignore[misc]
    _COMPILED = True


def _python_batch(  # noqa: PLR0913
    cal: np.ndarray,
    base_duration: np.ndarray,
    started: np.ndarray,
    finished: np.ndarray,
    act_start: np.ndarray,
    act_end: np.ndarray,
    task_type: np.ndarray,
    cstr_a: np.ndarray,
    cstr_a_at: np.ndarray,
    cstr_b: np.ndarray,
    cstr_b_at: np.ndarray,
    pred_ptr: np.ndarray,
    pred_from: np.ndarray,
    pred_type: np.ndarray,
    pred_lag: np.ndarray,
    pred_lag_cal: np.ndarray,
    succ_ptr: np.ndarray,
    succ_to: np.ndarray,
    succ_type: np.ndarray,
    succ_lag: np.ndarray,
    succ_lag_cal: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    cum: np.ndarray,
    cum_end: np.ndarray,
    off: np.ndarray,
    base_cum: np.ndarray,
    window_lo: int,
    window_hi: int,
    data_date: int,
    progress: int,
    float_kind: int,
    critical_minutes: int,
    rule: int,
    drive_n: int,
    varied_index: np.ndarray,
    row_minutes: np.ndarray,
    watch: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Same results as the compiled loop, one iteration at a time, so coverage can see it."""
    n = int(base_duration.shape[0])
    n_iter = int(row_minutes.shape[0])
    finishes = np.empty(n_iter, dtype=np.int64)
    codes = np.zeros(n_iter, dtype=np.int64)
    total = np.zeros(n, dtype=np.int64)
    flags = np.zeros((n_iter, n), dtype=np.uint8)
    watched = np.zeros((n_iter, int(watch.shape[0])), dtype=np.int64)
    duration = base_duration.copy()
    es = np.empty(n, dtype=np.int64)
    ef = np.empty(n, dtype=np.int64)
    ls = np.empty(n, dtype=np.int64)
    lf = np.empty(n, dtype=np.int64)
    ef_pre = np.empty(n, dtype=np.int64)
    remain = np.empty(n, dtype=np.int64)
    total_f = np.empty(n, dtype=np.int64)
    free_f = np.empty(n, dtype=np.int64)
    critical = np.empty(n, dtype=np.uint8)
    drive = np.empty(drive_n, dtype=np.uint8)
    done = np.empty(n, dtype=np.uint8)
    on_long = np.empty(n, dtype=np.uint8)
    viol_ms_f = np.empty(n, dtype=np.uint8)
    viol_mf_f = np.empty(n, dtype=np.uint8)
    viol_ms_b = np.empty(n, dtype=np.uint8)
    viol_mf_b = np.empty(n, dtype=np.uint8)
    logic_es = np.empty(n, dtype=np.int64)
    logic_ef = np.empty(n, dtype=np.int64)
    logic_ls = np.empty(n, dtype=np.int64)
    logic_lf = np.empty(n, dtype=np.int64)
    alap = np.empty(n, dtype=np.uint8)
    for i in range(n_iter):
        duration[:] = base_duration
        for column, index in enumerate(varied_index.tolist()):
            duration[int(index)] = int(row_minutes[i, column])
        code = execute(
            cal,
            duration,
            started,
            finished,
            act_start,
            act_end,
            task_type,
            cstr_a,
            cstr_a_at,
            cstr_b,
            cstr_b_at,
            pred_ptr,
            pred_from,
            pred_type,
            pred_lag,
            pred_lag_cal,
            succ_ptr,
            succ_to,
            succ_type,
            succ_lag,
            succ_lag_cal,
            starts,
            ends,
            cum,
            cum_end,
            off,
            base_cum,
            window_lo,
            window_hi,
            data_date,
            progress,
            float_kind,
            critical_minutes,
            rule,
            es,
            ef,
            ls,
            lf,
            ef_pre,
            remain,
            total_f,
            free_f,
            critical,
            drive,
            done,
            on_long,
            viol_ms_f,
            viol_mf_f,
            viol_ms_b,
            viol_mf_b,
            logic_es,
            logic_ef,
            logic_ls,
            logic_lf,
            alap,
        )
        codes[i] = code
        finishes[i] = int(ef_pre.max()) if n and code == 0 else 0
        flags[i] = critical
        total += critical.astype(np.int64)
        if watch.size:
            watched[i] = ef[watch]
    return finishes, total, flags, watched, codes


def run_batch(
    compiled: object,
    varied_index: np.ndarray,
    row_minutes: np.ndarray,
    watch: np.ndarray,
):
    """Run one pass per iteration. Coverage uses the Python loop; otherwise numba prange."""
    tables = compiled.tables
    assert tables is not None
    starts, ends, cum, cum_end, off, base_cum, window_lo, window_hi = tables
    args = (
        compiled.cal,
        np.ascontiguousarray(compiled.duration),
        compiled.started,
        compiled.finished,
        compiled.act_start,
        compiled.act_end,
        compiled.task_type,
        compiled.cstr_a,
        compiled.cstr_a_at,
        compiled.cstr_b,
        compiled.cstr_b_at,
        compiled.pred_ptr,
        compiled.pred_from,
        compiled.pred_type,
        compiled.pred_lag,
        compiled.pred_lag_cal,
        compiled.succ_ptr,
        compiled.succ_to,
        compiled.succ_type,
        compiled.succ_lag,
        compiled.succ_lag_cal,
        starts,
        ends,
        cum,
        cum_end,
        off,
        base_cum,
        int(window_lo),
        int(window_hi),
        int(compiled.data_date),
        int(compiled.progress),
        int(compiled.float_kind),
        int(compiled.critical_minutes),
        int(compiled.rule),
        int(compiled.drive.shape[0]),
        np.ascontiguousarray(varied_index, dtype=np.int64),
        np.ascontiguousarray(row_minutes, dtype=np.int64),
        np.ascontiguousarray(watch, dtype=np.int64),
    )
    if _COMPILED and sys.gettrace() is None:
        finishes, total, flags, watched, codes = batch_passes(*args)
    else:
        finishes, total, flags, watched, codes = _python_batch(*args)
    if codes.size and (int(codes.min()) != 0 or int(codes.max()) != 0):
        raise CalendarLimitError("horizonte de calendario agotado")
    return finishes, total, flags, watched
