import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod, abstractproperty
from six import with_metaclass


class BarReader(with_metaclass(ABCMeta, object)):
    @abstractproperty
    def data_frequency(self):
        pass

    @abstractmethod
    def load_raw_arrays(self, columns, start_date, end_date, assets):
        """
        Parameters
        ----------
        columns : list of str
           'open', 'high', 'low', 'close', or 'volume'
        start_date: Timestamp
           Beginning of the window range.
        end_date: Timestamp
           End of the window range.
        assets : list of int
           The asset identifiers in the window.
        Returns
        -------
        list of np.ndarray
            A list with an entry per field of ndarrays with shape
            (minutes in range, sids) with a dtype of float64, containing the
            values for the respective field over start and end dt range.
        """
        pass

    @abstractproperty
    def last_available_dt(self):
        """
        Returns
        -------
        dt : pd.Timestamp
            The last session for which the reader can provide data.
        """
        pass

    @abstractproperty
    def trading_calendar(self):
        """
        Returns the trading_calendars.calendar used to read
        the data.  Can be None (if the writer didn't specify it).
        """
        pass

    @abstractproperty
    def first_trading_day(self):
        """
        Returns
        -------
        dt : pd.Timestamp
            The first trading day (session) for which the reader can provide
            data.
        """
        pass

    @abstractmethod
    def get_value(self, sid, dt, field):
        """
        Retrieve the value at the given coordinates.
        Parameters
        ----------
        sid : int
            The asset identifier.
        dt : pd.Timestamp
            The timestamp for the desired data point.
        field : string
            The OHLVC name for the desired data point.
        Returns
        -------
        value : float|int
            The value at the given coordinates, ``float`` for OHLC, ``int``
            for 'volume'.
        Raises
        ------
        NoDataOnDate
            If the given dt is not a valid market minute (in minute mode) or
            session (in daily mode) according to this reader's tradingcalendar.
        """
        pass

    @abstractmethod
    def get_last_traded_dt(self, asset, dt):
        """
        Get the latest minute on or before ``dt`` in which ``asset`` traded.
        If there are no trades on or before ``dt``, returns ``pd.NaT``.
        Parameters
        ----------
        asset : zipline.asset.Asset
            The asset for which to get the last traded minute.
        dt : pd.Timestamp
            The minute at which to start searching for the last traded minute.
        Returns
        -------
        last_traded : pd.Timestamp
            The dt of the last trade for the given asset, using the input
            dt as a vantage point.
        """
        pass


class SessionBarReader(BarReader):
    """
    Reader for OHCLV pricing data at a session frequency.
    """
    @property
    def data_frequency(self):
        return 'session'

    @abstractproperty
    def sessions(self):
        """
        Returns
        -------
        sessions : DatetimeIndex
           All session labels (unioning the range for all assets) which the
           reader can provide.
        """
        pass


class ContinuousFutureSessionBarReader(SessionBarReader):

    def __init__(self, bar_reader, roll_finders):
        self._bar_reader = bar_reader
        self._roll_finders = roll_finders

    def load_raw_arrays(self, columns, start_date, end_date, assets):
        """
        Parameters
        ----------
        fields : list of str
            'sid'
        start_dt: Timestamp
           Beginning of the window range.
        end_dt: Timestamp
           End of the window range.
        sids : list of int
           The asset identifiers in the window.
        Returns
        -------
        list of np.ndarray
            A list with an entry per field of ndarrays with shape
            (minutes in range, sids) with a dtype of float64, containing the
            values for the respective field over start and end dt range.
        """
        rolls_by_asset = {}
        for asset in assets:
            rf = self._roll_finders[asset.roll_style]
            rolls_by_asset[asset] = rf.get_rolls(
                asset.root_symbol,
                start_date,
                end_date,
                asset.offset
            )

        num_sessions = len(
            self.trading_calendar.sessions_in_range(start_date, end_date)
        )
        shape = num_sessions, len(assets)

        results = []

        tc = self._bar_reader.trading_calendar
        sessions = tc.sessions_in_range(start_date, end_date)

        # Get partitions
        partitions_by_asset = {}
        for asset in assets:
            partitions = []
            partitions_by_asset[asset] = partitions

            rolls = rolls_by_asset[asset]
            start = start_date

            for roll in rolls:
                sid, roll_date = roll
                start_loc = sessions.get_loc(start)

                if roll_date is not None:
                    end = roll_date - sessions.freq
                    end_loc = sessions.get_loc(end)
                else:
                    end = end_date
                    end_loc = len(sessions) - 1

                partitions.append((sid, start, end, start_loc, end_loc))

                if roll_date is not None:
                    start = sessions[end_loc + 1]

        for column in columns:
            if column != 'volume' and column != 'sid':
                out = np.full(shape, np.nan)
            else:
                out = np.zeros(shape, dtype=np.int64)

            for i, asset in enumerate(assets):
                partitions = partitions_by_asset[asset]

                for sid, start, end, start_loc, end_loc in partitions:
                    if column != 'sid':
                        result = self._bar_reader.load_raw_arrays(
                            [column], start, end, [sid])[0][:, 0]
                    else:
                        result = int(sid)
                    out[start_loc:end_loc + 1, i] = result

            results.append(out)

        return results

    @property
    def last_available_dt(self):
        """
        Returns
        -------
        dt : pd.Timestamp
            The last session for which the reader can provide data.
        """
        return self._bar_reader.last_available_dt

    @property
    def trading_calendar(self):
        """
        Returns the zipline.utils.calendar.trading_calendar used to read
        the data.  Can be None (if the writer didn't specify it).
        """
        return self._bar_reader.trading_calendar

    @property
    def first_trading_day(self):
        """
        Returns
        -------
        dt : pd.Timestamp
            The first trading day (session) for which the reader can provide
            data.
        """
        return self._bar_reader.first_trading_day

    def get_value(self, continuous_future, dt, field):
        """
        Retrieve the value at the given coordinates.
        Parameters
        ----------
        sid : int
            The asset identifier.
        dt : pd.Timestamp
            The timestamp for the desired data point.
        field : string
            The OHLVC name for the desired data point.
        Returns
        -------
        value : float|int
            The value at the given coordinates, ``float`` for OHLC, ``int``
            for 'volume'.
        Raises
        ------
        NoDataOnDate
            If the given dt is not a valid market minute (in minute mode) or
            session (in daily mode) according to this reader's tradingcalendar.
        """
        rf = self._roll_finders[continuous_future.roll_style]
        sid = (rf.get_contract_center(continuous_future.root_symbol,
                                      dt,
                                      continuous_future.offset))
        return self._bar_reader.get_value(sid, dt, field)

    def get_last_traded_dt(self, asset, dt):
        """
        Get the latest minute on or before ``dt`` in which ``asset`` traded.
        If there are no trades on or before ``dt``, returns ``pd.NaT``.
        Parameters
        ----------
        asset : zipline.asset.Asset
            The asset for which to get the last traded minute.
        dt : pd.Timestamp
            The minute at which to start searching for the last traded minute.
        Returns
        -------
        last_traded : pd.Timestamp
            The dt of the last trade for the given asset, using the input
            dt as a vantage point.
        """
        rf = self._roll_finders[asset.roll_style]
        sid = (rf.get_contract_center(asset.root_symbol,
                                      dt,
                                      asset.offset))
        if sid is None:
            return pd.NaT
        contract = rf.asset_finder.retrieve_asset(sid)
        return self._bar_reader.get_last_traded_dt(contract, dt)

    @property
    def sessions(self):
        """
        Returns
        -------
        sessions : DatetimeIndex
           All session labels (unioning the range for all assets) which the
           reader can provide.
        """
        return self._bar_reader.sessions
