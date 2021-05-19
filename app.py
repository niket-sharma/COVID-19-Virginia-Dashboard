'''
Python dash file:

Visualizes the dashboard for the predction model and
    the optimization model
'''


# package imports
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from virginia_prediction_model import predict
from virginia_optimization_model import optimize
import plotly.express as px


# css stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# python dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# radio buttons for state prediction vs county prediction
state_vs_county = {
    'state level': [],
    'county level': []
}

# sorted list of county names
my_counties = pd.read_csv('locality_populations.csv',names=['locality','population'])
my_counties = my_counties.sort_values(by=['locality'])

# prediction model input variables
location = 'Virginia'
scenario = 1
days = 30
custom_params = {
    'theta': 0.00683125,
    'sigma': 0.072947592,
    'kappa': 0.003590055,
    'V1': 0.00364
}

# optimizatioin model input variables
stockpile = 0


# html layout code
app.layout = html.Div([

    # dashboard tabs
    dcc.Tabs([
		
		# Introduction tab
		dcc.Tab(label='Welcome Page',children=[
			html.Div(children=[
			html.H1(
				children= 'The Virginia COVID-19 Vaccine Dashboard',
				style={
            		'textAlign': 'center',
					'text-decoration': 'underline'
        			}
			),
			dcc.Markdown('''
			## Introduction
			Welcome to the Virginia COVID-19 Vaccine dashboard! 
			The purpose of this dashboard is to use vaccine administration 
			data in tandem with the well-understood COVID-19 cases data to 
			see how the virus is affecting 
			the state of Virginia now and in the future. This dashboard
			features a suite of functionalities that enables the user to 
			simulate custom COVID-19 progression scenarios and easily derive
			insights from the results. The two models we introduce here is
			the **prediction model** and the **optimization model**. 

			## Prediction Model
			Given some initial parameters, the prediction model forecasts
			the potiential spread of COVID-19 in Virginia over a specified
			number of days. To use the prediction model, click the 
			"Prediction Model" tab. Let's go over what each of the 
			prediction model inputs mean, and how to interpret the output.
			
			1. **Region**:

			The prediction model can run a simulation at the state level
			or at the individual county level. In the first block of the
			prediction model page, the user can select the **state level** 
			radio button if they want their results to be for the entire 
			state of Virginia, or they can select the **county level** 
			button if they want to see results for a specific county. 
			If the user selects the **county level** button, 
			they can pick their county of interest from the 
			**select county** dropdown menu.

			2. **Scenarios**:

			Due to factors like virus variants, vaccine hesitancy, and
			vaccine distribution, there is a degree of uncertainty in
			how COVID-19 can progress. Our predition model takes this
			uncertainty by enabling the user to simulate different 
			scenarios in our **Scenarios** section. When the scenarios
			dropdown menu is clicked, the user sees 4 options for 
			scenarios. The **real scenario** option represents the expected
			progress of COVID-19, barring any unexpected events. The 
			**bad scenario** option represents a "worst-case scenario" 
			so to speak. In the bad scenario, the virus is more 
			transmisible, vaccine administration counts is diminished,
			and vaccine hesitancy is high, resulting in more reinfections.
			On the flip size, the **good scenario** option represents
			a best-case scenario, where vaccine hesitancy is low and the
			virus is less transmisible.

			The scenarios section also has a **custom scenarios** option,
			where the user can input specific prediction model scenario
			parameters. If enabled, the user can input custom infection
			rates, recovery rates, deaths rates, and vaccine rates into
			the prediction model.
			
			3. **Period**:

			In the **Period** block, the user select how far into the 
			future the prediction model runs.

			4. **Output**:

			When the user is satified with their inputs, they can
			click the **Predict** button to execute the prediction model.

			The output itself is a normalized time series of different 
			variables of interest, like the number of people infected and
			the number of people vaccinated.

			## Optimization Model
			Given a number of vaccines, the optimization model 
			methodologically allocates vaccines to the counties that
			need it most. The output to the optimization model is a table
			that tells how many vaccines a county receives, and the 
			prioritization level of the county.
			'''),

			],style={'background-color': '#e6f2ff'})],

		),


        # prediction model tab
        dcc.Tab(label='Prediction Model', children=[
			html.Div(children=[
            # html heading (makes the thin grey line)
            html.Hr(),

            # state prediction vs county prediction radio button html
            html.Label('1. Region'),
            dcc.RadioItems(
                id='state-v-county-radio',
                options=[{'label': k, 'value': k} for k in \
                state_vs_county.keys()],

                value='state level'
            ),
            
            # county drop-down box
            html.Label('select county'),
            dcc.Dropdown(
                id='county-dropdown-prediction',
                options=[{'label': k, 'value':k} for k in my_counties['locality']],
            ),
            
            html.Hr(),
            
            # scenario type drop-down box
            html.Label("2. Scenarios"),
            dcc.Dropdown(
                id='scenario-dropdown',
                options=[
                    {'label': 'real scenario', 'value': 'average'},
                    {'label': 'bad scenario', 'value': 'bad'},
                    {'label': 'good scenario', 'value': 'good'},
                    {'label': 'custom scenario', 'value': 'custom'}
                ],
                value='average',
                clearable=False
            ),
            
            # custom scenario parameters text boxes
            html.Label('Custom infection rate',id="custom-infection-label"),
            dcc.Input(
                id='infection-rate', 
                placeholder='infection rate (decimal)', 
                type='text',
                disabled=True,
                debounce = True
            ),
            
            html.Label('Custom recovery rate',id="custom-recovery-label"),
            dcc.Input(
                id='recovery-rate', 
                placeholder='recovery rate (decimal)', 
                type='text',
                disabled=True,
                debounce = True
            ),
                
            html.Label('Custom death rate',id="custom-death-label"),
            dcc.Input(
                id='death-rate', 
                placeholder='death rate (decimal)', 
                type='text',
                disabled=True,
                debounce=True
            ),
            
            html.Label('Custom vaccine rate',id="custom-vaccine-label"),
            dcc.Input(
                id='vaccine-rate', 
                placeholder='vaccine rate (decimal)', 
                type='text',
                disabled=True,
                debounce=True
            ),
            html.Hr(),

            # slider for days to prediction
            html.Label("Period"),
            dcc.Slider(
                id='prediction-days',
                min=30,
                max=360,
                step=None,
                marks={
                30: '30 days',
                60: '60 days',
                90: '90 days',
                120: '120 days',
                150: '150 days',
                180: '180 days',
                210: '210 days',
                240: '240 days',
                270: '270 days',
                300: '300 days',
                330: '330 days',
                360: '360 days'
                },
                value=30            
            ),

            html.Hr(),

            # prediction button
            html.Label('Execute prediction'),
            html.Button('predict',id='predict-button'),

            # prediction model output
            html.Div(id='prediction-loading'), 
				dcc.Loading(
				id="p-loading",
				type="dot",
				children=dcc.Graph(id='prediction-output')
            )
        ])]),
        
        
        # optimization model tab
        dcc.Tab(label='Optimization Model', children=[
            html.Hr(),
            
            # stockpile input
            html.Label('Vaccine Allocation'),
            dcc.Input(
                id='vaccine-stockpile', 
                type='number',
                placeholder='integer',
            ),

            # optimization button
            html.Label('Execute optimization'),
            html.Button('optimize',id='optimize-button'),
            
            # optimizaton model output
            dcc.Loading(
                id="optimization-loading",
                type="cube",
                children=html.Div(id="optimization-output")
            ),
        ]),
    ])
])

# functions for interacting with user input
# --------------------------------------------


# disable county drop-down when state level is selected
@app.callback(
    Output('county-dropdown-prediction','disabled'),
    Input('state-v-county-radio','value'),prevent_initial_call=True)
def set_stateOrCounty_status(val):
    if val == 'state level':
        global location
        location = 'Virginia'
        return True
    else:
        return False

# updates pred model location parameter
@app.callback(
    Output('county-dropdown-prediction','value'),
    Input('county-dropdown-prediction','value'),prevent_initial_call=True
)
def update_location(val):
    global location
    location = val
    return val

# disables custom scenario text-boxes when custom is not selected 
@app.callback(
    Output('infection-rate','disabled'),
    Output('recovery-rate','disabled'),
    Output('death-rate','disabled'),
    Output('vaccine-rate','disabled'),
    Input('scenario-dropdown','value'),prevent_initial_call=True
)
def set_scenario_custom_status(val):
    if val == 'custom':
        return [False,False,False,False]
    else:
        return [True,True,True,True]

# updates scenario input parameter
@app.callback(
    Output('scenario-dropdown','value'),
    Input('scenario-dropdown','value'),prevent_initial_call=True
)
def update_scen(val):
    global scenario

    if val == 'average':
        scenario = 1
    elif val == 'bad':
        scenario = 0
    elif val == 'good':
        scenario = 2
    elif val =='custom':
        scenario = custom_params
    return val

# next few functions updates custom parameter values (backend stuff)
@app.callback(
    Output('infection-rate','value'),
    Input('infection-rate', 'value'),prevent_initial_call=True
)
def update_infection(val):
    global custom_params
    global scenario

    custom_params['theta'] = float(val)
    scenario = custom_params
    return val

@app.callback(
    Output('recovery-rate','value'),
    Input('recovery-rate','value'),prevent_initial_call=True
)
def update_recovery(val):
    global custom_params
    global scenario

    custom_params['sigma'] = float(val)
    scenario = custom_params
    return val

@app.callback(
    Output('death-rate','value'),
    Input('death-rate','value'),prevent_initial_call=True
)
def update_death(val):
    global custom_params
    global scenario

    custom_params['kappa'] = float(val)
    scenario = custom_params
    return val

@app.callback(
    Output('vaccine-rate','value'),
    Input('vaccine-rate','value'),prevent_initial_call=True
)
def update_vaccine(val):
    global custom_params
    global scenario

    custom_params['V1'] = float(val)
    scenario = custom_params
    return val


@app.callback(
    Output('prediction-days','value'),
    Input('prediction-days','value'),prevent_initial_call=True
)

# updates days input parameter
def update_days(val):
    global days

    days = val
    return val

@app.callback(
    Output('prediction-output', 'figure'),
    Input('predict-button','n_clicks')
)
# when prediction button is clicked, run prediction model
def execute_predict(btn):
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	if 'predict-button' in changed_id:
		pred = predict(location,scenario,days) # prediction model
		fig = px.line(pred, x = "time",  y = pred.columns[0:5])
		fig.update_layout(title='Covid-19 Prediction Model',
				xaxis_title='days',
				yaxis_title='Number of people normalized',
				transition_duration=500)
		return fig
	else:
		return {}

@app.callback(
    Output('vaccine-stockpile','value'),
    Input('vaccine-stockpile','value'),prevent_initial_call=True
)

# updates stockpile input parameter
def update_stockpile(val):
    global stockpile

    stockpile = val
    return val


@app.callback(
	Output("optimization-output", "children"),
	Input("optimize-button", "n_clicks")
)
# when optimization button is clicked, run optimiztion model
def execute_optimize(btn):
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]	
	if 'optimize-button' in changed_id:
		opt = optimize(stockpile)
	
		return dash_table.DataTable(
			id='table',
			columns=[{"name": i, "id": i} for i in opt.columns],
			data=opt.to_dict('records'),
			)


if __name__ == '__main__':
    app.run_server(debug=True)
