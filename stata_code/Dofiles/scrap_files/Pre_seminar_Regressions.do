*-------------------------------------------------------------------------------
* DiD Regressions
*Tamina and Jeffrey: maybe you should not define treatment variable in the clean file but rather define it here such that we may change it easily. 
* 
*         
*		 		
*-------------------------------------------------------------------------------
*do "$Dofiles/1_import.do"
*do "$Dofiles/2_merge.do"
*do "$Dofiles/3_clean.do"

/*Non-regression analysis:
gen diff_treat = ndvi_2022-ndvi_2020 if treatment == 1
gen diff_control = ndvi_2022-ndvi_2020 if treatment == 0
egen mean_diff_treat = mean(diff_treat)
egen mean_diff_control = mean(diff_control)
gen no_reg_did = mean_diff_treat - mean_diff_control*/

* Generate pre and post periods, here 2016-2019 are pre periods and 2021-2022 post
* Possibly we could exclude year 2021 from the analysis, as upgrade takes place during that time?
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 
rename population population_2019

* Declare data set as panel data
xtset id year

* Regressions, for these regressions we excluded year 2021 as upgrades would take place then. Where is the exclusion?
* "Naive regression"
xtreg ndvi treatment post did
* Naive + cluster standard errors
xtreg ndvi treatment post did, cluster(road_id) 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did, fe cluster(road_id)

* Issues if we want to add controls, because they are the "same" for each year although the values represent data for one year only (omitted due to fixed effects that control for everything that remains similar acrross years?)
xtreg ndvi treatment post did population, fe cluster(road_id)
xtreg ndvi treatment post did population nearest_commercial road_length, fe cluster(road_id)

*Try without fixed effects and with the controls that remain the same for all years
xtreg ndvi treatment post did population, cluster(road_id)
xtreg ndvi treatment post did population nearest_commercial road_length, cluster(road_id)
* Treatment, population and nearest_commercial omitted due to collinearity but did estimates remain robust

* Should perhaps do something about the fact that all variables except NDVI remain at the same value for all years. We should control for nearest_commercial and population in a certain year instead of treating them as "reappearing" at the same values each year. This might be why they are omitted in the above regressions. So, replace the values as missing for the years they are not representing? Perhaps we should not use a panel at all. 


*** Use the prio_score as a control; then we might have conditional parallel trends. 
* BUT not good as prio causes treatment; maybe better to restrict sample




* Generate dummies for years 
gen d_16 = 0
replace d_16 = 1 if year == 2016

gen d_17 = 0
replace d_17 = 1 if year == 2017

gen d_18 = 0
replace d_18 = 1 if year == 2018

gen d_19 = 0 
replace d_19 = 1 if year == 2019

gen d_20 = 0
replace d_20 = 1 if year == 2020

gen d_21 = 0 
replace d_21 = 1 if year == 2021

gen d_22 = 0 
replace d_22 = 1 if year == 2022


* Create dummies for "remoteness". Could also use quartiles eg.

*MAKE SURE THAT ROADS ARE DROPPED NOT OBSERVATIONS?
gen remoteness_1 = 0
replace remoteness_1 = 1 if nearest_commercial <= 15.0

gen remoteness_2 = 0
replace remoteness_2 = 1 if nearest_commercial > 15.0 & nearest_commercial <= 25.0

gen remoteness_3 = 0
replace remoteness_3 = 1 if nearest_commercial > 25.0 & nearest_commercial <= 35.0

gen remoteness_4 = 0
replace remoteness_4 = 1 if nearest_commercial > 35.0


*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did, fe cluster(road_id) 