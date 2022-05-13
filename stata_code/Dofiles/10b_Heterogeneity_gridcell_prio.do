use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

*eststo clear
tempname myresults 
postfile `myresults' cell_size did se using myresults.dta, replace

local filelist : dir "$Datasets/post_jitter_reshape/" files "*.dta"

foreach file of local filelist{
	local height =substr("`file'", 20, 10)
	local height =substr("`height'", 1, strlen("`height'")-4)
	use "$Datasets/post_jitter_reshape/grid_cells_reshape_`height'.dta", clear
	
	gen post = 0
	replace post = 1 if year == 2022
	gen did = post*treatment 
	rename population population_2019
	xtset id year
	drop if year < 2018
	label variable ndvi "NDVI"
	label variable nearest_city "Nearest city"
	label variable area "Grid cell size"
	label variable r_length_km "Road length in kilometers"
	label variable population_2019 "Population in 2019"
	label variable prioritization_score "Prioritization score"
	label variable rainfall "Precipitation in mm"
	label variable treatment "Treatment"
	label variable did "DiD"

	xi: xtreg ndvi treatment post did rainfall i.year if prioritization_score > 0 & year != 2021, fe cluster(rnd_road_id)
	post `myresults' (`height') (`=_b[did]') (`=_se[did]')
	} 
postclose `myresults'
use myresults, clear 

save "$Datasets/heterogeneity/primary_size.dta", replace
rm myresults.dta
use "$Datasets/heterogeneity/primary_size.dta", clear 


sort cell_size

gen se_minus = did - (1.96*se)
gen se_plus = did + (1.96*se) 

gen t_stat = did/se

twoway line did se_minus se_plus cell_size, ytitle("Coefficient") xtitle("Grid cell size") ///
legend(label(1 "DiD estimate") label(2 "DiD - 1.96*se") label(3 "DiD + 1.96*se")) /// 
graphregion(fcolor(white)) ///
lcolor(black black black) ///
lpattern(solid dash dash) ///
yscale(range(-0.01 0.05)) ylabel(, nogrid) yline(0) xscale(range(0 15)) xlabel(#15)
graph export prio_robust_size_CI.png, replace

twoway line t_stat cell_size, ytitle("t-statistic") xtitle("Grid cell size") ///
graphregion(fcolor(white)) ///
lcolor(black) ///
yscale(range(0.8 2.2)) ylabel(#7,nogrid)
graph export prio_robust_size_tstat.png, replace
