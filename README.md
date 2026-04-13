# cmems_ocean_tide
An autoprocessing of ocean tide data from the Marine Copernicus global dataset ([GLOBAL_ANALYSISFORECAST_PHY_001_024](https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description)) at a specific point ("longitude", "latitude"), hereafter referred to as a fishing port, at the corresponding time range. 

**Data Source**
- dataset_id : "cmems_mod_glo_phy_anfc_merged-sl_PT1H-i"
- variables: "Sea surface height above geoid due to ocean tide"
- names: "ocean_tide"

**Workflow**

(1) load and filter fishing port type 

(2) Fetches tidal data

- Load data from Copernicus Marine using the port's specific longitude and latitude at the corresponding time range.
- Converts tidal data into a pandas DataFrame.
- Localizes the time to the corresponding Indonesia time zone > GMT+7 (Asia/Jakarta), GMT+8 (Asia/Makassar), GMT+9 (Asia/Jayapura)
    
(3) Saves data to a CSV file, dynamically naming them based on the port's type and name.

(4) Make a timeseries graph of tidal data based on local_time, dynamically naming them based on the port's type and name.

**Credentials** 

To access all Copernicus Marine Data Store services, first, you should create a configuration file called `.copernicusmarine-credentials`. By default, this file is saved in the user’s home directory. The `login` function allows you to save credentials and needs to be run only once. Then you can use the remaining functionality without having to specify your credentials again.

    copernicusmarine.login(username='<your_username>', password='<your_password>')

** TIde Plot**
<img width="1200" height="600" alt="715_72_21_PPI_Paranggi" src="https://github.com/user-attachments/assets/5d445531-63ee-4c3d-84f4-37a8fdc6b15e" />
