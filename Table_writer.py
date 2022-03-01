from pip import main
from tabulate import tabulate
from datetime import datetime
import re
import pandas as pd
import xnat
from xnat.core import CustomVariableMap

def read_table():

    data_dict = {}
    data = pd.read_table('Custom_Variables.txt', delimiter='\s\s+', header=[0], skiprows=1,
        dtype={'Variable': str}, engine='python').values.tolist()
    for elem in data:
        data_dict[elem[0]] = elem[1]
    return

def write_table():
    with open('Custom_Variables.txt', 'w+') as meta_file:
        meta_file.write(tabulate([['Project', 'CEST'], ['Subject', 'da_PyMT_5'], ['Acquisition_date', datetime.now()], 
            ['Group', 'Control'], ['Dose', 1], ['Timepoint', 'Post 3 weeks']], headers=['Variable', 'Value']))
    return

def read_project():
    with xnat.connect(server='http://130.192.212.48:8080/', user='Cim-5', password='Imaging2022') as session:
        project = session.classes.ProjectData(
                                    name='Project_1', parent=session
                                    )

        subject = session.classes.SubjectData(
                                        parent=project, label='da_PyMT_5'
                                    )
        subject.fields['group'] = 'control'

        experiment = session.classes.ExperimentData(
                                        parent=subject, label='da_PyMT_5_20190327_134300'
                                    )
        experiment.fields['group'] = 'control'
        
        print('End')
    session.disconnect()
    print('End')

# write_table()
read_project()
read_table()