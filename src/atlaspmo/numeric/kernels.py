"""Numba CPM passes over compiled arrays.

Sentinels sit far below any working-minute delta so a negative float of a few
minutes is never confused with "grow the horizon".
"""

from __future__ import annotations

import sys

import numpy as np

GROW = -9_000_000_000_000_000
LIMIT = GROW - 1

try:
    from numba import njit
except ImportError:  # pragma: no cover - the wheel is part of the install
    njit = None


def run_passes(  # noqa: PLR0913
    cal: np.ndarray,
    duration: np.ndarray,
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
    es: np.ndarray,
    ef: np.ndarray,
    ls: np.ndarray,
    lf: np.ndarray,
    ef_pre: np.ndarray,
    remain: np.ndarray,
    total_f: np.ndarray,
    free_f: np.ndarray,
    critical: np.ndarray,
    drive: np.ndarray,
    done: np.ndarray,
    on_long: np.ndarray,
    viol_ms_f: np.ndarray,
    viol_mf_f: np.ndarray,
    viol_ms_b: np.ndarray,
    viol_mf_b: np.ndarray,
    logic_es: np.ndarray,
    logic_ef: np.ndarray,
    logic_ls: np.ndarray,
    logic_lf: np.ndarray,
    alap_blocked: np.ndarray,
) -> int:
    """Fill the output arrays. Returns 0, GROW, or LIMIT."""
    n = es.shape[0]

    def bad(value: int) -> bool:
        return value <= GROW

    def cumulative(clock: int, minute: int) -> int:
        if minute < window_lo or minute > window_hi:
            return GROW
        lo = off[clock]
        hi = off[clock + 1]
        if hi <= lo:
            return base_cum[clock]
        relative = np.searchsorted(starts[lo:hi], minute, side="right") - 1
        if relative < 0:
            return base_cum[clock]
        index = lo + relative
        if minute < ends[index]:
            return cum[index] + (minute - starts[index])
        return cum_end[index]

    def earliest(clock: int, target: int) -> int:
        if target <= 0:
            return 0
        lo = off[clock]
        hi = off[clock + 1]
        if hi <= lo or target <= cum[lo] or target > cum_end[hi - 1]:
            return GROW
        index = lo + np.searchsorted(cum_end[lo:hi], target, side="left")
        if index >= hi:
            return GROW
        return starts[index] + (target - cum[index])

    def latest(clock: int, target: int) -> int:
        nxt = earliest(clock, target + 1)
        if bad(nxt):
            return nxt
        return nxt - 1

    def snap_forward(clock: int, minute: int) -> int:
        if minute < window_lo or minute > window_hi:
            return GROW
        lo = off[clock]
        hi = off[clock + 1]
        if hi <= lo:
            return GROW
        relative = np.searchsorted(starts[lo:hi], minute, side="right") - 1
        if relative >= 0:
            index = lo + relative
            if minute < ends[index]:
                return minute
        nxt = lo + np.searchsorted(starts[lo:hi], minute, side="left")
        if nxt < hi:
            return starts[nxt]
        return GROW

    def snap_backward(clock: int, minute: int) -> int:
        if minute < window_lo or minute > window_hi:
            return GROW
        lo = off[clock]
        hi = off[clock + 1]
        if hi <= lo:
            return GROW
        relative = np.searchsorted(starts[lo:hi], minute, side="right") - 1
        if relative < 0:
            return GROW
        index = lo + relative
        if minute <= ends[index]:
            return minute
        return ends[index]

    def sub_minutes(clock: int, minute: int, amount: int) -> int:
        if amount == 0:
            return snap_backward(clock, minute)
        base = cumulative(clock, minute)
        if bad(base):
            return base
        target = base - amount
        if target < 0:
            return LIMIT
        return latest(clock, target)

    def add_minutes(clock: int, minute: int, amount: int) -> int:
        if amount < 0:
            return sub_minutes(clock, minute, -amount)
        if amount == 0:
            return snap_forward(clock, minute)
        base = cumulative(clock, minute)
        if bad(base):
            return base
        return earliest(clock, base + amount)

    def apply_lag(clock: int, minute: int, lag: int) -> int:
        if lag == 0:
            return minute
        return add_minutes(clock, minute, lag)

    def work_between(clock: int, start_m: int, end_m: int) -> int:
        left = cumulative(clock, start_m)
        if bad(left):
            return left
        right = cumulative(clock, end_m)
        if bad(right):
            return right
        return right - left

    def first_date(index: int, code: int) -> int:
        if cstr_a[index] == code and cstr_a_at[index] >= 0:
            return cstr_a_at[index]
        if cstr_b[index] == code and cstr_b_at[index] >= 0:
            return cstr_b_at[index]
        return -1

    for edge in range(drive.shape[0]):
        drive[edge] = 0
    for index in range(n):
        alap_blocked[index] = 0
        viol_ms_f[index] = 0
        viol_mf_f[index] = 0
        viol_ms_b[index] = 0
        viol_mf_b[index] = 0
        on_long[index] = 0
        critical[index] = 0
        done[index] = 0
        remain[index] = -1

    if n == 0:
        return 0

    for index in range(n):
        clock = cal[index]
        is_done = finished[index] == 1
        if progress == 2 and act_start[index] >= 0 and act_end[index] >= 0:
            is_done = True
        if is_done:
            es[index] = act_start[index]
            ef[index] = act_end[index]
            done[index] = 1
            continue
        origin = data_date
        if started[index] == 1 and progress == 2 and act_start[index] >= 0:
            origin = act_start[index]
        start = add_minutes(clock, origin, 0)
        if bad(start):
            return start
        ignore = started[index] == 1 and (progress == 1 or progress == 2)
        if not ignore:
            for edge in range(pred_ptr[index], pred_ptr[index + 1]):
                pred = pred_from[edge]
                kind = pred_type[edge]
                lag = pred_lag[edge]
                lag_cal = pred_lag_cal[edge]
                if kind == 1:
                    bound = apply_lag(lag_cal, es[pred], lag)
                elif kind == 3:
                    bound = apply_lag(lag_cal, es[pred], lag)
                    if bad(bound):
                        return bound
                    bound = sub_minutes(clock, bound, duration[index])
                elif kind == 2:
                    bound = apply_lag(lag_cal, ef[pred], lag)
                    if bad(bound):
                        return bound
                    bound = sub_minutes(clock, bound, duration[index])
                else:
                    bound = apply_lag(lag_cal, ef[pred], lag)
                if bad(bound):
                    return bound
                if duration[index] > 0:
                    bound = add_minutes(clock, bound, 0)
                    if bad(bound):
                        return bound
                start = max(start, bound)
        for slot in range(2):
            code = cstr_a[index] if slot == 0 else cstr_b[index]
            raw = cstr_a_at[index] if slot == 0 else cstr_b_at[index]
            if raw < 0 or (code != 1 and code != 2):
                continue
            snapped = add_minutes(clock, raw, 0)
            if bad(snapped):
                return snapped
            start = max(start, snapped)
        if duration[index] == 0:
            finish = start
        else:
            finish = add_minutes(clock, start, duration[index])
            if bad(finish):
                return finish
        if started[index] == 1:
            remain[index] = start
            es[index] = act_start[index] if act_start[index] >= 0 else start
        else:
            es[index] = start
        ef[index] = finish
        for slot in range(2):
            code = cstr_a[index] if slot == 0 else cstr_b[index]
            raw = cstr_a_at[index] if slot == 0 else cstr_b_at[index]
            if raw < 0 or (code != 4 and code != 5):
                continue
            snapped = sub_minutes(clock, raw, 0)
            if bad(snapped):
                return snapped
            if snapped > ef[index]:
                ef[index] = snapped
                pushed = sub_minutes(clock, ef[index], duration[index])
                if bad(pushed):
                    return pushed
                es[index] = max(es[index], pushed)
        if started[index] == 0:
            logic_es[index] = es[index]
            logic_ef[index] = ef[index]
            mand_start = first_date(index, 7)
            mand_finish = first_date(index, 8)
            if mand_start >= 0:
                if mand_start < logic_es[index]:
                    viol_ms_f[index] = 1
                es[index] = mand_start
                if mand_finish < 0:
                    if duration[index] == 0:
                        ef[index] = mand_start
                    else:
                        moved = add_minutes(clock, mand_start, duration[index])
                        if bad(moved):
                            return moved
                        ef[index] = moved
            if mand_finish >= 0:
                if mand_finish < logic_ef[index]:
                    viol_mf_f[index] = 1
                ef[index] = mand_finish
                if mand_start < 0:
                    if duration[index] == 0:
                        es[index] = mand_finish
                    else:
                        moved = sub_minutes(clock, mand_finish, duration[index])
                        if bad(moved):
                            return moved
                        es[index] = moved
            if task_type[index] == 1:
                snapped = add_minutes(clock, es[index], 0)
                if bad(snapped):
                    return snapped
                es[index] = snapped
                ef[index] = snapped
        if not ignore:
            for edge in range(pred_ptr[index], pred_ptr[index + 1]):
                pred = pred_from[edge]
                kind = pred_type[edge]
                lag = pred_lag[edge]
                lag_cal = pred_lag_cal[edge]
                if kind == 1:
                    bound = apply_lag(lag_cal, es[pred], lag)
                elif kind == 3:
                    bound = apply_lag(lag_cal, es[pred], lag)
                    if bad(bound):
                        return bound
                    bound = sub_minutes(clock, bound, duration[index])
                elif kind == 2:
                    bound = apply_lag(lag_cal, ef[pred], lag)
                    if bad(bound):
                        return bound
                    bound = sub_minutes(clock, bound, duration[index])
                else:
                    bound = apply_lag(lag_cal, ef[pred], lag)
                if bad(bound):
                    return bound
                if duration[index] > 0:
                    bound = add_minutes(clock, bound, 0)
                    if bad(bound):
                        return bound
                same = bound == es[index]
                if task_type[index] == 1:
                    opened = add_minutes(clock, bound, 0)
                    if bad(opened):
                        return opened
                    if opened == es[index]:
                        same = True
                if same:
                    drive[edge] = 1

    pf = ef[0]
    for index in range(1, n):
        pf = max(pf, ef[index])
    for index in range(n):
        ef_pre[index] = ef[index]

    for index in range(n - 1, -1, -1):
        clock = cal[index]
        if done[index] == 1:
            ls[index] = es[index]
            lf[index] = ef[index]
            continue
        has_lf = 0
        has_ls = 0
        lf_min = pf
        ls_min = pf
        if succ_ptr[index + 1] == succ_ptr[index]:
            has_lf = 1
            lf_min = pf
        for edge in range(succ_ptr[index], succ_ptr[index + 1]):
            succ = succ_to[edge]
            if ls[succ] < 0 or lf[succ] < 0:
                continue
            kind = succ_type[edge]
            lag = succ_lag[edge]
            lag_cal = succ_lag_cal[edge]
            if kind == 1:
                bound = apply_lag(lag_cal, ls[succ], -lag)
                if bad(bound):
                    return bound
                if has_ls == 0 or bound < ls_min:
                    ls_min = bound
                    has_ls = 1
            elif kind == 3:
                bound = apply_lag(lag_cal, lf[succ], -lag)
                if bad(bound):
                    return bound
                if has_ls == 0 or bound < ls_min:
                    ls_min = bound
                    has_ls = 1
            elif kind == 2:
                bound = apply_lag(lag_cal, lf[succ], -lag)
                if bad(bound):
                    return bound
                if has_lf == 0 or bound < lf_min:
                    lf_min = bound
                    has_lf = 1
            else:
                bound = apply_lag(lag_cal, ls[succ], -lag)
                if bad(bound):
                    return bound
                if has_lf == 0 or bound < lf_min:
                    lf_min = bound
                    has_lf = 1
        for slot in range(2):
            code = cstr_a[index] if slot == 0 else cstr_b[index]
            raw = cstr_a_at[index] if slot == 0 else cstr_b_at[index]
            if raw < 0:
                continue
            if code == 1 or code == 3:
                snapped = sub_minutes(clock, raw, 0)
                if bad(snapped):
                    return snapped
                if has_ls == 0 or snapped < ls_min:
                    ls_min = snapped
                    has_ls = 1
            if code == 4 or code == 6:
                snapped = sub_minutes(clock, raw, 0)
                if bad(snapped):
                    return snapped
                if has_lf == 0 or snapped < lf_min:
                    lf_min = snapped
                    has_lf = 1
        if has_lf == 0:
            lf_min = pf
        late_finish = lf_min
        late_start = sub_minutes(clock, late_finish, duration[index])
        if bad(late_start):
            return late_start
        if has_ls == 1:
            from_start = add_minutes(clock, ls_min, duration[index])
            if bad(from_start):
                return from_start
            if from_start < late_finish:
                late_finish = from_start
                late_start = sub_minutes(clock, late_finish, duration[index])
                if bad(late_start):
                    return late_start
            late_start = min(late_start, ls_min)
        ls[index] = late_start
        lf[index] = late_finish
        if started[index] == 0:
            logic_ls[index] = ls[index]
            logic_lf[index] = lf[index]
            mand_start = first_date(index, 7)
            mand_finish = first_date(index, 8)
            if mand_start >= 0:
                if logic_ls[index] < mand_start:
                    viol_ms_b[index] = 1
                ls[index] = mand_start
                if mand_finish < 0:
                    if duration[index] == 0:
                        lf[index] = mand_start
                    else:
                        moved = add_minutes(clock, mand_start, duration[index])
                        if bad(moved):
                            return moved
                        lf[index] = moved
            if mand_finish >= 0:
                if logic_lf[index] < mand_finish:
                    viol_mf_b[index] = 1
                lf[index] = mand_finish
                if mand_start < 0:
                    if duration[index] == 0:
                        ls[index] = mand_finish
                    else:
                        moved = sub_minutes(clock, mand_finish, duration[index])
                        if bad(moved):
                            return moved
                        ls[index] = moved
            if task_type[index] == 1:
                snapped = add_minutes(clock, ls[index], 0)
                if bad(snapped):
                    return snapped
                ls[index] = snapped
                snapped = add_minutes(clock, lf[index], 0)
                if bad(snapped):
                    return snapped
                lf[index] = snapped

    if rule == 1:
        stack = np.empty(n, dtype=np.int64)
        queued = np.zeros(n, dtype=np.uint8)
        top = 0
        for index in range(n):
            if ef[index] == pf:
                stack[top] = index
                top += 1
                queued[index] = 1
        while top > 0:
            top -= 1
            current = stack[top]
            on_long[current] = 1
            for edge in range(pred_ptr[current], pred_ptr[current + 1]):
                if drive[edge] != 1:
                    continue
                pred = pred_from[edge]
                if queued[pred] == 1:
                    continue
                queued[pred] = 1
                stack[top] = pred
                top += 1

    for index in range(n):
        if cstr_a[index] == 9 or cstr_b[index] == 9:
            if succ_ptr[index + 1] > succ_ptr[index]:
                alap_blocked[index] = 1
            elif ls[index] >= 0:
                es[index] = ls[index]
                ef[index] = lf[index]
                remain[index] = ls[index]
    for index in range(n):
        clock = cal[index]
        origin = remain[index] if remain[index] >= 0 else es[index]
        start_float = work_between(clock, origin, ls[index])
        if bad(start_float):
            return start_float
        finish_float = work_between(clock, ef[index], lf[index])
        if bad(finish_float):
            return finish_float
        if float_kind == 1:
            total = start_float
        elif float_kind == 2:
            total = finish_float
        elif start_float < finish_float:
            total = start_float
        else:
            total = finish_float
        total_f[index] = total
        if succ_ptr[index + 1] == succ_ptr[index]:
            free_f[index] = finish_float
        else:
            have = 0
            best = 0
            for edge in range(succ_ptr[index], succ_ptr[index + 1]):
                succ = succ_to[edge]
                kind = succ_type[edge]
                if kind == 1:
                    gap = work_between(clock, es[index], es[succ])
                elif kind == 2:
                    gap = work_between(clock, ef[index], ef[succ])
                elif kind == 3:
                    gap = work_between(clock, es[index], ef[succ])
                else:
                    gap = work_between(clock, ef[index], es[succ])
                if bad(gap):
                    return gap
                slack = gap - succ_lag[edge]
                if have == 0 or slack < best:
                    best = slack
                    have = 1
            free_f[index] = best if have == 1 else 0
        if rule == 1:
            critical[index] = on_long[index]
        elif total <= critical_minutes:
            critical[index] = 1
        else:
            critical[index] = 0
    return 0


_COMPILED = False
if njit is not None:
    run_passes = njit(cache=True)(run_passes)  # type: ignore[misc]
    _COMPILED = True


def execute(  # noqa: PLR0913
    cal: np.ndarray,
    duration: np.ndarray,
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
    es: np.ndarray,
    ef: np.ndarray,
    ls: np.ndarray,
    lf: np.ndarray,
    ef_pre: np.ndarray,
    remain: np.ndarray,
    total_f: np.ndarray,
    free_f: np.ndarray,
    critical: np.ndarray,
    drive: np.ndarray,
    done: np.ndarray,
    on_long: np.ndarray,
    viol_ms_f: np.ndarray,
    viol_mf_f: np.ndarray,
    viol_ms_b: np.ndarray,
    viol_mf_b: np.ndarray,
    logic_es: np.ndarray,
    logic_ef: np.ndarray,
    logic_ls: np.ndarray,
    logic_lf: np.ndarray,
    alap_blocked: np.ndarray,
) -> int:
    """Run the compiled pass, or the Python function while coverage is tracing."""
    if _COMPILED and sys.gettrace() is None:
        return int(
            run_passes(
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
                alap_blocked,
            )
        )
    target = run_passes.py_func if _COMPILED else run_passes  # type: ignore[attr-defined]
    return int(
        target(
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
            alap_blocked,
        )
    )
