from typing import Dict, List, Tuple

import numpy as np
import math


class SwingingDoor:

    def init_snap(self, archived_pnt: Dict[str, float], value: float, trade_date: int,
                  time: int, positive_dev: float, negative_dev: float) -> Dict[str, float]:
        """
        Initializes a snapshot for the Swinging Door algorithm.

        Args:
            archived_pnt: The previously archived point.
            value: Current value.
            trade_date: Trade date for the current value.
            time: Time index for the current value.
            positive_dev: Positive deviation factor.
            negative_dev: Negative deviation factor.

        Returns:
            A dictionary representing the initialized snapshot.
        """
        prev_val = float(archived_pnt['value'])
        prev_time = int(archived_pnt['time_value'])
        time = int(time)
        value = float(value)
        Smax = (value + positive_dev * value - prev_val) / (time - prev_time)
        Smin = (value - negative_dev * value - prev_val) / (time - prev_time)
        slope = (value - prev_val) / (time - prev_time)

        return {
            'value': value,
            'trade_date': trade_date,
            'time': time,
            'Smax': Smax,
            'Smin': Smin,
            'Slope': slope
        }

    def snap_archive(self, snapshot: Dict[str, float], is_snap: bool) -> Dict[str, float]:
        """
        Creates a snapshot for archiving.

        Args:
            snapshot: The snapshot to be archived.
            is_snap: Flag indicating if the snapshot is for archiving.

        Returns:
            A dictionary representing the archived snapshot.
        """
        return {
            'value': snapshot['value'],
            'trade_date': snapshot['trade_date'],
            'time_value': snapshot['time'],
            'is_snap': is_snap,
        }

    def compress(self, time_series: List[float], kwh_sens: float, average_minutes: int) -> Tuple[List[float], List[int]]:
        """
        Returns the Swinging Door compression of a time-series.

        Args:
            time_series: List of time-series data points.
            kwh_sens: Sensitivity factor for deviation.
            average_minutes: Window size for averaging.

        Returns:
            A tuple of lists containing the compressed series values and corresponding timestamps.
        """
        archive: List[Dict[str, float]] = []
        res: List[float] = []
        times: List[int] = []

        POSITIVE_DEV: float = kwh_sens / 100
        NEGATIVE_DEV: float = POSITIVE_DEV

        counter: int = 0
        archive_count: int = 0

        for idx, val in enumerate(time_series):
            value: float = val
            trade_date: int = idx

            if counter == 0:
                # This is the header so we skip this iteration
                pass

            elif counter == 1:
                # This is the first data point, always added into archive
                archive.append({
                    'value': value,
                    'trade_date': trade_date,
                    'time_value': counter,
                    'is_snap': False,
                })
                archive_count += 1

            elif counter == 2:
                # This is the first snapshot that we will receive
                SNAPSHOT: Dict[str, float] = self.init_snap(
                    archive[archive_count - 1],
                    value,
                    trade_date,
                    counter,
                    POSITIVE_DEV,
                    NEGATIVE_DEV,
                )

                tmp_arch: Dict[str, float] = self.snap_archive(SNAPSHOT, False)
                archive.append(tmp_arch)
                res.append(tmp_arch['value'])
                times.append(tmp_arch['trade_date'])

            else:
                # Set up incoming value
                INCOMING: Dict[str, float] = self.init_snap(
                    archive[archive_count - 1],
                    value,
                    trade_date,
                    counter,
                    POSITIVE_DEV,
                    NEGATIVE_DEV,
                )
                if SNAPSHOT['Smin'] <= INCOMING['Slope'] <= SNAPSHOT['Smax']:
                    # It is within the filtration bounds, edit the INCOMING and
                    # set the SNAPSHOT. When editing INCOMING, make sure that the incoming
                    # slopes are not bigger than the current SNAPSHOT's slopes
                    INCOMING['Smax'] = min(SNAPSHOT['Smax'], INCOMING['Smax'])
                    INCOMING['Smin'] = max(SNAPSHOT['Smin'], INCOMING['Smin'])
                    SNAPSHOT = INCOMING
                else:
                    # It is outside the bounds so we must archive the current SNAPSHOT
                    # and init a new snap using this new archived point and INCOMING
                    tmp_arch: Dict[str, float] = self.snap_archive(SNAPSHOT, False)
                    archive.append(tmp_arch)
                    res.append(tmp_arch['value'])
                    times.append(tmp_arch['trade_date'])

                    archive_count += 1
                    SNAPSHOT = self.init_snap(
                        archive[archive_count - 1],
                        value,
                        trade_date,
                        counter,
                        POSITIVE_DEV,
                        NEGATIVE_DEV,
                    )

            counter += 1

        # Always add the latest point into the archive
        tmp_arch: Dict[str, float] = self.snap_archive(SNAPSHOT, True)
        archive.append(tmp_arch)
        res.append(tmp_arch['value'])
        times.append(tmp_arch['trade_date'])

        return self.average_per_hour(res, times, average_minutes)

    def average_per_hour(self, series: List[float], times: List[int], minutes: int) -> Tuple[List[float], List[int]]:
        """
        Computes average values per hour.

        Args:
            series: List of values.
            times: List of corresponding timestamps.
            minutes: Window size for averaging.

        Returns:
            A tuple of lists containing the averaged series values and corresponding timestamps.
        """
        res_times: List[int] = []
        res_series: List[float] = []

        end: int = times[-1]
        end = math.ceil(end / minutes) * minutes

        for i in range(0, end, minutes):
            min_time: int = i
            max_time: int = i + minutes
            tmp_observations: List[float] = []

            for idx, val in enumerate(times):
                if min_time <= val <= max_time:
                    tmp_observations.append(series[idx])

            res_times.extend([x for x in range(i, i + minutes)])

            if len(tmp_observations) < 1:
                tmp_observations = [res_series[-1]]

            avg: float = np.average(tmp_observations)
            res_series.extend([avg for _ in range(0, minutes)])

        return res_series, res_times