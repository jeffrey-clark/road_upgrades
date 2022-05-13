
** Rerun the initialize file to set the Gridcell_height and Gridcell_dir

do "Initialize.do"

do "$Dofiles/1a_import_upgrade_dummies.do"
do "$Dofiles/1b_prepare_roads.do"

** Now we loop through all of the Gridcell heights and store pre_jitter datasets

* get list of all directories (each directory own gridcell height)
local dirlist : dir "$Resources/grid_cells/" dirs "*"


foreach dir of local dirlist{

	local height =substr("`dir'", 5, 4)
	local height =substr("`height'", 1, strlen("`height'")-2)
	global Gridcell_dir "$Resources/grid_cells/1.0x`height'.0"
	
	
	
	do "$Dofiles/1c_import_gridcells.do"
	do "$Dofiles/2_merge.do"
	do "$Dofiles/3_RC_clean.do"
	
	preserve
		sort road_id subroad_id row_id
		save "$Datasets/grid_cells/grid_cells_`height'.dta", replace
	restore 
	
	do "$Dofiles/4a_tillmann_export.do"
	
	save "$Datasets/pre_jitter/share_latest_`height'.dta", replace
}


** Restore the Gridcell_dir global to that which is set in the initialize file
  global Gridcell_dir "$Resources/grid_cells/1.0x$Gridcell_height.0"
