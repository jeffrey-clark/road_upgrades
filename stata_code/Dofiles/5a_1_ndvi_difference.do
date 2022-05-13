* Make the NDVI difference

use "$Datasets/grid_cells_prioritization.dta", clear

foreach year of numlist 2011 (1) 2022{
local prev_year =`year'-1	
gen ndvi_diff_`year' = ndvi_`year'_02 - ndvi_`prev_year'_12

gen rainfall_avg_`year' = (rainfall_`year'_02 + rainfall_`prev_year'_12)*0.5

}


* diff 2021 is not good to use, because we have road work taking place during May 2020 - July 2021

save "$Datasets/grid_cells_prioritization_diff.dta", replace