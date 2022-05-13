* merge roads and cells

use "$Datasets/grid_cells.dta", clear

* Merge info on upgrade status
merge m:1 road_id subroad_id using "$Datasets/roads.dta", keepusing(rnd_road_id upgraded r_pct_upgraded sr_length_km r_length_km last_upgrade concat province district)
rename _merge merge_upgraded

* Drop the observations shorter than one km
drop if row_id == . 

order concat, last

drop if merge_upgraded != 3
save "$Datasets/grid_cells_merged.dta", replace

use "$Datasets/grid_cells_merged.dta", clear