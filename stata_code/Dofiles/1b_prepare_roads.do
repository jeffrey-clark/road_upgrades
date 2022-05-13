
use "$Datasets/rolling_composite_dummies_raw.dta", clear

forval year = 2018/2021 {

	dis "`year'"
	gen upgrade_period_count_`year' = upgraded_`year'_06 + upgraded_`year'_07 + upgraded_`year'_08 + upgraded_`year'_09 + upgraded_`year'_10 

}

gen upgraded = 0
gen upgrade_year = ""

gen upgraded_2018 = 0
gen upgraded_2019 = 0
gen upgraded_2020 = 0
gen upgraded_2021 = 0

foreach var of varlist upgraded_* {
	dis "`var'"
	local year =substr("`var'", 10, 4)
	if "`var'" == "upgraded_`year'" {
		dis "skipping"
		continue
	}
	
	replace upgraded = `var' if upgraded == 0 & upgrade_period_count_`year' > 1
	replace upgraded_`year' = `var' if upgraded_`year' == 0 & upgrade_period_count_`year' > 1
	replace upgrade_year = "`year'" if upgrade_year == "" & upgraded == 1 
}

drop upgrade_period_count* 

destring upgrade_year, replace 

* Find out road level percentage upgrade
* rename some variables
rename length_km sr_length_km
* total sr lengths for road level
sort road_id
by road_id: egen r_length_km = total(sr_length_km) 
* length of sub road upgrade:
gen sr_length_upgrade = sr_length_km if upgraded == 1
* get road length upgrade
sort road_id
by road_id: egen r_length_upgrade = total(sr_length_upgrade)
gen r_pct_upgraded = r_length_upgrade/r_length_km

preserve
duplicates drop road_id, force
tab r_pct_upgraded 
restore

* 64 roads upgraded (over 90%) by 2021

sort road_id
by road_id: egen last_upgrade = max(upgrade_year)

*Drop the dublicate road 
*Manual drop
drop if road_id == 102

preserve
duplicates drop road_id, force
tab last_upgrade if r_pct_upgraded >0
restore

preserve
duplicates drop road_id, force
tab last_upgrade if r_pct_upgraded >= 0.90
restore
* 73 roads are finalized in 2021. 

* Drop the previous upgrades
drop if r_pct_upgraded >= 0.90 & last_upgrade != 2021 

* The roads that must be removed
*Clean the data from ambiguities: drop all observations that have r_pct_upgrade larger than zero but smaller than 90 %. 
drop if r_pct_upgraded < 0.90 & r_pct_upgraded > 0.10

save "$Datasets/rolling_composite_dummies.dta", replace

import excel "$Composite_dir/roads_2017_2018_04_06.xlsx", firstrow case(lower) clear
drop upgrade_type upgraded
merge 1:1 road_id subroad_id using "$Datasets/rolling_composite_dummies.dta"
drop _merge

* Random road id generator *
duplicates drop road_id, force
set seed 5350
gen rnd_road_id = runiform()
order road_id rnd_road_id
sort rnd_road_id
replace rnd_road_id = _n

keep road_id rnd_road_id

merge 1:m road_id using "$Datasets/rolling_composite_dummies.dta"
drop _merge

sort rnd_road_id subroad_id
order rnd_road_id, first

save "$Datasets/roads.dta", replace


* Import the id to concat table
import excel "$Resources/id_concat_table.xlsx", firstrow case(lower) clear
save "$Datasets/id_concat_table.dta", replace

* Merge the concat value into the roads data set
use "$Datasets/roads.dta", clear
merge m:1 road_id using "$Datasets/id_concat_table.dta"
drop _merge
save "$Datasets/roads.dta", replace
