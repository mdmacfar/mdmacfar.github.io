

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.offline as pyo
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown1 = '''The gender wage gap is a topic of attention in the United States and the subject of a good deal of research and writing.

As an example, in a recent report (https://www.pewresearch.org/short-reads/2023/03/01/gender-pay-gap-facts/), Pew Research found that 
the gap in pay between genders has stayed consistent since 2002 with women earning an average of 82% of what men earn. The 
report goes on to suggest that women being treated differently by employers is one of the main reasons for the gap.

Another recent report by the US Department of Labor (https://blog.dol.gov/2023/03/14/5-fast-facts-the-gender-wage-gap) found substantial
differences between genders across different education levels. It also noted that the gap is more significant for Black and Hispanic women. 
One of the main contributors noted is the fact that men are less likely to work in lower-paying jobs that offer less benefits.

The General Social Survey (GSS) is a survey conducted by the National Opinion Research Center (University of Chicago) that has been 
ongoing since 1972. The survey contains demographic, behavioral, and many other topics and is conducted with an extremely robust methodology.
Their process begins by creating representative sample groups, collecting data, randomizing, documenting and tracking, analyzing, 
and publishing.

The goal of this dashboard is to explore data found in the GSS about the gender wage gap and present visualizations for those findings.'''


means = gss.groupby('sex')[['income', 'job_prestige', 'socioeconomic_index', 'education']].mean()
means = means.round(2)
means = means.rename(columns={'income': 'Income',
                                'job_prestige': 'Occupational Prestige',
                                'socioeconomic_index': 'Socioeconomic Index',
                                'education': 'Education'})


table_fig = ff.create_table(means.reset_index(),
                            index_title='Sex')

table_fig.update_layout(title='Mean Values for Men and Women')



order3 = ['strongly disagree', 'disagree', 'agree', 'strongly agree']
counts3 = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index(name='Count')



barplot3=px.bar(counts3, x='male_breadwinner', y='Count', color='sex',
                    labels={'male_breadwinner': 'Agreement Level', 'Count': 'Count'},
                    category_orders={'male_breadwinner': order3})


scatterplot4=px.scatter(gss_clean, x='job_prestige', y='income', color='sex', trendline='lowess',
                            labels={'job_prestige': 'Job Prestige', 'income': 'Income'},
                            hover_data=['education', 'socioeconomic_index'])

boxplot5a=px.box(gss_clean, x='sex', y='income',
                      labels={'income': 'Income'})

boxplot5b=px.box(gss_clean, x='sex', y='job_prestige',
                      labels={'job_prestige': 'Job Prestige'})



df6 = gss_clean[['income', 'sex', 'job_prestige']].copy()
df6['job_prestige_cat'] = pd.cut(df6['job_prestige'], bins=6, labels=False)
df6 = df6.dropna()



prestige_cat_range = df6.groupby('job_prestige_cat')['job_prestige'].agg(['min', 'max'])



facet_lab = ['Category 1 (Range: 0-26)',
                'Category 2 (Range: 27-37)',
                'Category 3 (Range: 38-48)',
                'Category 4 (Range: 49-58)',
                'Category 5 (Range: 59-69)',
                'Category 6 (Range: 70-100)']


df6['job_prestige_cat'] = df6['job_prestige_cat'].replace([0,1,2,3,4,5],facet_lab)


df6 = df6.sort_values(by='job_prestige_cat')
facet6=px.box(df6, x='sex', y='income', color='sex', facet_col='job_prestige_cat', facet_col_wrap=2,
              labels={'job_prestige_cat': 'Job Prestige Category', 'income': 'Income'},
              category_orders={'sex': ['male', 'female']},
              color_discrete_map={'male': 'blue', 'female': 'red'})
facet6.update_layout(showlegend=False)
facet6.update_layout(grid=dict(rows=3, columns=2))
facet6.update_layout(height=1000)


app = JupyterDash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        html.H1("Findings on the Gender Wage Gap from the General Social Survey"),
        
        dcc.Markdown(children = markdown1),
        
        html.H2("Mean Income, Occupational Prestige, Socioeconomic Index, and Education by Gender"),
        
        dcc.Graph(figure=table_fig),
        
        html.H2('Answer to the question: "Agree or disagree with: It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."'),
        
        dcc.Graph(figure=barplot3),
        
        html.H2("Job Prestige vs Income by Gender"),
        
        dcc.Graph(figure=scatterplot4),
        
        html.Div([
            
            html.H2("Income by Gender"),
            
            dcc.Graph(figure=boxplot5a)
            
        ], style = {'width':'50%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Job Prestige by Gender"),
            
            dcc.Graph(figure=boxplot5b)
            
        ], style = {'width':'50%', 'float':'right'}),
                
        html.H2("Income by Gender and Job Prestige Category"),
        
        dcc.Graph(figure=facet6),
        
    
    ]
)


if __name__ == '__main__':
    app.run_server(mode='inline', debug=True, port=8050)


html_filename = 'dashboard_output.html'
pyo.plot(app, filename=html_filename)

import os
os.remove(html_filename)
