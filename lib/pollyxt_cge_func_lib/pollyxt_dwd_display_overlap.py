import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.dates import DateFormatter, DayLocator, HourLocator, MinuteLocator, date2num
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os, sys
import scipy.io as spio
import numpy as np
from datetime import datetime, timedelta

def parse_polly_filename(pollyFile):
    import re

    psFmt = r"^(\d{4})_(\d{2})_(\d{2}).*_(\d{2})_(\d{2})_(\d{2})*.*"
    items = re.search(psFmt, pollyFile)

    return datetime(int(items[1]), int(items[2]), int(items[3]), int(items[4]), int(items[5]), int(items[6]))

def celltolist(xtickstr):
    tmp = []
    for iElement in range(0, len(xtickstr)):
        if not len(xtickstr[iElement][0]):
            tmp.append('')
        else:
            tmp.append(xtickstr[iElement][0][0])

    return tmp

def datenum_to_datetime(datenum):
    """
    Convert Matlab datenum into Python datetime.
    :param datenum: Date in datenum format
    :return:        Datetime object corresponding to datenum.
    """
    days = datenum % 1
    hours = days % 1 * 24
    minutes = hours % 1 * 60
    seconds = minutes % 1 * 60
    return datetime.fromordinal(int(datenum)) \
           + timedelta(days=int(days)) \
           + timedelta(hours=int(hours)) \
           + timedelta(minutes=int(minutes)) \
           + timedelta(seconds=round(seconds)) \
            - timedelta(days=366)

def rmext(filename):
    file, _ = os.path.splitext(filename)
    return file

def pollyxt_dwd_display_overlap(tmpFile, saveFolder):
    '''
    Description
    -----------
    Display the housekeeping data from laserlogbook file.

    Parameters
    ----------
    - tmpFile: the .mat file which stores the housekeeping data.

    Return
    ------ 

    Usage
    -----
    pollyxt_dwd_display_overlap(tmpFile)

    History
    -------
    2019-01-10. First edition by Zhenping

    Copyright
    ---------
    Ground-based Remote Sensing (TROPOS)
    '''

    if not os.path.exists(tmpFile):
        print('{filename} does not exists.'.format(filename=tmpFile))
        return
    
    # read data
    try:
        mat = spio.loadmat(tmpFile, struct_as_record=True)
        figDPI = mat['figDPI'][0][0]
        overlap532 = mat['overlap532'].reshape(-1)
        overlap532Defaults = mat['overlap532Defaults'].reshape(-1)
        sig532FR = mat['sig532FR'].reshape(-1)
        sig532NR = mat['sig532NR'].reshape(-1)
        sig532Gl = mat['sig532Gl'].reshape(-1)
        sigRatio532 = mat['sigRatio532'].reshape(-1)
        normRange532 = mat['normRange532'].reshape(-1)
        height = mat['height'].reshape(-1)
        pollyVersion = mat['campaignInfo']['name'][0][0][0]
        location = mat['campaignInfo']['location'][0][0][0]
        version = mat['processInfo']['programVersion'][0][0][0]
        dataFilename = mat['taskInfo']['dataFilename'][0][0][0]
    except Exception as e:
        print('Failed reading %s' % (tmpFile))
        return

    # display
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 8), sharey=True, gridspec_kw={'width_ratios': [1, 1]}, )

    # display signal
    p1, = ax1.plot(overlap532, height, color='#58B13F', linestyle='-', label=r'overlap 532 FR')
    p2, = ax1.plot(overlap532Defaults, height, color='#58B13F', linestyle='--', label=r'default overlap 532 FR')
    ax1.set_ylim([0, 3000])
    ax1.set_xlim([-0.05, 1.1])
    ax1.set_ylabel('Height (m)', fontweight='semibold', fontsize=15)
    ax1.set_xlabel('Overlap', fontweight='semibold', fontsize=15)
    ax1.tick_params(axis='both', which='major', labelsize=15, right=True, top=True, width=2, length=5)
    ax1.tick_params(axis='both', which='minor', width=1.5, length=3.5, right=True, top=True)
    ax1.grid(True)
    ax1.yaxis.set_major_locator(MultipleLocator(500))
    ax1.yaxis.set_minor_locator(MultipleLocator(100))
    start = parse_polly_filename(dataFilename)
    fig.text(0.5, 0.98, 'Overlap for {instrument} at {location}, {time}'.format(instrument=pollyVersion, location=location, time=start.strftime('%Y%m%d %H:%M')), horizontalalignment='center', fontweight='bold', fontsize=15)
    l = ax1.legend(handles=[p1, p2], loc='upper left', fontsize=15)

    sig532FR = np.ma.masked_where(sig532FR <= 0, sig532FR)
    sig532NR = np.ma.masked_where(sig532NR <= 0, sig532NR)
    sig532Gl = np.ma.masked_where(sig532Gl <= 0, sig532Gl)
    p1, = ax2.semilogx(sig532FR, height, color='#58B13F', linestyle='-.', label=r'FR 532')
    p2, = ax2.semilogx(sig532NR, height, color='#58B13F', linestyle=':', label=r'NR 532')
    p3, = ax2.semilogx(sig532Gl, height, color='#58B13F', linestyle='-', label=r'FR Glued 532')

    if normRange532.size != 0:
        ax2.plot([1e-10, 1e10], [height[normRange532[0] - 1], height[normRange532[0] - 1]], linestyle='--', color='#58B13F')
        ax2.plot([1e-10, 1e10], [height[normRange532[-1] - 1], height[normRange532[-1] - 1]], linestyle='--', color='#58B13F')
    
    ax2.set_xlim([1e-2, 1e3])
    ax2.set_xlabel('Signal [MHz]', fontweight='semibold', fontsize=15)
    ax2.tick_params(axis='both', which='major', labelsize=15, right=True, top=True, width=2, length=5)
    ax2.tick_params(axis='both', which='minor', width=1.5, length=3.5, right=True, top=True)
    ax2.grid(True)
    l = ax2.legend(handles=[p1, p2, p3], loc='upper right', fontsize=15)

    fig.text(0.87, 0.02, 'Version {version}'.format(version=version), fontsize=15)

    fig.savefig(os.path.join(saveFolder, '{dataFilename}_overlap.png'.format(dataFilename=rmext(dataFilename))), bbox_inches='tight', dpi=figDPI)
 
    plt.close()

def main():
    pollyxt_dwd_display_overlap('C:\\Users\\zhenping\\Desktop\\Picasso\\tmp\\tmp.mat', 'C:\\Users\\zhenping\\Desktop')

if __name__ == '__main__':
    # main()
    pollyxt_dwd_display_overlap(sys.argv[1], sys.argv[2])