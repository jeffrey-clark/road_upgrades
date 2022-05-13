* Placebo tests
use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

rename population population_2019

label variable ndvi NDVI
label variable nearest_city "Nearest city"
label variable area "Grid cell size"
label variable r_length_km "Road length in kilometers"
label variable population_2019 "Population in 2019"
label variable prioritization_score "Prioritization score"
label variable rainfall "Precipitation in mm"
label variable treatment "Treatment"

gen year_2019 = 0
replace year_2019 = 1 if year == 2019

gen ant_dummy = year_2019*treatment

* Placebo test, say treatment year is 2015
gen post_plac = 0
replace post_plac = 1 if year > 2019
gen did_plac = post_plac*treatment 

* Declare data set as panel data
xtset id year

eststo clear

*Primary sample, placebo
xtreg ndvi treatment post_plac did_plac rainfall i.year if year == 2018 |year == 2019 | year == 2020 | year == 2021 | year == 2022, fe cluster(rnd_road_id) 
estimates store robustness_placebo

*Selected roads, placebo
xtreg ndvi treatment post_plac did_plac rainfall i.year if selected == 1 & year == 2018 |selected == 1 & year == 2019 | selected == 1 & year == 2020 | selected == 1 & year == 2021 | selected == 1 & year == 2022, fe cluster(rnd_road_id) 
estimates store selected_robust_placebo

*Positive score, placebo
xtreg ndvi treatment post_plac did_plac rainfall i.year if prioritization_score > 0 & year == 2018 |prioritization_score > 0 & year == 2019 | prioritization_score > 0 & year == 2020 | prioritization_score > 0 & year == 2021 | prioritization_score > 0 & year == 2022, fe cluster(rnd_road_id) 
estimates store prio_robust_placebo

esttab robustness_placebo selected_robust_placebo prio_robust_placebo using "new_sensitivity.tex", replace label starlevels(* 0.1 ** 0.05 *** 0.01) se stats(N) title(Robustness tests) compress 


 