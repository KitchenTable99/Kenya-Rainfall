# Sub-Saharan Rainfall Analysis
Does drought in one year cause an increase in births in the next year? If so, this can be very closely mapped to transactional sex in Sub-Saharan Africa.

## Goals of Program
1. Parse gloabl precipitation data to create a rolling window against which the drought status will later be calculated.
2. Using a 30-year rolling window, fit a gamma distribution to the rainfall data and determine drought status of each year (5%-ile,  10%-ile, 15%-ile, No Drought)
3. Parse health surveys relating to female and their birth rates to identify births immediately following a drought year.
4. Combine health data with precipitation data and perform hazard regressions to obtain statistical significance.