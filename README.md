# Virginia COVID-19 Vaccine Dashboard
The **Virginia COVID-19 Vaccine Dashboard** is a vaccine-centered COVID-19 tracking tool for Virginia residents, policy-makers, and researchers alike. 

## Table of contents
1. [Introduction](#introduction)
2. [Technologies](#technologies)
3. [Setup](#setup)
4. [Usage](#usage)
5. [Files](#file-descriptions)
    1. [python](#python-files)
    2. [data](#covid-19-data-files)
    3. [miscellaneous](#miscellaneous)
6. [Contributors](#contributors)

## Introduction
Up until now, COVID-19 dashboards have focused mainly on the number of cases and deaths that a specific geographical region is experiences. Now that COVID-19 vaccines are more ubiquitous in the United States, it would be of interest to see how vaccines affects cases and deaths. Given user inputs, our dashboard provides functionalities for predicting the number of cases and deaths in Virginia and it's subdivisions (taking into account vaccine dose administrations). Also, our optimization model methodologically distributes vaccines to counties that need it most, given user inputs. 

## Technologies
The Virginia COVID-19 Vaccine dashboard was created with:
* anaconda python version: 4.10.1
* dash version: 1.19.0
* plotly version: 4.14.3

## Setup
Clone the Virginia COVID-19 Vaccine dashboard gitlab repository to your local machine
```
git clone https://code.vt.edu/cs-5934-spring-2021/covid-vac/capstone-project.git
```
## Usage
We recommend that you activate an Anaconda environment before running the following command.

To begin using the dashboard on your browser, complete the following steps:
Run the dashoard server app with the following command:
```
python app.py
```
Then visit http://127.0.0.1:8050/ in your web browser. You should see the dashboard page.

## File descriptions
Here are brief descriptions of each of the files in the repository

### Python files
*app.py*   --  The main python dash file. Responsible for all the UI you see.

*update_data.py*  -- Updates the COVID-19 data files needed for the dashboard to the current date. Data is obtained from Virginia Department of Heath. Run the file with the following command
```
python update_data.py
```

*virginia_prediction_model.py* -- Prediction model algorithm. Used by dashboard on the backend

*virginia_optimization_model.py* -- Optimization model algorithm. Used by dashboard on the backend


### COVID-19 data files
*locality_cases.csv* -- COVID-19 cases and deaths broken down to the county level of Virginia by date.

*locality_parameters.csv* -- ODE parameters for each county of Virginia, as well as Virginia at-large. Used by prediction model algorithm for calcuate results.

*locality_populations.csv* -- Population of each county of Virginia

*locality_vaccines.csv* -- Vaccine adminstration counts broken down to the county level by date.

### Miscellaneous
*project_charter.pdf* -- The original project charter for this capstone course.

## Contributors
* Kingsley Nwosu
* Alex Zhu
* Niket Sharma




~                    
