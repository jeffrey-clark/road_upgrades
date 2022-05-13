

* Import roads base
import excel "$Composite_dir/roads_2017_2018_04_06.xlsx" , firstrow case(lower) clear
keep road_id subroad_id length_km
save "$Datasets/rolling_composite_dummies_raw.dta", replace



local filelist: dir "$Composite_dir" files "*.xlsx"
dis `filelist'


foreach file of local filelist {
  dis "`file'"
  local year =substr("`file'", 12, 4)
  dis "`year'"
local month =substr("`file'", 20, 2)	
  dis "`month'"
 
  * First import the excel filelist
  import excel "$Composite_dir/`file'" , firstrow case(lower) 	clear
	replace upgraded = 0 if upgrade_type == "paving"
	keep upgraded road_id subroad_id
	rename upgraded upgraded_`year'_`month'
	merge 1:1 road_id subroad_id using "$Datasets/rolling_composite_dummies_raw.dta"
	order upgraded_`year'_`month', last
	drop _merge
	order road_id subroad_id length_km, first
	save "$Datasets/rolling_composite_dummies_raw.dta", replace
}



