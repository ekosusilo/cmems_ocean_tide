# ---------------------------------------------------------------------------
# Ocean Tidal Data Processing
# The primary objective is to process tide data from Marine Copernicus global 
# dataset for each fishing port point ("longitude", "lattitude") at 
# the corresponding time range (7 days a head) 
#
# Data Source
# dataset_id : "cmems_mod_glo_phy_anfc_merged-sl_PT1H-i"
# variables  : "Sea surface height above geoid due to ocean tide"
# names      : "ocean_tide"
#
# Workflow
# (1) load and filter fishing port type 
# (2) Fetches tidal data
#     (a) Load data from Copernicus Marine using the port's specific longitude 
#         and latitude at the corresponding time range.
#     (b) Converts tidal data into a pandas DataFrame.
#     (c) Localizes the time to Indonesia time
#         GMT+7 (Asia/Jakarta), GMT+8 (Asia/Makassar), GMT+9 (Asia/Jayapura)
# (3) Saves data to a CSV file, 
#     dynamically naming them based on the port's id, type and name.
# (4) Make timeseries graph of tidal data based on local_time, 
#     dynamically naming them based on the port's id, type and name.
# ---------------------------------------------------------------------------



# -------------------------
# General Configuration
# -------------------------

# --- import packages
import os
import pandas as pd
import numpy as np
import copernicusmarine
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime, timedelta, timezone


# -- set working directory
workdir = "your_working_directory_path"


# -------------------------
# Define Function  
# -------------------------
# function >> plot_ocean_tide
# ===========================
def plot_data(data, 
              filename,
              metadata):
    '''
    Generate time series tidal graph 

    Parameters:
    ----------
    data (str):
      Time-series tide data.
    filename (str):
      The output filename.
    metadata (dict):
      A dictionary containing the some port properties.
    '''
    
    # Generate plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['time_local'], data['ocean_tide'],
             color='red', linestyle='-', linewidth=2, alpha=0.7)

    # Plot properties
    # Format title and axis label 
    ax.set_title(f"{metadata['type']} {metadata['name']}")
    ax.set_xlabel(f"Waktu ({metadata['tz']})")
    ax.set_ylabel('Ketinggian Air (m)')
    plt.xticks(rotation=45, ha='right')

    # Add major & minor ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M:%S'))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.grid(which='minor', linestyle=':', alpha=0.5)

    # Set x-axis limits based on data
    ax.set_xlim(data['time_local'].min(), data['time_local'].max())

    # save plot
    plt.tight_layout()
    if filename:
        plt.savefig(filename)
    
    plt.close(fig)   


# function >> fetch_tidal_data
# ============================
def fetch_data(metadata):
    """
    Fetch tidal data for a list of fishing ports and save results to CSV files.

    Parameters:
      metadata (dict):
        A dictionary containing the following keys:
        - 'id' (str): ID of the fishing port.
        - 'type' (str): Type of the fishing port.
        - 'name' (str): Name of the fishing port.
        - 'tz' (str): Indonesia local time zone (e.g., 'wib', 'wita', 'wit').
        - 'lon' (float): Longitude coordinate of the fishing port.
        - 'lat' (float): Latitude coordinate of the fishing port.
        - 'start' (datetime): Start datetime reference - 1.
        - 'stop' (datetime): Stop datetime reference + 7.
    """

    # show message
    try:
        # Step 1: Define timezone and datetime strings
        if metadata['tz'] == "wib":
            time_zone = "Asia/Jakarta"
            start_dt_str = metadata['start'].strftime("%Y-%m-%dT17:00:00")
            stop_dt_str  = metadata['stop'].strftime("%Y-%m-%dT16:00:00")
        elif metadata['tz'] == "wita":
            time_zone = "Asia/Makassar"
            start_dt_str = metadata['start'].strftime("%Y-%m-%dT16:00:00")
            stop_dt_str  = metadata['stop'].strftime("%Y-%m-%dT15:00:00")
        else:
            time_zone = "Asia/Jayapura"
            start_dt_str = metadata['start'].strftime("%Y-%m-%dT15:00:00")
            stop_dt_str  = metadata['stop'].strftime("%Y-%m-%dT14:00:00")

        # Step 2: Acquire data from Copernicus Marine
        da = copernicusmarine.open_dataset(
            dataset_id        = "cmems_mod_glo_phy_anfc_merged-sl_PT1H-i",
            minimum_longitude = metadata['lon'],
            maximum_longitude = metadata['lon'],
            minimum_latitude  = metadata['lat'],
            maximum_latitude  = metadata['lat'],
            start_datetime    = start_dt_str,
            end_datetime      = stop_dt_str,
            variables         = ["ocean_tide"]
        )

        # Step 3: Convert to DataFrame
        df = da.to_dataframe().reset_index()
        df = df[['time', 'ocean_tide']].copy()

        # Step 4: Timezone conversion
        try:
            df['time'] = df['time'].dt.tz_localize('UTC')
        except TypeError:
            pass  # Already tz-aware

        df['time_local'] = df['time'].dt.tz_convert(time_zone)

        df = df[['time', 'time_local', 'ocean_tide']].rename(
            columns={'time': 'time_utc'}
        )
        df['time_utc']   = df['time_utc'].dt.tz_localize(None)
        df['time_local'] = df['time_local'].dt.tz_localize(None)

    except Exception as e:
        print(f"  Error processing: {e}")

    return(df)        


# -------------------------------
# Main Workflow
# -------------------------------

# -- load fishing port dataset
port_df_filtered = pd.read_csv(
    os.path.join(workdir, "fishing_port.csv"), 
    delimiter=";"
).query("jenis_pelabuhan in ['PPS','PPN','PPP','PPI']")


# -- test by using single point
port_df_filtered = port_df_filtered.iloc[[100]]


# -- set time range, by system or type manually single date
today = datetime.now()
# today = datetime.strptime('2026-01-01', "%Y-%m-%d")


def main():
    for index, port_data in port_df_filtered.iterrows():
      # set metadata
      metadata = {
        "id"    : port_data['kode_pelabuhan'],
        "type"  : port_data['jenis_pelabuhan'],
        "name"  : port_data['nama_pelabuhan'],
        "tz"    : port_data['tz'],
        "lon"   : port_data['lon'],
        "lat"   : port_data['lat'],
        "start" : today + timedelta(days=-1),
        "stop"  : today + timedelta(days=7)
        }
      
      # set output name dan path
      basename = f"{metadata['id']} {metadata['type']} {metadata['name']}"
      csv_name = f"{basename.replace(' ', '_')}.csv"
      png_name = f"{basename.replace(' ', '_')}.png"
      png_path = os.path.join(workdir, png_name)
      csv_path = os.path.join(workdir, csv_name)

      # data processing
      print(f"Process >>> {basename}")
      print(f"✅ fetch data")
      tide = fetch_data(metadata)
  
      print(f"✅ save to csv")  
      tide.to_csv(csv_path, index=False)
  
      print(f"✅ create plot")
      plot_data(tide, png_path, metadata)
      
      print("\n")    
    
    
# -------------------------------
if __name__ == '__main__':
    main()
# -------------------------------
