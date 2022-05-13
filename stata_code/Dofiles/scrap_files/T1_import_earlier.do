* Import roads
import excel "$Resources/roads_2017_2018_05_07.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_05_07.dta", replace

* Import roads
import excel "$Resources/roads_2018_2019_05_07.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2018_2019_05_07.dta", replace

* Import roads
import excel "$Resources/roads_2019_2020_05_07.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2019_2020_05_07.dta", replace

use "$Datasets/roads_2017_2018_05_07.dta", clear

append using "$Datasets/roads_2018_2019_05_07.dta" "$Datasets/roads_2019_2020_05_07.dta", generate(year)
replace year = 2017 if year == 0
replace year = 2018 if year == 1
replace year = 2019 if year == 2

drop if upgraded == 0

drop if upgrade_type == "paving"

duplicates drop road_id subroad_id, force
save "$Datasets/upgrades_prior.dta", replace 


* Import the id to concat table
import excel "$Resources/id_concat_table.xlsx", firstrow case(lower) clear
save "$Datasets/id_concat_table.dta", replace

* Merge the concat value into the roads data set
use "$Datasets/upgrades_prior.dta", clear
merge m:1 road_id using "$Datasets/id_concat_table.dta"
drop _merge
save "$Datasets/upgrades_prior.dta", replace

* Import cells
import excel "$Resources/GEE_grids_03_05.xlsx" , firstrow case(lower) clear
save "$Datasets/grid_cells.dta", replace

* merge roads and cells

use "$Datasets/grid_cells.dta", clear

* Merge info on upgrade status
merge m:1 road_id subroad_id using "$Datasets/upgrades_prior.dta", keepusing(upgraded upgrade_type length_km concat)
rename _merge merge_upgraded

* Drop the observations shorter than one km
drop if region != "test_grids"

order error concat, last

save "$Datasets/grid_cells_merged.dta", replace

use "$Datasets/grid_cells_merged.dta", clear




