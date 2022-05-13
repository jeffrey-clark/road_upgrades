*-------------------------------------------------------------------------------
* Robustness checks and control group investigations
*
* 
*         
*		 		
*-------------------------------------------------------------------------------

do "$Dofiles/1_import.do"
do "$Dofiles/2_merge.do"
do "$Dofiles/3_clean.do"
do "$Dofiles/Regressions.do"

* Robustness checks
drop post did

***Generate false treatment period
gen post = 0
replace post = 1 if year == 2019
gen did = post*treatment 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if year >= 2016 | year <= 2019, fe cluster(road_id)

drop post did treatment 

***Generate false treatment group, maybe try something else that makes sense
gen treatment = 0
replace treatment = 1 if road_length >= 10

gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did, fe cluster(road_id)

drop post did treatment 

*** Are we using good controls? ***

* Check how long our treated roads are:
* Generate our usual treatment 
gen treatment = 0
replace treatment = 1 if pct_road_upgrade >= 0.90

sort treatment 
by treatment: tab road_length

tab road_length if treatment == 0
tab road_length if treatment == 1

drop post did 

* Check the original non-naive DiD regression for the subset of roads > 10 km
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if road_length >= 10, fe cluster(road_id)

drop post did

* Check the original non-naive DiD regression for the subset of roads < 10 km
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if road_length <= 10, fe cluster(road_id)

* Check the original non-naive DiD regression for the subset of roads < 50 km
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if road_length <= 50, fe cluster(road_id)

drop post did

* Look at how far away nearest_commercial is for treatment and control
tab nearest_commercial if treatment == 0 
tab nearest_commercial if treatment == 1
* Can't see it all, but appears as if though controls have longer to center

* Check the original non-naive DiD regression for the subset of roads < 75 km away from a commercial center
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did if nearest_commercial<= 75, fe cluster(road_id)

drop post did

* Results are pretty robust despite efforts to show see if there are significant effects from restricting our sample ( really restricting our controls)