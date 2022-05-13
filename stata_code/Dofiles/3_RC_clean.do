*-------------------------------------------------------------------------------
* What this file does: 
* Deletes paving upgrades on subroad level
* Calculates percentage road upgrades on road level
* Cleans the data from intermediary variables and observations not defined as control nor treatment	 	  
* Reshapes the file into long format      
*		 		
*---------------------------------------------------------------------

* load the dataset
use "$Datasets/grid_cells_merged.dta", clear

*Clean the data from intermediary variables we created
drop merge_upgraded
drop col_id

*Define treatment and control groups
gen treatment = 0
replace treatment = 1 if r_pct_upgraded >= 0.90

*Generate unique identifyers for the data
set seed 5350
gen id = runiform()
sort id
replace id = _n

order id, first
order upgraded treatment concat, last

save "$Datasets/grid_cells_cleaned.dta", replace
use "$Datasets/grid_cells_cleaned.dta", clear

