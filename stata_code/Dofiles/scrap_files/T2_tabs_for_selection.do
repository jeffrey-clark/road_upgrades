use "$Datasets/grid_cells_prioritization.dta", clear


count if selected == 1 & treatment == 0
count if selected == 1 & treatment == 1
count if selected == 0 & treatment == 0
count if selected == 0 & treatment == 1

tab prioritization_score if selected == 0 & treatment == 0
tab prioritization_score if selected == 1 & treatment == 1
tab prioritization_score if selected == 0 & treatment == 0
tab prioritization_score if selected == 0 & treatment == 1

tab prioritization_score if treatment == 1
tab prioritization_score if treatment == 0

sum prioritization_score
tab selected if prioritization_score == .
tab prioritization_score

* Minimum score is -35.2, maximum score is 27.3
sort selected
by selected: tab prioritization_score
by selected: tab treatment
