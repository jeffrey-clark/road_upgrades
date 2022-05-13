*---------------------------------------------------------------------
* What this file does: 
* - Reduces the sample 
* - Tests whether pripritization score can be used as an IV for "treatment" - i.e. "first stage regression" IV = dummy for prioritization score above zero
* - Runs reduced form regression, i.e. NDVI on IV
* - Runs second stage regression, i.e. generates a new variable = constant from previos regression + IV*coefficient + eventual controls; reg NDVI on new variable + controls
*
* - Runs the IV regression in a single line using ivreg2 rather than broken up
*
* Cluster standard errors at road level please
*---------------------------------------------------------------------

*** 1 *** use merge roads and cells
use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

* Declare data as time series?
 
*** 2 *** First stage regression - Now clustered on grid cell level...
gen positive_score = 0
replace positive_score = 1 if prioritization_score > 0

plot treatment prioritization_score

reg treatment positive_score, cluster(rnd_road_id)

reg selected prioritization_score, cluster(rnd_road_id)
reg selected positive_score, cluster(rnd_road_id)
reg selected prioritization_score if prioritization_score > 0, cluster(rnd_road_id)

* High correlation between selected and positive_score
reg selected positive_score, cluster(rnd_road_id)
reg treatment selected, cluster(rnd_road_id)

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


*Naive regression:
reg ndvi selected r_length_km population nearest_city
*The above has Endogeneity issues because selected are associated with higher agricultural potential

* A Fuzzy RD is an IV
* just identified, see Mixtape pdf page 325
* What to do with "selected" variable? Should we control for it? It jumps at prioritization_score = 0, but also increases the probability of treatment

* First stage 
reg treatment positive_score, cluster(rnd_road_id)

* positive_score needs to increase probability of treatment
* positive_score cannot affect ndvi differences directly, but only through increasing the probability of treatment
* but if positive_score is correlated with agricultural potential and this is correlated with ndvi outcomes then?
* selected is correlated with positive_score (positive score increases probability of selection), but not with agricultural potential or ndvi?
* can we use positive_score as an instrument for selected and selected as an instrument for treatment? what about all roads that are not YET upgraded?
* ivreg2 regression 
* Do something with the data; either use some years, exclude 2021, etc...

* No controls
/*
*** 3 *** Fuzzy RDD regression
preserve
drop if prioritization_score > 10
drop if prioritization_score < -10
ivregress 2sls ndvi (treatment=positive_score) prioritization_score if year == 2022, cluster(rnd_road_id) 

*ivregress 2sls ndvi r_length_km population nearest_commercial (treatment=positive_score) if year != 2021, cluster(rnd_road_id) 
restore

* Better to only do the regressions for certain prioritization_scores directly in the one line of code rather than dropping observations

ivregress 2sls ndvi (treatment=positive_score) prioritization_score if year == 2022 & prioritization_score > -12 & prioritization_score < 12, cluster(rnd_road_id) 
ssc install avar
weakivtest 
* A weak IV?

* Questions:
* Control for prioritization_score?
* Can we use that we have observations from previous years? Now only comparing outcomes in 2022. 

* No reasonable explanaition why NDVI diff should be lower. Perhaps, reallocation out of agriculture rather than increased activity?

*** 4 *** Plots of the discontinuity in assignment to treatment

ssc install cmogram
cmogram treatment prioritization_score, cut(0) scatter line(0.5) qfitci histopts(bin(10)) //Quadratic fit and confidence intervals
cmogram treatment prioritization_score, cut(0) scatter line(0.5) lfit histopts(bin(10)) //linear fit
cmogram treatment prioritization_score, cut(0) scatter line(0.5) lowess histopts(bin(10)) //lowess fit
*/