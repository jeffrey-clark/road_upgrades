* Run only 5a, not 5b

use "$Datasets/grid_cells_prioritization.dta", clear

rename population population_2019

regress ndvi_diff_2022 treatment ndvi_diff_2020 ndvi_diff_2019 ndvi_diff_2018 ndvi_diff_2017 population_2019 nearest_commercial r_length_km prioritization_score, cluster(rnd_road_id) 

*Create dummies for "remoteness". Could also use quartiles eg.
gen remoteness_1 = 0
replace remoteness_1 = 1 if nearest_commercial <= 15.0

gen remoteness_2 = 0
replace remoteness_2 = 1 if nearest_commercial > 15.0 & nearest_commercial <= 30.0

gen remoteness_3 = 0
replace remoteness_3 = 1 if nearest_commercial > 30.0 & nearest_commercial <= 45.0

gen remoteness_4 = 0
replace remoteness_4 = 1 if nearest_commercial > 45.0


regress ndvi_diff_2022 treatment ndvi_diff_2020 ndvi_diff_2019 ndvi_diff_2018 ndvi_diff_2017 population_2019 remoteness_2 remoteness_3 remoteness_4 r_length_km prioritization_score, cluster(rnd_road_id) 