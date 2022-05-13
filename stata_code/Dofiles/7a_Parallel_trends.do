use "$Datasets/grid_cells_prioritization_diff_reshape.dta", clear

* Generate pre and post periods, here 2018-2020 are pre periods and 2022 post
* We will exclude year 2021 from the analysis, as upgrade takes place during that time.

gen post = 0
replace post = 1 if year == 2022
gen did = post*treatment 
rename population population_2019

* Declare data set as panel data
xtset id year

label variable ndvi "NDVI"
label variable year "Year"

* Parallel trends with non-restricted prio score (ndvi means)
preserve
drop if year > 2020
collapse (mean) ndvi, by(treatment year)
twoway line ndvi year if treatment==1 || line ndvi year if treatment==0, ytitle("NDVI") xtitle("Year") ///
legend(label(1 "Treatment") label(2 "Control")) /// 
graphregion(fcolor(white)) ///
lpattern(dash) ///
lcolor(black) ///
yscale(range(0.16 0.3)) ylabel(#8,nogrid)
graph export primary_pt_means.png
restore



