# Kenya-Rainfall
## Required Libraries
* os
* re
* time
* tqdm
* argparse
* geopandas
* itertools
* shapely.geometry

### Notes
* All rainfall data analysis is meant to be carried out with the provided precip_data folder. Should additional files be required or a certain file no longer be needed, check  file_parsers.precipFileParser() to make sure that it works with the new format. Every time the function is called with return_coords=True, it is hard coded. This might need to be changed.