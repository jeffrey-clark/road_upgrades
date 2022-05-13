* Making a histogram for the road upgrade detection part

* Set the working directory
cd "C:\Users\tamin\GitHub\road_upgrades\stata_code\Histogram"

import excel "average_histogram.xlsx" , firstrow case(lower) clear
save "average_histogram.dta", replace

*twoway (histogram avg_upgraded, percent color(blue%50) width(0.2)) ///
*(histogram avg_not_upgraded, percent color(orange%50) width(0.2)), ///
*legend(order(1 "Upgraded" 2 "Not upgraded")) graphregion(color(white)) ylabel(, nogrid)
*graph export average_histogram.png

/*histogram avg_upgraded, percent normal color(blue%50) width(0.2) name(A)
histogram avg_not_upgraded, percent normal color(orange%50) width(0.2) name(B)
graph combine A B, ycommon xcommon graphregion(color(white))*/

import excel "heuristic_optimization.xlsx" , firstrow case(lower) clear
save "heuristic_optimization.dta", replace

twoway line model heuristic relative_thresh, ytitle("Accuracy (%)") xtitle("Relative threshold (%)") ///
legend(label(1 "Model") label(2 "Heuristic")) /// 
graphregion(fcolor(white)) ///
lpattern(solid dash) ///
lcolor(black black) ///
yscale(range(0.75 1)) ylabel(,nogrid) xlabel(#21)
*graph export heuristic_optimization.png