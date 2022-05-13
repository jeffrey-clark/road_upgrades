* Make the necessary changes in order to send Tillmann the file

* use merge roads and cells
use "$Datasets/grid_cells_cleaned.dta", clear

*** CLEAN THE DATA ***

* drop variables that we don't want Tillmann to see
drop subroad_id row_id road_id
*drop road_id
drop sr_length_km r_pct_upgraded

drop width height


*** RENAME VARIABLES *** 
/*
foreach var of varlist *_check {
      if "`var'" == "total_check" {
        continue
      }
			local no_check_var = subinstr("`var'","_check", "", .)
			dis "checking `no_check_var'"
			//compare `var' `no_check_var'
			replace check_disc = 1 if `var' != `no_check_var'
      replace check_disc_vars = check_disc_vars + ", `var'" if `var' != `no_check_var' & check_disc_vars != ""
      replace check_disc_vars = "`var'" if `var' != `no_check_var' & check_disc_vars == ""

	}
*/


** VARIABLES NOT TO PETURB
local skip_peturb upgraded upgrade_type treatment rnd_road_id id

dis "`skip_peturb'"

foreach var of varlist * {
	
	* skip the variable concat
	if "`var'" == "concat"{
	    continue
	}
	
	* check var is in skip_peturb
	local subset : list var in skip_peturb
	if `subset' == 1{
		rename `var' keepCat_`var'
		continue
	}
	
	* rename variables according to numeric or categorical nature
	capture confirm string variable `var'
		if !_rc {
			rename `var' keepCat_`var'
		}
		else {
		   rename `var' keepCont_`var'
		}
	}

drop if concat == ""

// SAVING AND EXPORT DONE IN MASTERDOFILE "CREATE_PRE_JITTER"	
* export excel file to Resources
//export excel "$Exports/share_latest.xlsx", firstrow(variables) replace
//save "$Exports/share_latest.dta", replace