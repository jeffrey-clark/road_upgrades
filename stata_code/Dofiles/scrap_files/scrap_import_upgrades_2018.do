
* Import roads
import excel "$Resources/roads_2017_2018_04_06.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_04_06.dta", replace

	*** Find out percentage level upgrade on road ***
use "$Datasets/roads_2017_2018_04_06.dta", clear
* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* rename variable for subroad length
rename length_km sr_length_km

sort road_id subroad_id
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded  
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

save "$Datasets/roads_2017_2018_04_06.dta", replace

	*** Import next file ***

* Import roads
import excel "$Resources/roads_2017_2018_05_07.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_05_07.dta", replace
	*** Find out percentage level upgrade on road ***
use "$Datasets/roads_2017_2018_05_07.dta", clear
* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* rename variable for subroad length
rename length_km sr_length_km

sort road_id subroad_id
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded  
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

save "$Datasets/roads_2017_2018_05_07.dta", replace

	*** Import next file ***

* Import roads
import excel "$Resources/roads_2017_2018_06_08.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_06_08.dta", replace
	*** Find out percentage level upgrade on road ***
use "$Datasets/roads_2017_2018_06_08.dta", clear
* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* rename variable for subroad length
rename length_km sr_length_km

sort road_id subroad_id
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded  
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

save "$Datasets/roads_2017_2018_06_08.dta", replace

	*** Import next file ***

* Import roads
import excel "$Resources/roads_2017_2018_07_09.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_07_09.dta", replace
	*** Find out percentage level upgrade on road ***
use "$Datasets/roads_2017_2018_07_09.dta", clear
* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* rename variable for subroad length
rename length_km sr_length_km

sort road_id subroad_id
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded  
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

save "$Datasets/roads_2017_2018_07_09.dta", replace
	*** Import next file ***


* Import roads
import excel "$Resources/roads_2017_2018_08_10.xlsx" , firstrow case(lower) clear
save "$Datasets/roads_2017_2018_08_10.dta", replace
	*** Find out percentage level upgrade on road ***
use "$Datasets/roads_2017_2018_08_10.dta", clear
* Delete subroad upgrades recorded as paving type
replace upgraded = 0 if upgrade_type == "paving"
replace upgrade_type = "" if upgrade_type == "paving"

* rename variable for subroad length
rename length_km sr_length_km

sort road_id subroad_id
by road_id: egen r_length_km = total(sr_length_km) // total sr lengths for r level

* Get percentage upgrade on road level
sort road_id subroad_id upgraded  
by road_id subroad_id upgraded: egen sr_length_upgraded = total(sr_length_km)

sort road_id subroad_id upgraded 
by road_id subroad_id upgraded: replace sr_length_upgraded = cond(_n==1,sr_length_upgraded,0)

replace sr_length_upgraded = 0 if upgraded == 0

sort road_id
by road_id: egen r_length_upgraded = total(sr_length_upgraded)

gen r_pct_upgraded = r_length_upgrade/r_length_km

*Look at the distribution of percentage upgrades
tab r_pct_upgrade

save "$Datasets/roads_2017_2018_08_10.dta", replace
	*** Import done ***


use "$Datasets/roads_2017_2018_04_06.dta", clear
append using "$Datasets/roads_2017_2018_05_07.dta" "$Datasets/roads_2017_2018_06_08.dta" "$Datasets/roads_2017_2018_07_09.dta" "$Datasets/roads_2017_2018_08_10.dta"
save "$Datasets/roads_2018.dta", replace

use "$Datasets/roads_2018.dta", clear
