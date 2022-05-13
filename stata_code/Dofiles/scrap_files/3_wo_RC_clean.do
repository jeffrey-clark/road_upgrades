*-------------------------------------------------------------------------------
* What this file does: 
* Deletes paving upgrades on subroad level
* Calculates percentage road upgrades on road level
* Cleans the data from intermediary variables and observations not defined as control nor treatment	 	  
* Reshapes the file into long formay      
*		 		
*---------------------------------------------------------------------

* load the dataset
use "$Datasets/grid_cells_merged.dta", clear

* rename som variables, and drop unnecessary
rename length_km sr_length_km
drop merge_upgraded

* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

//tab road_id if upgraded == 1

* Get road length: we want to look at road_id and subroad_id and sum the length of unique subroad_ids for each road 
sort road_id
by road_id: replace sr_length_km = . if row_id != 0  // remove repeated lengths
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded row_id 
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

*Clean the data from intermediary variables we created
drop r_length_upgrade
drop sr_length_upgraded
by road_id: replace sr_length_km = sr_length_km[1] // restore removed sr lengths


* order the road length variables nicely, generate additional variables
gen sr_length_pct = sr_length_km / r_length_km


order sr_length_pct r_length_km r_pct_upgraded, after(sr_length_km)

tab road_id if r_pct_upgraded > 0 
tab road_id if r_pct_upgraded > 0 & r_pct_upgraded < 0.90

*Clean the data from ambiguities: drop all observations that have r_pct_upgrade larger than zero but smaller than 90 %. This is the same as dropping the whole road: 8, 14, 27, 34, 64, 86, 110, 126
tab r_pct_upgraded
drop if r_pct_upgraded > 0 & r_pct_upgraded < 0.90


*Define treatment and control groups
gen treatment = 0
replace treatment = 1 if r_pct_upgraded >= 0.90

*Generate unique identifyers for the data
gen id = _n
order id, after(region)
order upgraded upgrade_type treatment error concat, last



save "$Datasets/grid_cells_cleaned.dta", replace
use "$Datasets/grid_cells_cleaned.dta", clear



