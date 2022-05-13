  * ******************************************************************** *
  * ******************************************************************** *
  *                                                                      *
  *  MS THESIS          - Initialize.do                                  *
  *                                                                      *
  * **********************************************************************
  * **********************************************************************

    /*
    ** PURPOSE:      Write intro to survey round here

    ** OUTLINE:      PART 0: Standardize settings and install packages
                     PART 1: Prepare folder path globals
                     PART 2: Run the master dofiles for each high-level task

    ** IDS VAR:

    ** NOTES:

    ** WRITTEN BY:   names_of_contributors

    ** Last date modified: 07 March 2022
    */



  * ******************************************************************** *
  *
  *       PART 0:  INSTALL PACKAGES AND STANDARDIZE SETTINGS
  *
  *           - Install packages needed to run all dofiles called
  *
  * ******************************************************************** *

  *Install all packages that this project requires:
  *(Note that this never updates outdated versions of already installed commands, to update commands use adoupdate)
  local user_commands latab estout xls2dta //Fill this list will all user-written commands this project requires
  foreach command of local user_commands {
      cap which `command'
      if _rc == 111 {
          ssc install `command'
      }
  }


  * ******************************************************************** *
  *
  *       PART 1:  PREPARING FOLDER PATH GLOBALS
  *
  *           - Set the global dropbox to point to the project folder
  *            on each collaborator's computer.
  *           - Set other locals that point to other folders of interest.
  *
  * ******************************************************************** *


  * Show the username
  dis "`c(username)'"


  * Jeffrey
  if c(username)=="Jeffrey" {
  global Github "C:/Users/Jeffrey/GitHub/road_upgrades/stata_code"
  }


  * Tamina
  if c(username)=="tamin" {
  global Github "C:\Users\tamin\GitHub\road_upgrades\stata_code"
  }




  global Resources "$Github/Resources"
  global Dofiles "$Github/Dofiles"
  global Datasets "$Github/Datasets"
  global Exports "$Github/Exports"
  global Composite_dir "$Resources/Rolling_composites/composites_3"
  
  global Gridcell_height "10"
  global Gridcell_dir "$Resources/grid_cells/1.0x$Gridcell_height.0"
  
  cd $Github
