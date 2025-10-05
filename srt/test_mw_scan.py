import srt_util
import numpy as np
import math as m
import matplotlib.pyplot as plt

with srt_util.SRT_HDF_Reader('Measurements/MilkyWay1dScan/MilkyWayScan_T2200_G350to190_Stp0deg25_20251002.hdf') as srt_reader:
    mw_pos = srt_reader.get_object_positions()
    mw_spec = srt_reader.get_power_spectrum()
    

def plot_mw_scan_spectra(spec, x_vals, label, scale = 1):
    minmax_x = (min(x_vals), max(x_vals))

    minmax_freq = (srt_util.MINMAX_FREQ[0] / scale , srt_util.MINMAX_FREQ[1] / scale)

    im = plt.imshow(spec.T, extent=(*minmax_x, *minmax_freq), origin='lower', aspect='auto')
    

    cbar = plt.colorbar(im)
    cbar.set_label(label)

    plt.ylim(minmax_freq)
    plt.yticks(srt_util.SPECTROMETER_TICKS/scale)
    
plot_mw_scan_spectra(mw_spec, 360.0-mw_pos['CenterH'],'Spectral power density [a.u./Hz]', 1e6) # Galactic longitudes are wrong in LabView tool. 270° should be 90°. Therfore correct is l = 360°-l_labview
plt.show()