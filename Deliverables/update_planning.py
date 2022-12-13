import pandas as pd
import numpy as np
import random
import os

# implementing random seed for control
sd = 42
np.random.seed(sd)

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

# modified get demand function 
def get_POS_demand(school_pos_df):

    from collections import Counter
    C = Counter()
    for i in range(len(school_pos_df)):
        # read in student's POS
        student = school_pos_df.iloc[i]
        # compile list of POS
        pos_list = []
        for rank in ['First','Second','Third','Fourth','Fifth','Sixth']:
            if student[rank] not in pos_list:
                pos_list.append(student[rank])
        # update counter
        C.update(pos_list)


    return C

# uncouple function called in update
def uncouple_pos_matches(demand_counter_object):
# NE meanning Non-Empty matches, only
    NE_pos_list = [] 
    for pos in demand_counter_object:
        # the 0 comes from missing / empty matches
        if pos[0] == 0:
            continue
        
        # Break up the Coupled POS matches into separate, equally-demanded POS matches
        if ',' in pos[0]:
            # temp list of elements
            l = pos[0].split(', ')
            for match in l:
                NE_pos_list.append([match, pos[1]])
        # If not coupled, pass in as a list rather than tuple for decrement process later? 
        else:
            NE_pos_list.append(list(pos))

    return NE_pos_list

# update function
def update_planning_doc(school, lg_rooms):
    p_path = '/Users/amurphy/Documents/GitHub/YouScience/Deliverables/planning.xlsx'

    # read in planning.xlsx including the whitworth condition
    if school == 'Whitworth-Buchanan Middle School':
        planning_df = pd.read_excel(p_path, sheet_name=school[:-1])
    else:
        planning_df = pd.read_excel(p_path, sheet_name=school)
    
    # find the n most demanded and their original room numbers
    priority_pos_swap = {}
    no_swap = []
    pos_list = uncouple_pos_matches(school_demand[school]) # need to call function to split paired pos
    # up to {lg_rooms} reassignments can occur by demand priority
    for i in range(lg_rooms):
        x_pos = pos_list[i][0]
        no_swap.append(x_pos)
        x_previously_assigned_room = planning_df.loc[planning_df.POS == x_pos]['MS Room #'].values[0]
        # checking if already assigned to big room
        if type(x_previously_assigned_room) == int:
            pass
        elif ('Library' in x_previously_assigned_room) or ('Auditorium' in x_previously_assigned_room):
            continue # don't store for reassignment
        priority_pos_swap[x_pos] = x_previously_assigned_room

    # check the language for lg rooms, and their assigned POSs
    rooms_to_go = {}
    for room in list(planning_df['MS Room #'].values):
        if type(room) == int:
            continue
        elif ('Library' in room) or ('Auditorium' in room):
            to_go_pos = planning_df.loc[planning_df['MS Room #'] == room].POS.values[0]
            # checking to make sure not already a priority POS
            if to_go_pos in list(priority_pos_swap.keys()):
                # ensures room is not added to list to swap from
                continue
            rooms_to_go[to_go_pos] = room

    # determine newly assigned room #'s 
    to_replace = {}
    i,j = 0, 0
    for key in list(priority_pos_swap.keys()):
        # priority pos with new room
        to_replace[key] = list(rooms_to_go.values())[i]
        i+=1

    # condition that each priority pos is in a large room already, or that there are none available
    if priority_pos_swap == {}:
        print(f'{school} worksheet NO Changes available.')
        logf.write(f'{school} worksheet NO Changes available.')
        return no_swap

    for key in list(rooms_to_go.keys()):
        # to be reasigned pos with new room
        to_replace[key] = list(priority_pos_swap.values())[j]
        j+=1

    # reassign POS room #'s 
    for key in list(to_replace.keys()):
        planning_df.loc[planning_df.POS == key, 'MS Room #'] = to_replace[key]

    # update planning.xslx (EDIT include condition for whitworth!!!!!!!!!!)
    with pd.ExcelWriter(p_path,engine="openpyxl",mode="a", if_sheet_exists='replace') as writer:
        if school == 'Whitworth-Buchanan Middle School':
            planning_df.to_excel(excel_writer=writer,sheet_name=school[:-1])
        else:
            planning_df.to_excel(excel_writer=writer,sheet_name=school)
    
    print(f'{school} worksheet updated in planning.xlsx')
    logf.write(f'{school} worksheet updated in planning.xlsx')
    return to_replace

# read in capacity_report.csv
c_path = '/Users/amurphy/Documents/GitHub/YouScience/YouScienceData/Reports/Capacity_Report.csv'
cap_df = pd.read_csv(c_path)

# creating demand report for checking in the future
schools_pos_most_demanded = {}

l_path = '/Users/amurphy/Documents/GitHub/YouScience/YouScienceData/Reports/planning_update.txt'
with open(l_path,'w') as logf:

    # iterate through school checklist
    for school in schools:
        # get # of large rooms
        lg_rooms = cap_df.loc[cap_df.School == school]['Number of Large Rooms'].values[0]
        schools_pos_most_demanded[school] = update_planning_doc(school=school, lg_rooms=lg_rooms)

    logf.write('-Schools POS in demand per number of large rooms-')
    for school in schools:
        logf.write(f'{school}:\n')
        i = 1
        if type(schools_pos_most_demanded[school]) == list:
            for pos in schools_pos_most_demanded[school]:
                logf.write(f'{i}. {pos}')
                i+=1
        else:
            for pos in list(schools_pos_most_demanded[school].keys()):
                logf.write(f'{i}. {pos}, {schools_pos_most_demanded[school][pos]}')
                i+=1

logf.close()