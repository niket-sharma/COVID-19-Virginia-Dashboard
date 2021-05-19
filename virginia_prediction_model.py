''' 
Prediction Model Algorithm 

Given user inputs, predicts covid cases, deaths, etc
for how many days the user wants
'''


# package imports
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



# prediction wrapper function
def predict(location,scenario,days):

    # get data on cases, population, vaccines, and ODE parameters
    vdh_data = retrieve_input_data()

    locality_populations = vdh_data[0] # population of each county in VA
    locality_cases = vdh_data[1] # covid cases for each county in VA
    locality_vaccines = vdh_data[2] # vaccine administration numbers in VA
    locality_parameters = vdh_data[3] # ODE parameters for each county in VA
    

    # Run prediction model
    # ---------------------------
    pred = 0
    if location == 'Virginia': # prediction for whole state of VA
        pred = statePrediction(locality_populations, locality_cases, \
        locality_vaccines, scenario, days) 

    else: # prediction for a specific county
        
        # a bit of preprocessing for specific county data
        local_population =  locality_populations.loc[\
        locality_populations['locality']==location]
        
        local_cases = locality_cases.loc[locality_cases['locality']==location]
        
        local_vaccines = locality_vaccines.loc[\
        locality_vaccines['locality']==location]

        pred = countyPrediction(location,local_population,local_cases, \
        local_vaccines, locality_parameters, scenario, days)
    return pred


# ODE function
def deriv(y, t, rho,theta,sigma,kappa,V1):
    xS, xI, xR, xF, xV = y
    dxSdt = -rho * xS * xI - V1
    dxIdt = rho *(1 - theta)* xS * xI  - (sigma + kappa) * xI 
    dxRdt = sigma * xI
    dxFdt = rho*theta*xS*xI + kappa*xI
    dxVdt = V1
    return dxSdt, dxIdt, dxRdt, dxFdt, dxVdt

# state predictions over period
def statePrediction(population,cases,vaccines,scenario,period):
    # county data for most recent date
    most_recent_cases = cases.loc[cases['date']==cases['date'].max()]

    # initial values for prediction model
    initial_confirmed = most_recent_cases['confirmed'].sum()
    initial_fatal = most_recent_cases['fatalities'].sum()
    initial_vaccine = vaccines['doses'].sum()
    initial_recovered = most_recent_cases['recovered'].sum()
    initial_infected = initial_confirmed - \
    initial_fatal - initial_recovered

    # base https://scipython.com/book/chapter-8-scipy
    #/additional-examples/the-sir-epidemic-model/

    # Total population, N.
    N = population['population'].sum()
    # Initial number of infected and recovered individuals, I0 and R0.
    I0 = (initial_infected / N)
    R0 = (initial_recovered / N)
    # vaccinated people = 0 
    V0 = (initial_vaccine / N)
    # Everyone else, S0, is susceptible to infection initially.
    S0 = (N - I0 - R0 - V0) / N
    # intial deaths
    F0 = (initial_fatal / N) 
    

    # pred model ODE parameters
    kappa = 0
    rho = 0
    sigma = 0
    theta = 0
    V1 = 0
        
    if scenario == 1: # real scenario
        kappa = 0.003590055
        rho = 0.086783753 
        sigma = 0.072947592 
        theta = 0.00683125
        V1 = 0.00364

    elif scenario == 0: # bad scenario
        kappa = 0.003590055 * 2
        rho = 0.086783753 * 2 
        sigma = 0.072947592 * 0.5
        theta = 0.00683125
        V1 = 0.001

    elif scenario == 2: # good scenario
        kappa = 0.003590055 * 0.5
        rho = 0.086783753 * 0.5 
        sigma = 0.072947592 * 2
        theta = 0.00683125
        V1 = 0.01
        
    elif isinstance(scenario, dict): # custom scenario
        kappa = scenario['kappa']
        rho = 0.086783753 
        sigma = scenario['sigma']
        theta = scenario['theta']
        V1 = scenario['V1']

    V0 = 0
    

    # A grid of time points (in days)
    t = np.linspace(0, period, period)

    # Initial conditions vector
    y0 = S0, I0, R0, F0, V0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(rho,theta,sigma,kappa,V1))
    xS, xI, xR, xF, xV = ret.T
    temp = pd.DataFrame({"Susceptible Population" : xS, \
	"Infected with COVID-19" : xI, "Recovered from COVID-19" : xR ,\
	"Fatalities" : xF, "Vaccinated Population" : xV, "time" :t})
    return(temp)
    

# county predictions over period
def countyPrediction(county,population,cases,vaccines,params,scenario,period):
    # county data for most recent date
    most_recent_cases = cases.loc[cases['date']==cases['date'].max()]

    # initial values for prediction model
    initial_confirmed = most_recent_cases['confirmed'].sum()
    initial_fatal = most_recent_cases['fatalities'].sum()
    initial_vaccine = vaccines['doses'].sum()
    initial_recovered = most_recent_cases['recovered'].sum()
    initial_infected = initial_confirmed - initial_fatal - initial_recovered

    # base https://scipython.com/book/chapter-8-scipy
    #/additional-examples/the-sir-epidemic-model/

    # Total population, N.
    N = population['population'].sum()
    # Initial number of infected and recovered individuals, I0 and R0.
    I0 = (initial_infected / N)
    R0 = (initial_recovered / N)
    # vaccinated people = 0 
    V0 = (initial_vaccine / N)
    # Everyone else, S0, is susceptible to infection initially.
    S0 = (N - I0 - R0 - V0) / N
    # intial deaths
    F0 = (initial_fatal / N) 
    

    # pred model ODE parameters
    kappa = 0
    rho = 0
    sigma = 0
    theta = 0
    V1 = 0

    if scenario == 1: # real scenario
        kappa = params.loc[params['locality']==county].iloc[0].kappa
        rho = params.loc[params['locality']==county].iloc[0].rho 
        sigma = params.loc[params['locality']==county].iloc[0].sigma 
        theta = params.loc[params['locality']==county].iloc[0].theta
        V1 = 0.00364

    elif scenario == 0: # bad scenario
        kappa = params.loc[params['locality']==county].iloc[0].kappa * 2
        rho = params.loc[params['locality']==county].iloc[0].rho * 2
        sigma = params.loc[params['locality']==county].iloc[0].sigma * 0.5 
        theta = params.loc[params['locality']==county].iloc[0].theta
        V1 = 0.001

    elif scenario == 2: # good scenario
        kappa = params.loc[params['locality']==county].iloc[0].kappa * 0.5
        rho = params.loc[params['locality']==county].iloc[0].rho * 0.5
        sigma = params.loc[params['locality']==county].iloc[0].sigma * 2 
        theta = params.loc[params['locality']==county].iloc[0].theta
        V1 = 0.01

    elif isinstance(scenario, dict): # custom scenario
        kappa = scenario['kappa']
        rho = 0.086783753 
        sigma = scenario['sigma']
        theta = scenario['theta']
        V1 = scenario['V1']

    V0 = 0


    # A grid of time points (in days)
    t = np.linspace(0, period, period)

    # Initial conditions vector
    y0 = S0, I0, R0, F0, V0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(rho,theta,sigma,kappa,V1))
    xS, xI, xR, xF, xV = ret.T

    temp = pd.DataFrame({"Susceptible Population" : xS, \
	"Infected with COVID-19" : xI, "Recovered from COVID-19" : xR ,\
	"Fatalities" : xF, "Vaccinated Population" : xV, "time" :t})

    return(temp)


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
