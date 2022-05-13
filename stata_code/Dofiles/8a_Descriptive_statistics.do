
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

*** Descriptive statistics for treatment vs control group ***
*** All time-invariant data will be the same across periods, obviously. 
*** For above reason, we might want to only report time invariant 
*** statistics once


*Pattern: says if output is to be printed or suppressed, 1 for print 0 for suppress
*fmt is number of decimals

preserve
drop if year < 2018
drop if year == 2021
drop if year == 2022
sort treatment
eststo clear
eststo treatment: quietly estpost summarize ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall if treatment == 1
eststo control: quietly estpost summarize ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall if treatment == 0
eststo diff: quietly estpost ttest ///
ndvi nearest_city r_length_km area population_2019 pop_per_area prioritization_score rainfall, by(treatment) unequal
esttab treatment control diff using primary_sum_stat_group.tex, ///
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
eststo treatment: quietly estpost summarize ///
ndvi rainfall if treatment == 1
eststo control: quietly estpost summarize ///
ndvi rainfall if treatment == 0
eststo diff: quietly estpost ttest ///
ndvi rainfall, by(treatment) unequal
esttab treatment control diff using primary_sum_stat_group_2.tex, ///
cells("mean(pattern(1 1 0) fmt(4)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(4)) t(pattern(0 0 1) par fmt(4))") ///
label 
restore 

*** Descriptive statistics for SELECTED vs not selected, pre-program ***

* For the periods 2010-2017, by selected group
preserve
drop if year == 2018
drop if year == 2019
drop if year == 2020
drop if year == 2021
drop if year == 2022
sort selected
eststo clear
by selected: eststo: quietly estpost summarize ///
ndvi nearest_city area r_length_km population_2019 pop_per_area prioritization_score rainfall 
esttab, cells("mean sd") label nodepvar

* difference in means
eststo clear
eststo: estpost ttest ndvi nearest_city area r_length_km population_2019 pop_per_area prioritization_score rainfall, ///
    by(selected) unequal 
esttab ., wide label
// unsure about unequal command
restore

