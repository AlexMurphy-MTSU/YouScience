import pandas as pd
import numpy as np
import random
import os 

# implementing random seed for control
np.random.seed(42)

# school names for consistency 
schools = ['Oakland Middle School',
    'Siegel Middle School',
    'Whitworth-Buchanan Middle School',
    'Christiana Middle School',
    # 'Smyrna Middle School',
    # 'Stewarts Creek Middle School',
    'Rockvale Middle School',
    'Rocky Fork Middle School',
    'Blackman Middle School',
    # 'Thurman Francis Arts Academy',
    'Rock Springs Middle School',
    'LaVergne Middle School'
]

# capacity report features
capacity_report = {
    #(A-E)
    'School':[],
    'Capacity Status':[],
    'Pathway Status':[],
    'Assigned Default Capacity':[],
    'Assigned Max Capacity':[],
    '8th Graders':[],
    # 'Number of Large Rooms':[],
    # 'Number of Small Rooms':[],
}

capacity_vector_report = {
    #(F-G)
    'School':[],
    'Capacity_Vector':[],
}

# getting event year for file pathways
try:
    event_year = int(input('Enter 4-digit year of YouScience Event\n'))
except ValueError:
    event_year = 2022
print(f"Running for YS Career Fair {event_year}")

# copy of extract function that unpacks cap vector objects
def extract_capacity_vector(school):
    # read in capacity vector object 
    df = pd.read_csv('../YouScienceData/Reports/capacity_vectors.csv')
    df.drop("Unnamed: 0", axis=1, inplace=True)

    # inital object is long str
    vector_str = df.loc[df.School == school, "Capacity_Vector"].values[0]
    if vector_str == '{}':
        print(f'{school} missing data.')
        return 0
    # transforms it into list of room: cap strings
    vector_list = vector_str.split(', ')

    # transforming into actionable dictionary vector
    vector_dict = {}
    for item in vector_list:
        k, v = item.split(': ')
        # checking for first item to have '{'
        if '{' in k:
            k = k[1:]
        # checking for last item to have '}' 
        if '}' in v:
            v = v[:-1]
        try:
            vector_dict[int(k)] = int(v)
        except ValueError:
            # shave off quotations 
            vector_dict[k[1:-1]] = int(v)
    
    return {k: v for k, v in sorted(vector_dict.items(), key=lambda item: item[1], reverse=True)}

# EDIT: 1/12/23 by Murphy, clause for checking if number of rooms >= num of Pathways offered
djpath = '/Users/amurphy/Documents/GitHub/YouScience/direct_join_prepared.xlsx'
dj_df = pd.read_excel(djpath)

# building capacity report AND building capacity vector
for school in schools:
    # read in planning document
    p = '/Users/amurphy/Documents/GitHub/YouScience/Deliverables/planning.xlsx'
    
    try:
        if school == 'Whitworth-Buchanan Middle School':
            planning_df = pd.read_excel(p,sheet_name='Whitworth-Buchanan Middle Schoo')
        else:
            planning_df = pd.read_excel(p,sheet_name=school)
    except:
        continue

    # EDIT: 1/12/23 by Murphy, clause for checking if number of rooms >= num of Pathways offered
    pathways_grouped = list(dj_df[dj_df[school].notna()][school])
    pathways_uncoupled = []
    for pos in pathways_grouped:
        l = pos.split(', ')
        if len(l)>1:
            for x in l:
                pathways_uncoupled.append(x)
        else:
            pathways_uncoupled.append(l[0])
    avail_rooms = [x for x in list(planning_df['MS Room Number']) if "(if needed)" not in str(x)]
    num_pathways = len(set(pathways_uncoupled))
    num_avail_rooms = len(avail_rooms)
    num_all_rooms = planning_df['MS Room Number'].notna().sum()
    avail_check = num_avail_rooms - num_pathways
    all_check = num_all_rooms - num_pathways
    if avail_check >= 0:
        pos_status = f'{avail_check} Extra Rooms'
    elif all_check >= 0:
        pos_status = f'{all_check} Extra Rooms with "if needed"'
    else:
        pos_status = f'{abs(all_check)} More Pathways Than all Rooms'
    capacity_report['Pathway Status'].append(pos_status)
    # END EDIT: 1/16/23 (fixed repeated POS, reinstated check for "if needed" rooms)

    #(A,F)
    capacity_report['School'].append(school)
    capacity_vector_report['School'].append(school)

    #(D)
    max_cap = sum(list(planning_df['Max Room Capacity']))
    capacity_report['Assigned Max Capacity'].append(max_cap)

    #(E)
    # read in skyward roster for length, NOTE: currently reading from desktop folder
    try:
        sky_p = f'/Users/amurphy/Documents/GitHub/YouScience/YouScienceData/Skyward/{event_year-1}-{event_year}/Skyward_{school}.xlsx'
        sky_df = pd.read_excel(sky_p)
        volume = len(sky_df.drop_duplicates("Student's School Email")) # necessary! 
        capacity_report['8th Graders'].append(volume)
    except FileNotFoundError:
        print(f'No Skyward rosters available for year: {event_year}. Report cancelled...')
        quit()
    
    #(C), (G), pt. 1 set for default rooms
    capacity_vector = {}
    default_rooms, if_needed_rooms = [], [] # need this for building capacity vector if not using all rooms
    default_capacity = 0
    for room in list(planning_df['MS Room Number']):
        cap = planning_df.loc[planning_df['MS Room Number'] == room, 'Max Room Capacity'].values[0]
        if "(if needed)" not in str(room):
            default_rooms.append(room)
            default_capacity += cap
            capacity_vector[room] = cap
        else:
            if_needed_rooms.append(room)
    capacity_report['Assigned Default Capacity'].append(default_capacity)
    
    #(B) - determining status, NOTE: this does not reflect capcity to meet demand for pathways of study
    diff = default_capacity - volume
    abs_diff = max_cap - volume
    if diff > 0:
        status = ['Sufficient',0]
    elif diff < 0 and abs_diff < 0:
        status = ['Insufficient',1]
    else:
        status = ['Suff. w/ All',2]
    capacity_report['Capacity Status'].append(status[0])

    #(G), pt. 2 - checking if we need to add conditionally assigned rooms
    if status[1] != 0: # NOT use only default
        for room in if_needed_rooms:
            cap = planning_df.loc[planning_df['MS Room Number'] == room, 'Max Room Capacity'].values[0]
            capacity_vector[room] = cap

    #(G), pt. 3 sorting capacity vector in descending order, gets sorted on unpacking
    # capacity_vector = {k: v for k, v in sorted(capacity_vector.items(), key=lambda item: item[1])}
    capacity_vector_report['Capacity_Vector'].append(capacity_vector)
    
# verifying export paths
export_p = f'/Users/amurphy/Documents/GitHub/YouScience/YouScienceData/Reports/{event_year}/'
if not os.path.exists(export_p):
    os.makedirs(export_p)

# exporting capacity report
export_report_p = f'{export_p}Capacity_Report.csv'
pd.DataFrame(capacity_report, columns=list(capacity_report.keys())).to_csv(export_report_p)

# exporting capacity vectors
export_vectors_p = f'{export_p}capacity_vectors.csv'
pd.DataFrame(capacity_vector_report, columns=list(capacity_vector_report.keys())).to_csv(export_vectors_p)