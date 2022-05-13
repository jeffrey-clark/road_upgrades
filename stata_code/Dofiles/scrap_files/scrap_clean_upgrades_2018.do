*-------------------------------------------------------------------------------
* What this file does: 
* Deletes paving upgrades on subroad level
* Calculates percentage road upgrades on road level
* Cleans the data from intermediary variables and observations not defined as control nor treatment	 	  
* Reshapes the file into long formay      
*		 		
*---------------------------------------------------------------------
local prev_year 2017
local year 2018
dis `prev_year'

* load the dataset
use "$Datasets/roads_`year'.dta", clear

* rename som variables, and drop unnecessary
rename length_km sr_length_km

* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* Rename period region
rename region month

replace month = "6" if month == "roads_`prev_year'_`year'_04_06"
replace month = "7" if month == "roads_`prev_year'_`year'_05_07"
replace month = "8" if month == "roads_`prev_year'_`year'_06_08"
replace month = "9" if month == "roads_`prev_year'_`year'_07_09"
replace month = "10" if month == "roads_`prev_year'_`year'_08_10" 

destring month, replace

sort road_id subroad_id month
* Get road length: we want to look at road_id and subroad_id and sum the length of unique subroad_ids for each road 
by road_id subroad_id: replace sr_length_km = . if month != 6  // remove repeated lengths
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Fill the subroad length again
sort road_id subroad_id month
by road_id subroad_id: replace sr_length_km = sr_length_km[1] 

preserve
* Get the upgraded segments
drop if upgraded == 0
duplicates drop road_id subroad_id, force
*collapse upgraded, by(road_id subroad_id r_length_km sr_length_km)
by road_id: egen r_length_upgraded = total(sr_length_km)
gen r_pct_upgraded = r_length_upgrade/r_length_km
keep road_id subroad_id r_pct_upgraded
save "$Datasets/yearly_upgrades_`year'.dta", replace
restore

merge m:1 road_id subroad_id using "$Datasets/yearly_upgrades_`year'.dta"

sort road_id r_pct_upgraded 
by road_id: replace r_pct_upgraded = r_pct_upgraded[1] 

preserve
duplicates drop road_id, force
tab r_pct_upgraded 
restore

* 9 roads over 90 % upgraded in rolling composite 2018
* 0 roads over 90 % upgraded in rolling composite 2019
* 2 roads over 90 % upgraded in rolling composite 2020
* 48 roads over 90 % upgraded in rolling composite 2021

* Create a dummy for yearly upgrades
replace r_pct_upgraded = 0 if r_pct_upgraded == .
gen partial_upgrade = 0
replace partial_upgrade = 1 if r_pct_upgraded > 0 