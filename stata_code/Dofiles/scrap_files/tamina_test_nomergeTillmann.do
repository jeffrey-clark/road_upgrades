use "$Datasets/grid_cells_cleaned.dta", clear

* Make the NDVI difference

foreach year of numlist 2011 (1) 2022{
local prev_year =`year'-1	
gen ndvi_diff_`year' = ndvi_`year'_02 - ndvi_`prev_year'_12
}

* diff 2021 is not good to use, because we have road work taking place during May 2020 - July 2021

save "$Datasets/tamina_test_grid_cells_prioritization_diff.dta", replace

* use merge roads and cells
use "$Datasets/tamina_test_grid_cells_prioritization_diff.dta", clear

reshape long ndvi_diff_, i(id) j(year) 


rename ndvi_diff_ ndvi
order year, before(ndvi)

save "$Datasets/tamina_test_grid_cells_prioritization_diff_reshape.dta", replace

use "$Datasets/tamina_test_grid_cells_prioritization_diff_reshape.dta", clear

* Minimum score is -35.2, maximum score is 27.3 (update plz)

* Generate pre and post periods, here 2016-2019 are pre periods and 2022 post
* We will exclude year 2021 from the analysis, as upgrade takes place during that time.

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

* Declare data set as panel data
xtset id year

drop if year < 2017


* Regressions, for these regressions we excluded year 2021 as upgrades would take place then. 
* "Naive regression"
xtreg ndvi treatment post did if year != 2021

* Naive + cluster standard errors on road level
xtreg ndvi treatment post did if year != 2021, cluster(road_id) 
*outreg2 using Seminar_March.doc

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if year != 2021, fe cluster(road_id) 
*outreg2 using Seminar_March.doc

*Fixed effects + cluster standard errors + year fixed effects
xtreg ndvi treatment post did i.year if year != 2021, fe cluster(road_id) 
*outreg2 using Seminar_March.doc