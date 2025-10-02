import numpy as np
import h5py

# HDF5 structure:
# Data
#   Positioning
#      ArrayIndex: O
#      ObjectPosition: O
#         Azimuth: >f8
#         elevation: >f8
#      ObjectOffset
#         CenterH: >f8
#         CenterV: >f8
#      TrueMeasurementPosition
#         Azimuth: >f8
#         Elevation: >f8
#      TrueTime: >f8
#   Spectrometer
#      IQRate: >f8
#      CarrierFrequency: >f8
#      Gain: >f8
#      BasebandPowerSpectrum: O
#      N_FFT: >u4
#      N_AVG: >u4
#      Window: >u4
#      t_int_ms: >u4

class SRT_HDF_Reader:
    """
    Reader for SRT HDF5 files with structure:
    Data/
        Positioning/
        Spectrometer/
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.file = h5py.File(filename, 'r')
        self.data = self.file['Data']

    def close(self):
        """Close the HDF5 file."""
        if self.file:
            self.file.close()
            self.file = None

    def get_time(self) -> np.ndarray:
        """Return measurement times as numpy datetime64 array."""
        epoch = np.datetime64('1904-01-01T00:00:00')
        return epoch + self.data['Positioning']['TrueTime'][...].astype('timedelta64[s]')

    def get_object_positions(self) -> dict:
        """Return object positioning data as dict of arrays."""
        pos = self.data['Positioning']
        return {
            'Azimuth': pos['ObjectPosition']['Azimuth'][...],
            'Elevation': pos['ObjectPosition']['elevation'][...], # lowercase 'elevation' is a type in the original data!
            'CenterH': pos['ObjectOffset']['CenterH'][...],
            'CenterV': pos['ObjectOffset']['CenterV'][...],
            'TrueAzimuth': pos['TrueMeasurementPosition']['Azimuth'][...],
            'TrueElevation': pos['TrueMeasurementPosition']['Elevation'][...],
        }

    def get_spectrometer_metadata(self) -> dict:
        """Return spectrometer metadata."""
        spec = self.data['Spectrometer']
        return {
            'IQRate': spec['IQRate'][()],
            'CarrierFrequency': spec['CarrierFrequency'][()],
            'Gain': spec['Gain'][()],
            'N_FFT': spec['N_FFT'][()],
            'N_AVG': spec['N_AVG'][()],
            'Window': spec['Window'][()],
            't_int_ms': spec['t_int_ms'][()]
        }

    def get_power_spectrum(self) -> np.ndarray:
        """
        Return BasebandPowerSpectrum as a 2D numpy array:
        shape = (n_measurements, spectrum_length)
        """
        spec_data = self.data['Spectrometer']['BasebandPowerSpectrum']
        return np.array([row.byteswap() for row in spec_data])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()


CARRIER_FREQ = 1.4204e9 # Hz
SPECTROMETER_STEPSIZE = 3906 # Hz
SPECTROMETER_FREQUENCIES = CARRIER_FREQ + SPECTROMETER_STEPSIZE * np.arange(-256,256)
SPECTROMETER_XTICKS = (CARRIER_FREQ + SPECTROMETER_STEPSIZE * np.arange(-256,257))[::64]/1e6