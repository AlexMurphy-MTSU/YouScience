import pandas as pd
import numpy as np
import random

# implementing random seed for control
np.random.seed(42)

# school names for consistency 
schools = ['Oakland Middle School',
    'Siegel Middle School',
    'Whitworth-Buchanan Middle School',
    'Christiana Middle School',
    'Smyrna Middle School',
    'Stewarts Creek Middle School',
    'Rockvale Middle School',
    'Rocky Fork Middle School',
    'Blackman Middle School',
    'Thurman Francis Arts Academy',
    'Rock Springs Middle School',
    'LaVergne Middle School'
]

capacity_report = {
    'School':[],
    'Status':[],
    'Assigned Capacity':[],
    '8th Graders':[],
    'Number of Large Rooms':[],
    'Number of Small Rooms':[]
}

# building capacity report
for school in schools:
    # read in planning document to get list of rooms
    if school == 'Whitworth-Buchanan Middle School':
        plan_df = pd.read_excel('/Users/amurphy/Documents/GitHub/YouScience/Deliverables/planning.xlsx', sheet_name='Whitworth-Buchanan Middle Schoo')
    else:
        plan_df = pd.read_excel('/Users/amurphy/Documents/GitHub/YouScience/Deliverables/planning.xlsx', sheet_name=school)
    # get the rooms per that school
    rooms = list(plan_df['MS Room #'])
    capacity = 0
    lg_rooms = 0
    sm_rooms = 0
    for room in rooms:
        try:
            if ('Library' in room) or ('Auditorium' in room):
                capacity += 50
                lg_rooms += 1
            else:
                capacity += 35
                sm_rooms += 1
        except TypeError:
            capacity += 35
            sm_rooms += 1

    # determine volume from YS match roster
    path = f'/Users/amurphy/Documents/GitHub/YouScience/Deliverables/YS_Criteria_by_School/{school} YSCriteria.csv'
    ys_df = pd.read_csv(path)
    volume = len(ys_df)

    # compile dictionary for report
    capacity_report['School'].append(school)
    if capacity >= volume:
        capacity_report['Status'].append('Ready')
    else:
        capacity_report['Status'].append('Insufficient Space')
    capacity_report['Assigned Capacity'].append(capacity)
    capacity_report['8th Graders'].append(volume)
    capacity_report['Number of Large Rooms'].append(lg_rooms)
    capacity_report['Number of Small Rooms'].append(sm_rooms)
    
cap_df = pd.DataFrame(capacity_report)
cap_df['Status'] = cap_df['Assigned Capacity'] > cap_df['8th Graders']

# Exporting capacity report
cap_df.to_csv('/Users/amurphy/Documents/GitHub/YouScience/YouScienceData/Reports/Capacity_Report.csv')