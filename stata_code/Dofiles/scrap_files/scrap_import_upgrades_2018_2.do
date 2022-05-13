local prev_year 2017
local year 2018
dis `prev_year'

* Import roads
import excel "$Resources/roads_`prev_year'_`year'_04_06.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_`prev_year'_`year'_04_06.dta", replace

* Import roads
import excel "$Resources/roads_`prev_year'_`year'_05_07.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_`prev_year'_`year'_05_07.dta", replace

*Import roads

import excel "$Resources/roads_`prev_year'_`year'_06_08.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_`prev_year'_`year'_06_08.dta", replace

* Import roads
import excel "$Resources/roads_`prev_year'_`year'_07_09.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_`prev_year'_`year'_07_09.dta", replace

* Import roads
import excel "$Resources/roads_`prev_year'_`year'_08_10.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_`prev_year'_`year'_08_10.dta", replace


use "$Datasets/roads_`prev_year'_`year'_04_06.dta", clear
append using "$Datasets/roads_`prev_year'_`year'_05_07.dta" "$Datasets/roads_`prev_year'_`year'_06_08.dta" "$Datasets/roads_`prev_year'_`year'_07_09.dta" "$Datasets/roads_`prev_year'_`year'_08_10.dta"
save "$Datasets/roads_`year'.dta", replace

use "$Datasets/roads_`year'.dta", clear
