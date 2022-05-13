use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

tab prioritization_score

* Minimum score is -35.2, maximum score is 27.3 (update plz)

* Generate pre and post periods, here 2016-2019 are pre periods and 2022 post
* We will exclude year 2021 from the analysis, as upgrade takes place during that time.

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

gen nampula = 0
replace nampula = 1 if province == "Nampula"

egen province_cat = group(province)

* Declare data set as panel data
xtset id year

drop if year < 2018

label variable ndvi NDVI
label variable nearest_city "Nearest city"
label variable area "Grid cell size"
label variable r_length_km "Road length in kilometers"
label variable population_2019 "Population in 2019"
label variable prioritization_score "Prioritization score"
label variable rainfall "Precipitation in mm"
label variable nampula "Nampula"
label variable treatment "Treatment"
label variable did "DiD"

* We may do the regressions for a restricted sample 

*GC Year Fixed effects + cluster standard errors 
xtreg ndvi treatment post did rainfall i.year if year != 2021 & selected == 1, fe cluster(rnd_road_id) 
estimates store did_secondary_selected

xtreg ndvi treatment post did rainfall i.year if year != 2021 & prioritization_score > 0, fe cluster(rnd_road_id) 
estimates store did_secondary_prio

esttab did_secondary_selected did_secondary_prio using "secondary_did.tex", replace label starlevels(* 0.1 ** 0.05 *** 0.01) se stats(N) title(Secondary difference-in-differences) compress