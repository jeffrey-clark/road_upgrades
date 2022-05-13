
* Import the base
import excel "$Gridcell_dir/grid_cells_01_02.xlsx" , firstrow case(lower) clear
drop ndvi_* error region
save "$Datasets/grid_cells.dta", replace


local filelist: dir "$Gridcell_dir" files "*.xlsx"
dis `filelist'


foreach file of local filelist {
	* extract the month from the filename
	local month =substr("`file'", 15, 2)	
	dis "`file'"
	
	* import the excel file
	import excel "$Gridcell_dir/`file'" , firstrow case(lower) clear
	keep ndvi_* rainfall_* road_id subroad_id row_id
	
	* rename the ndvi variables
	foreach var of varlist ndvi_* {
		rename `var' `var'_`month'
	}
	
	* rename the rainfall variables
	foreach var of varlist rainfall_* {
		rename `var' `var'_`month'
	}
	
	merge 1:1 road_id subroad_id row_id using "$Datasets/grid_cells.dta"
	drop _merge
	save "$Datasets/grid_cells.dta", replace	
}


local ndvi_vars ""

foreach year of numlist 2010 (1) 2022{
	
	foreach month of numlist 2 (2) 12 {
	  if length("`month'") == 1 local month 0`month'
	  di "`year' `month'"
	  local ndvi_vars `ndvi_vars' ndvi_`year'_`month'
	}
}

order `ndvi_vars', last

drop ndvi_2022_04 ndvi_2022_06 ndvi_2022_08 ndvi_2022_10 ndvi_2022_12
drop rainfall_2022_04 rainfall_2022_06 rainfall_2022_08 rainfall_2022_10 rainfall_2022_12

* Convert rainfall in meter to millimeters
foreach var of varlist rainfall* {
	
	replace `var' = `var'*1000

}

save "$Datasets/grid_cells.dta", replace