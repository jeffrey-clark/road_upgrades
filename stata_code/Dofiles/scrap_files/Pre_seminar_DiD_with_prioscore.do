* use merge roads and cells
use "$Datasets/grid_cells_prioritization.dta", clear

reshape long ndvi_, i(id) j(year) 

rename ndvi_ ndvi
order year, before(ndvi)

* Generate pre and post periods, here 2016-2019 are pre periods and 2021-2022 post
* Possibly we could exclude year 2021 from the analysis, as upgrade takes place during that time?
gen post = 0
replace post = 1 if year >= 2021
gen did = post*treatment 
rename population population_2019
 
* Declare data set as panel data
xtset id year

drop if prioritization_score > 10
drop if prioritization_score < -10

drop if prioritization_score > 8
drop if prioritization_score < -8

* Removed year == 2021 due to ambiguities in treatment status: can you do this??
drop if year == 2021

* Parallel trend graph
preserve
collapse (mean) ndvi, by(treatment year)
reshape wide ndvi, i(year) j(treatment)
graph twoway connect ndvi* year if year < 2021
restore

* Restrict the sample to find apt control groups to our treatment roads. 
* Score -8 to 8 looks good in parallel trends; did becomes insignificant (stat)

*NOW CLUSTERED ON GRID CELL ID
* "Naive regression"
xtreg ndvi treatment post did
* Naive + cluster standard errors
xtreg ndvi treatment post did, cluster(id) 

*Fixed effects + cluster standard errors 
xtreg ndvi treatment post did, fe cluster(id)