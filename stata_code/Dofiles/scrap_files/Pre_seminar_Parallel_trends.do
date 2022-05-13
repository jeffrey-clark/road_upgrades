*-------------------------------------------------------------------------------
* Parallel trends assumption
*
* -Scatterplot that visualizes pre-treatment trend periods
*         
*		 		
*-------------------------------------------------------------------------------
do "$Dofiles/1_import.do"
do "$Dofiles/2_merge.do"
do "$Dofiles/3_clean.do"
do "$Dofiles/Regressions.do"


* This code collapses the data into only means of ndvi per treatment vs control group
* Notice the large drop for year 2021, if we consider that treatment only started in year 2022 (change the year to 2022)

* Chosen treatment period
preserve
collapse (mean) ndvi, by(treatment year)
reshape wide ndvi, i(year) j(treatment)
graph twoway connect ndvi* year if year < 2021
restore


* If curves are straight lines, this was recommended online in: "https://www.statalist.org/forums/forum/general-stata-discussion/general/1601216-how-to-test-the-parallel-trends-assumption-of-difference-in-differences-estimation"
//xtreg ndvi treatment##c.year if year < 2021
//margins treatment, dydx(year)

* Try some didq
didq ndvi population nearest_commercial road_length if (year>2015 & year<2023), treated(treatment) time(year) begin(2021) end(2022)

* Excluidng year 2017?
didq ndvi population nearest_commercial road_length if (year>2017 & year<2023), treated(treatment) time(year) begin(2021) end(2022)


* The begin(2021) end(2022) arguments would be if treatment started already in 2021.
* Did include some controls there
* I can't quite work out the assumptions, but I don't think we have parallel trends. 
* "In addition, for the computations in didq to be meaningful, the difference between any two consecutive periods should be equal to 1.", see https://journals.sagepub.com/doi/pdf/10.1177/1536867X1501500312

* Looks like we would reject common pre-treatment dynamics. 
* What could be driving these?
sort treatment
by treatment: sum nearest_commercial population road_length

preserve
drop if nearest_commercial < 0.45
drop if nearest_commercial > 73
drop if population > 45000
drop if road_length > 40
collapse (mean) ndvi, by(treatment year)
reshape wide ndvi, i(year) j(treatment)
graph twoway connect ndvi* year if year < 2021
restore

preserve
drop if nearest_commercial < 0.45
drop if nearest_commercial > 73
drop if population > 45000
drop if road_length > 40
xtreg ndvi treatment post did, fe cluster(road_id)
didq ndvi population nearest_commercial road_length if (year>2015 & year<2023), treated(treatment) time(year) begin(2021) end(2022)
restore

* Looks better when we removed some controls that differ from treatment roads in some respects, but as soon as we add controls the commmon pre-treat trends are rejected. 