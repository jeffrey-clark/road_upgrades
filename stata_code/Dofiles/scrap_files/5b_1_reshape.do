use "$Datasets/grid_cells_prioritization.dta", clear

foreach var of varlist ndvi_* {
	local year =substr("`var'",6,4)
	local month =substr("`var'",11,2)
		rename `var' ndvi_`year'`month'
	}

reshape long ndvi_, i(id) j(year) 

tostring year, replace

rename year date

gen month =substr(date,5,2)
gen year =substr(date,1,4)

destring year month, replace

order month, after(year)

rename ndvi_ ndvi

save "$Datasets/grid_cells_prioritization_abs_reshape.dta", replace