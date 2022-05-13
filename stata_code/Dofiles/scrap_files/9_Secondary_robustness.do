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

gen post = 0
replace post = 1 if year == 2022
gen did = treatment*post

* No anticipation effects, say treatment is year 2018. 
gen post_ant = 0
replace post_ant = 1 if year > 2018
gen did_ant = post_ant*treatment 

* Placebo test, say treatment year is 2015
gen post_plac = 0
replace post_plac = 1 if year > 2015
gen did_plac = post_plac*treatment 

* Declare data set as panel data
xtset id year

*Fixed effects + cluster standard errors 
*xtreg ndvi treatment post did, fe cluster(rnd_road_id) 
*Fixed effects + cluster standard errors + year fixed effects
xtreg ndvi treatment post_ant did_ant rainfall i.year if selected == 1 & year == 2018 | year == 2019 | year == 2020 | year == 2021 | year == 2022, fe cluster(rnd_road_id) 
estimates store selected_robustness_anticipation

*Fixed effects + cluster standard errors + year fixed effects
xtreg ndvi treatment post_plac did_plac rainfall i.year if selected == 1 & year == 2013 | year == 2014 | year == 2015 | year == 2016 | year == 2017 | year == 2018, fe cluster(rnd_road_id) 
estimates store selected_robustness_placebo

*Fixed effects + cluster standard errors 
*xtreg ndvi treatment post did, fe cluster(rnd_road_id) 
*Fixed effects + cluster standard errors + year fixed effects
xtreg ndvi treatment post_ant did_ant rainfall i.year if prioritization_score > 0 & year == 2018 | year == 2019 | year == 2020 | year == 2021 | year == 2022, fe cluster(rnd_road_id) 
estimates store prio_robustness_anticipation

*Fixed effects + cluster standard errors + year fixed effects
xtreg ndvi treatment post_plac did_plac rainfall i.year if prioritization_score > 0 & year == 2013 | year == 2014 | year == 2015 | year == 2016 | year == 2017 | year == 2018, fe cluster(rnd_road_id) 
estimates store prio_robustness_placebo

esttab selected_robustness_anticipation selected_robustness_placebo prio_robustness_anticipation prio_robustness_placebo using "secondary_robustness.tex", replace label starlevels(* 0.1 ** 0.05 *** 0.01) se stats(N) title(Robustness tests) compress 


 