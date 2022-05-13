use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

tab prioritization_score

* Minimum score is -35.2, maximum score is 27.3 (update plz)

* Generate pre and post periods, here 2018-2020 are pre periods and 2022 post
* We will exclude year 2021 from the analysis, as upgrade takes place during that time.

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

gen nampula = 0
replace nampula = 1 if province == "Nampula"

egen province_cat = group(province)

*egen district_cat = group(district)

*egen road_cat = group(rnd_road_id)

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

* Regressions, for these regressions we excluded year 2021 as upgrades would take place then. 

* Naive + cluster standard errors on road level
reg ndvi treatment post did if year != 2021, cluster (rnd_road_id) 
estimates store did_naive

*GC Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if year != 2021, fe cluster(rnd_road_id) 
estimates store did_GC_FE

*GC + Year Fixed effects + cluster standard errors 
xtreg ndvi treatment post did i.year if year != 2021, fe cluster(rnd_road_id) 
estimates store did_GC_Y_FE

*** With rainfall ***

*GC Year Fixed effects + cluster standard errors 
xtreg ndvi treatment post did rainfall i.year if year != 2021, fe cluster(rnd_road_id) 
estimates store did_GC_Y_FE_rain

*GC + Year + region FE + cluster standard errors 
reghdfe ndvi treatment post did rainfall if year != 2021, absorb(year province) vce(cluster rnd_road_id) 
estimates store did_GC_Y_P_FE

*** Time-invariant controls ***, but province_cat instead of nampula
reghdfe ndvi treatment post did rainfall r_length_km population_2019 nearest_city if year != 2021, absorb(year province) vce(cluster rnd_road_id)
estimates store did_controls_Y_FE

esttab did_naive did_GC_FE did_GC_Y_FE did_GC_Y_FE_rain did_GC_Y_P_FE did_controls_Y_FE using "primary_did.tex", replace label starlevels(* 0.1 ** 0.05 *** 0.01) se stats(N) title(Difference-in-differences) compress

