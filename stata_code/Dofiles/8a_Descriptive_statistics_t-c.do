
use "$Datasets/grid_cells_prioritization_diff_reshape.dta", replace

rename population population_2019

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 

gen pop_per_area = population_2019/area

label variable ndvi "NDVI"
label variable nearest_city "Nearest city"
label variable area "Grid cell size"
label variable r_length_km "Road length in kilometers"
label variable population_2019 "Population in 2019"
label variable pop_per_area "Grid cell population density"
label variable prioritization_score "Prioritization score"
label variable rainfall "Precipitation in mm"

gen control = 0
replace control = 1 if treatment == 0

*** Descriptive statistics for treatment vs control group ***

*Pattern: says if output is to be printed or suppressed, 1 for print 0 for suppress
*fmt is number of decimals

preserve
drop if year < 2018
drop if year == 2021
drop if year == 2022
sort treatment
eststo clear
eststo control: quietly estpost summarize ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall if treatment == 0
eststo treatment: quietly estpost summarize ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall if treatment == 1
eststo diff: quietly estpost ttest ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall, by(control) unequal
esttab treatment control diff using primary_sum_stat_group_T-C.tex, ///
cells("mean(pattern(1 1 0) fmt(4)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(4)) t(pattern(0 0 1) par fmt(4))") ///
label 
restore 

preserve
drop if year < 2016
drop if year == 2016
drop if year == 2017
drop if year == 2018
drop if year == 2019
drop if year == 2020
drop if year == 2021
sort treatment
eststo clear
eststo control: quietly estpost summarize ///
ndvi rainfall if treatment == 0
eststo treatment: quietly estpost summarize ///
ndvi rainfall if treatment == 1
eststo diff: quietly estpost ttest ///
ndvi rainfall, by(control) unequal
esttab treatment control diff using primary_sum_stat_group_2_T-C.tex, ///
cells("mean(pattern(1 1 0) fmt(4)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(4)) t(pattern(0 0 1) par fmt(4))") ///
label 
restore 


