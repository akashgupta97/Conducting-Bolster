# -*- coding: utf-8 -*-
import sys,os
import numpy as np
import pandas as pd
import h5py
import math
import linecache
from datetime import datetime, timedelta, time
from collections import Counter
    
# Calibrate data given the calibration parameters saved using GGIR
def calibrate(x, y, z, temperature, calib_df):
    mean_temp = np.mean(temperature)
    temp = temperature - mean_temp
    cx = (x * calib_df['scale'][0]) + calib_df['offset'][0] + (temp * calib_df['tempoffset'][0])
    cy = (y * calib_df['scale'][1]) + calib_df['offset'][1] + (temp * calib_df['tempoffset'][1])
    cz = (z * calib_df['scale'][2]) + calib_df['offset'][2] + (temp * calib_df['tempoffset'][2])
    return cx,cy,cz

def nonwear_bouts(pd_datetime, nonwear_df):
    # Determine non-wear bouts
    nonwear_df['datetime'] = [datetime.strptime(dt,'%Y-%m-%dT%H:%M:%S+0100') if dt.endswith('0100') \
                              else datetime.strptime(dt,'%Y-%m-%dT%H:%M:%S+0000') for dt in nonwear_df['timestamp']]
    nonwear_df['nonwear'] = False
    nonwear_df.loc[nonwear_df['nonwearscore'] >= 2,'nonwear'] = True
    
    # Get nonwear bouts
    num_nonwear = len(nonwear_df)
    nonwear_bout = []
    st_idx = -1; end_idx = -1
    if nonwear_df.loc[0,'nonwear'] == True:
        st_idx = 0
    for idx in range(num_nonwear-1):
        if nonwear_df.loc[idx,'nonwear'] == False and nonwear_df.loc[idx+1,'nonwear'] == True:
            st_idx = idx+1
        if nonwear_df.loc[idx,'nonwear'] == True and nonwear_df.loc[idx+1,'nonwear'] == False:
            end_idx = idx
            if end_idx >= st_idx and st_idx >= 0:
                nonwear_bout.append((st_idx,end_idx))
    
    # Maintain non-wear boolean for each timestamp
    # If nonwear score is true for two or more axes, set that epoch as nonwear
    nsamples = len(pd_datetime)
    np_nonwear = np.array([False]*nsamples)
    for st_idx, end_idx in nonwear_bout:
        start_timestamp = nonwear_df.loc[st_idx,'datetime']
        end_timestamp = nonwear_df.loc[end_idx,'datetime']
        np_nonwear[(pd_datetime >= start_timestamp) & (pd_datetime < end_timestamp)] = True
    
    return np_nonwear

def estimate_nonwear(timestamp, x, y, z, interval='900', th=0.013):
    df = pd.DataFrame(data={'timestamp':timestamp, 'x':x, 'y':y, 'z':z})
    df.set_index('timestamp', inplace=True)
    df_std = df.resample(str(interval)+'S').std()
    is_nonwear = [(sum([row.x < th, row.y < th, row.z <th]) >=2) for index, row in df_std.iterrows()]
    df_std['nonwear'] = is_nonwear
    
    nonwear_df = pd.DataFrame(data={'timestamp':timestamp})
    nonwear_df['nonwear'] = False
    intervals = list(df_std.index.values)
    df_std = df_std.reset_index()
    for index,ts in enumerate(intervals):
        if index < len(intervals)-1:
            nonwear_df.loc[(nonwear_df['timestamp'] >= intervals[index]) &\
                         (nonwear_df['timestamp'] < intervals[index+1]),\
                         'nonwear'] = df_std.iloc[index]['nonwear']
    nonwear_df.loc[nonwear_df['timestamp'] >= intervals[-1], 'nonwear'] = df_std.iloc[-1]['nonwear']
    return np.array(nonwear_df['nonwear'].values)
  
def get_sleep_states(lbl_data, pd_datetime, states):
    # Obtain bouts for each sleep state from label data
    num_lbl = len(lbl_data)
    states_categ = list(set(lbl_data['Event']))
    states_bout = []
    for state in states_categ:
        state_df = lbl_data[lbl_data['Event'] == state]
        start_idx = state_df.index
        end_idx = start_idx + 1
        start_idx = start_idx[start_idx < (num_lbl-1)]
        end_idx = end_idx[end_idx < num_lbl]
        if len(start_idx) == 0:
            continue
        start_time = [lbl_data.loc[0,'Start DateTime']]*len(start_idx)
        end_time = [lbl_data.loc[0,'Start DateTime']]*len(start_idx)
        j = 0
        start_time[j] = lbl_data.loc[start_idx[j],'Start DateTime']
        if len(start_idx) > 1:
            for i in range(len(start_idx)-1):
                if end_idx[i] != start_idx[i+1]:
                    end_time[j] = lbl_data.loc[end_idx[i],'Start DateTime']
                    j += 1
                    start_time[j] = lbl_data.loc[start_idx[i+1],'Start DateTime']
        else:
            end_time[j] = lbl_data.loc[end_idx[j],'Start DateTime']
            j += 1
        start_time = start_time[:j]
        end_time = end_time[:j]
        states_bout.append((state, start_time, end_time))
             
    # Get sleep state for each timestamp if available
    valid_states = states[(pd_datetime >= lbl_data.loc[0,'Start DateTime']) & \
                          (pd_datetime < lbl_data.loc[num_lbl-1,'Start DateTime'])]
    valid_datetime = pd_datetime[(pd_datetime >= lbl_data.loc[0,'Start DateTime']) & \
                          (pd_datetime < lbl_data.loc[num_lbl-1,'Start DateTime'])]
    for state, start_time, end_time in states_bout:
        for idx in range(len(start_time)):
            valid_states[(valid_datetime >= start_time[idx]) & (valid_datetime < end_time[idx])] = state
    states.update(valid_states)
    
    return states

def save_output(out_fname, params):
    hf = h5py.File(out_fname,'w')
    for paramStr, paramData in params:
        if paramStr == 'DateTime':
            paramData = np.array([dt.strftime('%Y-%m-%d %H:%M:%S.%f').encode('utf8') for dt in paramData])
        elif paramStr == 'SleepState':
            paramData = [st.encode('utf8') for st in paramData]   
        hf.create_dataset(paramStr, data=paramData)
    hf.close()
    
# Extract calibrated accelerometer data, light & temperature data, 
# nonwear status and sleep state labels for every timestamp    
def preproc_amc(data_fname=None, lbl_fnames=None, calib_fname=None, \
                    nonwear_fname=None, out_fname=None):
    if data_fname is None or lbl_fnames is None or calib_fname is None \
            or nonwear_fname is None or out_fname is None:
        print('Invalid input/output files')
        return

    # Read data file
    print('... Loading data')
    fh = h5py.File(data_fname, 'r')
    #print(list(fh.keys()))

    # Extract data info
    x = np.array(fh['X'])
    y = np.array(fh['Y'])
    z = np.array(fh['Z'])
    light = np.array(fh['light'])
    button = np.array(fh['button'])
    temp = np.array(fh['temp'])
    timestamp = pd.Series(fh['timestamp']).apply(lambda x: x.decode('utf8'))
    timestamp = pd.to_datetime(timestamp, format='%Y-%m-%d %H:%M:%S.%f')
    nsamples = len(x)
    print('... Preprocessing %d samples' % nsamples)

    # Perform auto-calibration
    print('... Calibrating data')
    calib_df = pd.read_csv(calib_fname, sep='\t')
    cx, cy, cz = calibrate(x, y, z, temp, calib_df)

    # Perform flipping x and y axes to ensure standard orientation
    # For correct orientation, x-angle should be mostly negative
    # So, if median x-angle is positive, flip both x and y axes
    # Ref: https://github.com/wadpac/hsmm4acc/blob/524743744068e83f468a4e217dde745048a625fd/UKMovementSensing/prepacc.py
    angx = np.arctan2(cx, np.sqrt(cy*cy + cz*cz)) * 180.0/math.pi
    if np.median(angx) > 0:
        cx *= -1
        cy *= -1
 
    # Determine non-wear bouts
    print('... Determining nonwear bouts')
    nonwear_df = pd.read_csv(nonwear_fname, sep='\t')
    #np_nonwear = nonwear_bouts(timestamp, nonwear_df)
    np_nonwear = estimate_nonwear(timestamp, cx, cy, cz)
    
    # Read label file
    # Get sleep states for each timestamp / align each timestamp with labels if available
    nsamples = len(timestamp)
    states = pd.Series(['NaN']*nsamples)
    print('... Getting sleep states')
    for fname in lbl_fnames:
        lbl_data = pd.read_csv(fname, skiprows=9, sep=',', header=None)
        lbl_data.columns = ['Date','Time','Event']
        num_lbl = len(lbl_data)
        # Combine date and time
        if len(lbl_data.loc[0,'Date']) == 9:
            lbl_data['Date'] = lbl_data['Date'].apply(lambda x: datetime.strptime(x,'%d-%b-%y').date())
        else:
            lbl_data['Date'] = lbl_data['Date'].apply(lambda x: datetime.strptime(x,'%d-%b-%Y').date())
        lbl_data['Time'] = lbl_data['Time'].apply(lambda x: datetime.strptime(x,'%H:%M:%S').time())
        for idx in range(num_lbl):
            lbl_data.loc[idx,'Start DateTime'] = datetime.combine(lbl_data.loc[idx,'Date'], lbl_data.loc[idx,'Time'])
    
        states = get_sleep_states(lbl_data, timestamp, states)
    print(Counter(states))
    
    # Save data and labels to output file
    print('... Saving data')
    params = [('DateTime', timestamp),('X', cx),('Y', cy),('Z', cz), \
              ('Light', light), ('Temperature', temp), ('Button', button), \
              ('Nonwear', np_nonwear), ('SleepState', states)]
    save_output(out_fname, params)    
    
def main(argv):
    indir = argv[0]  
    lbldir = argv[1]
    basedir = argv[2]

    calibdir = os.path.join(basedir,'calib_param')
    nonweardir = os.path.join(basedir,'nonwear')
    outdir = os.path.join(basedir,'preprocessed')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    data_files = os.listdir(indir)
    lbl_files = os.listdir(lbldir)
    for data_fname in data_files:
        if os.path.exists(os.path.join(outdir,data_fname)):
            continue
        user = '_'.join(part for part in data_fname.split('_')[0:2])
        print('Processing ' + data_fname)
        lbl_fnames = [fname for fname in lbl_files if fname.startswith(user.lower())]
        calib_fname = data_fname.split('.h5')[0] + '.csv'
        nonwear_fname = data_fname.split('.h5')[0] + '.csv'
        preproc_amc(os.path.join(indir,data_fname), [os.path.join(lbldir,fname) for fname in lbl_fnames], \
                        os.path.join(calibdir,calib_fname), os.path.join(nonweardir,nonwear_fname), \
                        os.path.join(outdir,data_fname))
        #break
        
if __name__ == "__main__":
    main(sys.argv[1:])
