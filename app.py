import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#load dataset
#import data
gpa_raw = pd.read_csv('https://raw.githubusercontent.com/wadefagen/datasets/master/gpa/uiuc-gpa-dataset.csv')
#manipulate data
##add two columns: quality points and class size
gpa_raw['quality points'] = gpa_raw['A+']*4 + gpa_raw['A']*4 + gpa_raw['A-']*3.67 + gpa_raw['B+']*3.33 + gpa_raw['B']*3 + gpa_raw['B-']*2.67 + gpa_raw['C+']*2.33+ gpa_raw['C']*2 + gpa_raw['C-']*1.67 + gpa_raw['D+']*1.33 + gpa_raw['D']*1 + gpa_raw['D-']*0.67
gpa_raw['class size'] = gpa_raw['A+'] + gpa_raw['A'] + gpa_raw['A-'] + gpa_raw['B+'] + gpa_raw['B'] + gpa_raw['B-'] + gpa_raw['C+'] + gpa_raw['C'] + gpa_raw['C-'] + gpa_raw['D+'] + gpa_raw['D'] + gpa_raw['D-'] + gpa_raw['F'] + gpa_raw['W']
#Use groupby Mechanics to calculate gpa by class 
quality_points_sum = gpa_raw['quality points'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum()
class_size_sum = gpa_raw['class size'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum()
gpa_by_instructor = quality_points_sum/class_size_sum
#
gbi_df = gpa_by_instructor.reset_index()
gbi_df = gbi_df.rename(columns = {0:"GPA"})
#
#add number of students column to gbi_df
student_sum = class_size_sum.reset_index()
gbi_df = pd.merge(gbi_df, student_sum)
gbi_df = gbi_df.rename(columns = {"class size":"Students"})


#add each grade frequencies to gbi_df
ap_sum = gpa_raw['A+'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, ap_sum)
a_sum = gpa_raw['A'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, a_sum)
am_sum = gpa_raw['A-'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, am_sum)
bp_sum = gpa_raw['B+'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, bp_sum)
b_sum = gpa_raw['B'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, b_sum)
bm_sum = gpa_raw['B-'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, bm_sum)
cp_sum = gpa_raw['C+'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, cp_sum)
c_sum = gpa_raw['C'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, c_sum)
cm_sum = gpa_raw['C-'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, cm_sum)
dp_sum = gpa_raw['D+'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, dp_sum)
d_sum = gpa_raw['D'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, d_sum)
dm_sum = gpa_raw['D-'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, dm_sum)
f_sum = gpa_raw['F'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, f_sum)
w_sum = gpa_raw['W'].groupby([gpa_raw['Primary Instructor'], gpa_raw['Course Title']]).sum().reset_index()
gbi_df = pd.merge(gbi_df, w_sum)



#Remove unnecessary columns from gpa_raw
gpa_raw_filtered = gpa_raw.drop(['Year','Term','YearTerm','A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W','quality points','class size'],axis=1)
#



#merge gbi_df and gpa_raw
df = pd.merge(gbi_df, gpa_raw_filtered, how='left').drop_duplicates(subset=['Course Title', 'Primary Instructor'])
df = df.sort_values(by=['Subject','Number'])
#move columns, Subject and Number, to the front
subject_column = df['Subject']
df.drop(labels=['Subject'], axis=1, inplace = True)
df.insert(0, 'Subject', subject_column)
number_column = df['Number']
df.drop(labels=['Number'], axis=1, inplace = True)
df.insert(1, 'Number', number_column)
#all the above
#
#

app.layout = html.Div([
    #Subject Dropdown
    html.Label("Subject:"),
    
    dcc.Dropdown(
        id='subject-dpdn',
        options=[{'label': k, 'value': k} for k in df['Subject'].unique()],
        value='STAT',
        clearable=False #no x button for dropdown
    ),

    html.Hr(),
    #Number Dropdown
    html.Label("Number:"),
    
    dcc.Dropdown(id='number-dpdn', options=[], multi=False),

    html.Hr(),
    #Graph
    dcc.Graph(id='display-bar')
])

#1st callback - subject
@app.callback(
    Output('number-dpdn', 'options'),
    Input('subject-dpdn', 'value')
)
def set_number_options(selected_subject): #argument, selected_subject, refers to the 'value' right above
    dff = df[df.Subject == selected_subject]
    return [{'label': i, 'value': i} for i in dff['Number'].unique()] #this list is the list of options, for number dropdown

#2nd callback - number
@app.callback(
    Output('number-dpdn', 'value'),
    Input('number-dpdn', 'options')
)
def set_number_value(available_options):
    return [x['value'] for x in available_options]

#3rd callback - final
@app.callback(
    Output('display-bar', 'figure'),
    Input('number-dpdn', 'value'),
    Input('subject-dpdn', 'value')
)

def update_grpah(chosen_number, chosen_subject):
    try:
        filtered_df = df[(df.Subject==chosen_subject)]
        filtered_df = filtered_df.loc[filtered_df['Number'] == chosen_number]

    except ValueError:
        pass
    return px.bar(filtered_df, x='GPA', y='Primary Instructor', title = "Grade Difference Between Different Sections", range_x=(0,4), color = 'Students', color_continuous_scale = "redor", height = 800, labels = {'Primary Instructor':'Instructors'}, hover_data = ['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W'])



if __name__ == '__main__':
    app.run_server(debug=True)