* Make the necessary changes in the file received from Tillmann

* import the jittered file
use "$Datasets/post_jitter/share_latest_processed_$Gridcell_height.dta", clear


* Clean away prefixes and suffixes added in the jittering process
foreach var of varlist * {
	
	dis "`var'"
	
	* remove the keepCat prefix
	if strpos("`var'", "keepCat") > 0{
		local newname = substr("`var'", 9, .)
		rename `var' `newname'
	}
	
	* remove the keepCont prefix and _rep suffix
	if strpos("`var'", "keepCont") > 0{
		
		local end_index = strpos("`var'", "_rep")
		local var_span = `end_index' - 10
		local newname = substr("`var'", 10, `var_span')
		rename `var' `newname'
	}
	
}
	
	
* reorder as desired
order upgraded treatment Selected PrioritizationScore, last
rename Selected selected
rename PrioritizationScore prioritization_score


save "$Datasets/grid_cells_prioritization.dta", replace
use "$Datasets/grid_cells_prioritization.dta", clear