
* use merge roads and cells
use "$Datasets/grid_cells_prioritization_diff.dta", clear

reshape long ndvi_diff_ rainfall_avg_, i(id) j(year) 


rename ndvi_diff_ ndvi
rename rainfall_avg_ rainfall
order year, before(ndvi)

save "$Datasets/grid_cells_prioritization_diff_reshape.dta", replace