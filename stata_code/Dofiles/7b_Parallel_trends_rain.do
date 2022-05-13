use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

* Generate pre and post periods, here 2016-2019 are pre periods and 2022 post
* We will exclude year 2021 from the analysis, as upgrade takes place during that time.

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

* Declare data set as panel data
xtset id year

*Create district dummy

egen district_cat = group(district)

*** With rainfall residuals no DiD ***  

xtreg ndvi rainfall i.year if year < 2020, fe cluster(rnd_road_id)
predict residuals
* Parallel trends residual means
preserve
drop if year > 2020
collapse (mean) residuals, by(treatment year)
twoway line residuals year if treatment==1 || line residuals year if treatment==0, ytitle("Residuals") xtitle("Year") ///
legend(label(1 "Treatment") label(2 "Control")) /// 
graphregion(fcolor(white)) ///
lpattern(dash) ///
lcolor(black) ///
yscale(range(0.16 0.3)) ylabel(#8,nogrid)
graph export primary_residual_means.png, replace
restore
drop residuals 


reg ndvi rainfall if year < 2020, cluster(rnd_road_id)
predict residuals
* Parallel trends residual means
preserve
drop if year > 2020
collapse (mean) residuals, by(treatment year)
twoway line residuals year if treatment==1 || line residuals year if treatment==0, ytitle("Residuals") xtitle("Year") ///
legend(label(1 "Treatment") label(2 "Control")) /// 
graphregion(fcolor(white)) ///
lpattern(dash) ///
lcolor(black) ///
yscale(range(0.16 0.3)) ylabel(#8,nogrid)
graph export primary_residual_means_noFE.png, replace
restore
drop residuals 


