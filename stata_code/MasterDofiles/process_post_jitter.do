
** Rerun the initialize file to set the Gridcell_height and Gridcell_dir

do "Initialize.do"


** Now we loop through all of the post jitter files 

* get list of all directories (each directory own gridcell height)
local filelist : dir "$Datasets/post_jitter/" files "*.dta"


foreach file of local filelist{
	dis "`file'" 
	local height =substr("`file'", 24, 10)
	local height =substr("`height'", 1, strlen("`height'")-4)
	global Gridcell_height `height'
	

	do "$Dofiles/4b_tillmann_import.do"
	do "$Dofiles/5a_1_ndvi_difference.do"
	do "$Dofiles/5a_2_reshape.do"
	save "$Datasets/post_jitter_reshape/grid_cells_reshape_`height'.dta", replace
}

do "$Dofiles/10b_Heterogeneity_gridcell_primary.do"
do "$Dofiles/10b_Heterogeneity_gridcell_selected.do"
do "$Dofiles/10b_Heterogeneity_gridcell_prio.do"

** Restore backups
do "Initialize.do"
do "$Dofiles/4b_tillmann_import.do"
do "$Dofiles/5a_1_ndvi_difference.do"
do "$Dofiles/5a_2_reshape.do"

	
	