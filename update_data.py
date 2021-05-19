'''
update_data.py: go to vdh website and download the most recent
				COVID-19 data relevant to our dashboard
'''


import os
import requests

# update COVID-19 cases dataset
vdh_cases='https://data.virginia.gov/api/views/bre9-aqqr/rows.csv?accessType=DOWNLOAD'
response = requests.get(vdh_cases)
with open(os.path.join("locality_cases.csv"), 'wb') as f:
	f.write(response.content)

print('Virginia COVID-19 cases dataset updated!')

# update COVID-19 vaccine administrations dataset
vdh_vaccines='https://data.virginia.gov/api/views/28k2-x2rj/rows.csv?accessType=DOWNLOAD'
response = requests.get(vdh_vaccines)
with open(os.path.join("locality_vaccines.csv"), 'wb') as f:
	f.write(response.content)

print('Virginia COVID-19 vaccine administration dataset updated!')
