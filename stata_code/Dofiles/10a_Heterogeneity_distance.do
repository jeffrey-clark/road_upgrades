use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

egen province_cat = group(province)

* Declare data set as panel data
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

gen dist_1 = 0
gen dist_2 = 0
gen dist_3 = 0

replace dist_1 = 1 if nearest_city < 10
replace dist_2 = 1 if nearest_city >= 10 & nearest_city < 20
replace dist_3 = 1 if nearest_city >= 20

gen dist_did_1 = dist_1*did
gen dist_did_2 = dist_2*did
gen dist_did_3 = dist_3*did

eststo clear

*GC Year Fixed effects + cluster standard errors 
xtreg ndvi treatment post did dist_did_2 dist_did_3 rainfall i.year if year != 2021, fe cluster(rnd_road_id) 
test did dist_did_2 dist_did_3
estimates store heterog_quartiles

* F test joint significance: 0.2324

xtreg ndvi treatment post did dist_did_2 dist_did_3 rainfall i.year if selected == 1 & year != 2021, fe cluster(rnd_road_id) 
test did dist_did_2 dist_did_3
estimates store selected_heterog_quartiles

* F test joint significance: 0.0671

*GC Year Fixed effects + cluster standard errors for prio_score:
xtreg ndvi treatment post did dist_did_2 dist_did_3 rainfall i.year if prioritization_score > 0 & year != 2021, fe cluster(rnd_road_id) 
test did dist_did_2 dist_did_3
estimates store prio_heterog_quartiles

* F test joint significance: 0.0374

esttab heterog_quartiles selected_heterog_quartiles prio_heterog_quartiles using "heterog_did.tex", replace label starlevels(* 0.1 ** 0.05 *** 0.01) se stats(N) title(Difference-in-differences by nearest_city) compress

