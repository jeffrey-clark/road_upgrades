*---------------------------------------------------------------------
* What this file does: 
* Descriptive statistics on prioritization score, selected and positive score on ///
* road level. 
*---------------------------------------------------------------------

*** 1 *** use merge roads and cells
use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear
 
*** 2 *** First stage regression - Now clustered on grid cell level...
gen positive_score = 0
replace positive_score = 1 if prioritization_score > 0

plot treatment prioritization_score

rename population population_2019
gen pop_per_area = population_2019/area

label variable ndvi NDVI
label variable nearest_city "Nearest city"
label variable area "Grid cell size"
label variable r_length_km "Road length in kilometers"
label variable population_2019 "Population in 2019"
label variable pop_per_area "Grid cell population density"
label variable prioritization_score "Prioritization score"
label variable rainfall "Precipitation in meters"
label variable positive_score "Positive prioritization score"

preserve
drop if year < 2022
sort treatment rnd_road_id positive_score selected
collapse(mean) prioritization_score, by(treatment rnd_road_id positive_score selected)
eststo clear
eststo treatment: quietly estpost summarize ///
prioritization_score positive_score selected if treatment == 1
eststo control: quietly estpost summarize ///
prioritization_score positive_score selected if treatment == 0
esttab treatment control using descriptive_stats_prio.tex, ///
cells("mean(pattern(1 1) fmt(4)) sd(pattern(1 1))") ///
label 
restore 

preserve
drop if year < 2022
sort treatment rnd_road_id positive_score selected
collapse(mean) prioritization_score, by(treatment rnd_road_id positive_score selected)
eststo clear
eststo tr_select: quietly estpost summarize ///
prioritization_score if selected == 1 & treatment == 1
eststo co_select: quietly estpost summarize ///
prioritization_score if selected == 1 & treatment == 0
eststo co_nselect: quietly estpost summarize ///
prioritization_score if selected == 0 & treatment == 0
eststo tr_nselect: quietly estpost summarize ///
prioritization_score if selected == 0 & treatment == 1
esttab tr_select co_select co_nselect tr_nselect using descriptive_stats_roadid.tex, ///
cells("count") 
restore 

