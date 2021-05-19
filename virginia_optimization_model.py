'''
Optimization model algorithm

Given user inputs, methodologically allocations vaccines
to counties of virginia and designates the priority level
of each county
'''

# package imports
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import dateutil.relativedelta
import operator
from itertools import islice


# optimization wrapper function
def optimize(stockpile):
	# get data on cases, population, vaccines, and ODE parameters
	vdh_data = retrieve_input_data()

	locality_populations = vdh_data[0] # population of each county in VA
	locality_cases = vdh_data[1] # covid cases for each county in VA
	locality_vaccines = vdh_data[2] # vaccine administration numbers in VA
	locality_parameters = vdh_data[3] # ODE parameters for each county in VA
		
	# run optimization model
	allocations, priorities = state_optimization_model(stockpile,\
	locality_populations,locality_cases,locality_vaccines)
	
	# output optimization results to dashboard, with a bit of preproccessing
	opt_table = {}
	for key in allocations.keys():
		cols = []
		cols.append(allocations[key])
		if key in priorities[0]:
			cols.append('high')
		elif key in priorities[1]:
			cols.append('moderate')
		else:
			cols.append('low')
		opt_table[key] = cols
	opt_table = pd.DataFrame.from_dict(opt_table, orient='index')
	opt_table = opt_table.reset_index()
	opt_table = opt_table.rename(columns={"index": "state", 0: "vaccine allocation", 1: "priority"})	

	return opt_table

# categorize counties by importance score
def getPriorities(i_scores):
    high_priority = []
    medium_priority = []
    low_priority = []
    
    # top 10% of counties
    for i in range(0,13):
        high_priority.append(i_scores[i])
    
    # next 30% of counties
    for i in range(13,41):
        medium_priority.append(i_scores[i])
    
    # last 60% of counties
    for i in range(41,133):
        low_priority.append(i_scores[i])
        
    return [high_priority,medium_priority,low_priority]


# find good allocation of vaccines and classify counties 
# by priority level
def state_optimization_model(stockpile,population,cases,vaccines):
    
    # get cases and vaccine dose amounts for each county in VA
    county_cases = {}
    county_vaccines = {}
    for coun in set(cases['locality']):
        df_cases = cases.loc[cases['locality']==coun]

        df_vaccines = vaccines.loc[\
		vaccines['locality']==coun].doses.sum() 

        county_cases[coun] = df_cases
        county_vaccines[coun] = df_vaccines
    
    # get importance score for each county
    importance_scores = {}

	# average population of VA
    average_pop = sum(population['population'])/len(population) 
    for coun in set(cases['locality']):

		# population of county
        pop = population[population['locality']==coun].iloc[0].population 
        
        # get cases over past 2 months for county
        df = county_cases[coun]
        curr_case_date = df['date'].iloc[0].date().strftime("%Y-%m-%d")
        d = datetime.datetime.strptime(curr_case_date, "%Y-%m-%d")
        prev_date = d - dateutil.relativedelta.relativedelta(months=2)
        recent_cases = df[df['date'] >= prev_date]
        
        # obtain starting and ending numbers
        curr_infected = recent_cases.iloc[0].infected
        curr_fatalities = recent_cases.iloc[0].fatalities
        prev_infected = int(recent_cases.iloc[len(recent_cases)-1].infected)
        prev_fatalities = int(recent_cases.iloc[\
		len(recent_cases)-1].fatalities)

        # rate of infected/deaths for county
        infected_rate = 0 
        fatality_rate = 0
        if prev_infected == 0:
            infected_rate = (curr_infected - prev_infected)\
			/ (prev_infected + 1)
        else:
            infected_rate = (curr_infected - prev_infected)\
			/ prev_infected

        if prev_fatalities == 0:
            fatality_rate = (curr_fatalities - prev_fatalities)\
			/ (prev_fatalities + 1)
        else:
            fatality_rate = (curr_fatalities - prev_fatalities)\
			/ prev_fatalities 
    
         
        # ratio of people susceptible for infection
        susc = (pop - curr_infected-curr_fatalities-\
		county_vaccines[coun]) / pop

        # importance score formulation
        importance_score = int(((8 * infected_rate) +\
		(12 * fatality_rate) + (4 * susc))*(pop/average_pop))

        importance_scores[coun] = importance_score
        
    # sort importance scores
    importance_scores = dict(sorted(importance_scores.items(),\
	key=operator.itemgetter(1),reverse=True))
    
    # ratio of importance scores for each county
    imp_sum = int(sum(importance_scores.values()))
    imp_ratios = {}
    
    for coun in importance_scores.keys():
        imp_ratios[coun] = importance_scores[coun] / imp_sum
        
    # allocate vaccines based on ratio of importance score
    vaccine_allocations = {}
    for coun in imp_ratios.keys():
        vaccine_allocations[coun] = int(imp_ratios[coun] * stockpile)
     
    # counties by sorted importance score
    counties_sorted = list(importance_scores.keys())
    
    # classify each county into 3 categories based on importance score
    vaccine_priorities = getPriorities(counties_sorted)
    
    return vaccine_allocations, vaccine_priorities


# get needed VDH data
def retrieve_input_data():
	
	# Data Collection and Preprocessing
	# -----------------------------------

	# locality cases dataset collection and cleaning
	locality_cases = pd.read_csv('locality_cases.csv')

	locality_cases = locality_cases.drop(columns=\
	['FIPS', 'Hospitalizations', 'VDH Health District'])

	locality_cases = locality_cases.rename(columns=\
	{"Report Date": "date","Locality": "locality",\
	"Total Cases": "confirmed", "Deaths": "fatalities"})

	locality_cases['date'] = pd.to_datetime(locality_cases.date)

	locality_cases = locality_cases.sort_values(by='date',\
	ascending=False)

	# adding recovered and infected to locality dataset
	locality_cases['recovered'] = \
	(locality_cases['confirmed'] * 9) / 10

	locality_cases['recovered'] = \
	locality_cases['recovered'].astype(int)

	locality_cases['infected'] = locality_cases['confirmed'] - \
	locality_cases['recovered'] - locality_cases['fatalities']

	# virginia county population dataset
	locality_populations = pd.read_csv('locality_populations.csv',\
	names=['locality','population'])

	# virginia vaccine dataset collection and cleaning
	locality_vaccines = pd.read_csv('locality_vaccines.csv')
	locality_vaccines = locality_vaccines.drop(columns=['FIPS',\
	'Health District','Facility Type', 'Vaccine Manufacturer','Dose Number'])

	locality_vaccines = locality_vaccines.rename(columns=\
	{"Administration Date": "date", "Locality": "locality",\
	"Vaccine Doses Administered Count": "doses"})

	locality_vaccines['date'] = pd.to_datetime(locality_vaccines.date)
	locality_vaccines = locality_vaccines.sort_values(by=\
	'date',ascending=False)

	# virginia county prediction model parameters
	locality_parameters = pd.read_csv('locality_parameters.csv')
	
	return[locality_populations, locality_cases, locality_vaccines,locality_parameters]
