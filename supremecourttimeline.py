import pandas as pd
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import numpy as np
from bokeh.models import BoxAnnotation, Label, Panel, Tabs, Span

data_full = pd.read_csv('Supreme Court Data - Sheet1.csv')
data = data_full[data_full['Result & Date***']=='C']
data = data.dropna(subset=['Last day of predeccessor'])
data = data[data['Last day of predeccessor']!='New Seat']
data = data[data['Last day of predeccessor']!='N/A']

data['Judge Name'] = data['Last'] + ', ' + data['First']
data['Judge Name'] = data['Judge Name'].astype(str)

data['Oath Date'] = pd.to_datetime(data['Oath Date'])
data['Confirm Date'] = pd.to_datetime(data['Unnamed: 9'])
data['Recess Hover'] = np.where(data['Oath Date']<data['Confirm Date'], 'Took oath after recess appointment on ' +data['Oath Date'].astype(str) + ', '+data['Gap Last Day to Oath Date'] + ' days after  ' + data['Last day of predeccessor'].astype(str) + ' the last day that ' + data['To Replace'] + ' served on the court.', '')
data['Recess'] = np.where(data['Oath Date']<data['Confirm Date'], data['Gap Last Day to Oath Date'], data['Gap Last Day to Nominate'])
data['Gap Last Day to Oath Date'] = np.where(data['Oath Date']<data['Confirm Date'], data['Gap Last Day to Confirm Vote'], data['Gap Last Day to Oath Date'])
print(data.columns)

hover_text_nom_pos = 'Nomination sent to senate on ' + data['Nominated*'].astype(str) + ', ' + data['Gap Last Day to Nominate'] + ' days after ' + data['Last day of predeccessor'].astype(str) + ', the last day that ' + + data['To Replace'] + ' served on the court.'
hover_text_nom_neg = 'Nomination sent to senate on ' + data['Nominated*'].astype(str) + ', ' + data['Gap Last Day to Nominate'].astype(str) + ' days before ' + data['Last day of predeccessor'].astype(str) + ', the last day that ' + + data['To Replace'] + ' served on the court.'

hover_text_con_pos = 'Confirmed by senate on ' + data['Unnamed: 9'].astype(str) + ', ' + data['Gap Last Day to Confirm Vote'] + ' days after ' + data['Last day of predeccessor'].astype(str) + ', the last day that ' + + data['To Replace'] + ' served on the court.'
hover_text_con_neg = 'Confirmed to senate on ' + data['Unnamed: 9'].astype(str) + ', ' + data['Gap Last Day to Confirm Vote'].astype(str) + ' days before ' + data['Last day of predeccessor'].astype(str) + ', the last day that ' + + data['To Replace'] + ' served on the court.'

hover_text_oath_pos = 'Oath taken on ' + data['Oath Date'].astype(str) + ', ' + data['Gap Last Day to Oath Date'] + ' days after ' + data['Last day of predeccessor'].astype(str) + ', the last day that ' + + data['To Replace'] + ' served on the court.'
#hover_text_oath_neg = 'Oath taken on ' + data['Oath Date'] + ', ' + data['Gap Last Day to Oath Date'].astype(int)*-1 + ' days before ' + data['Last day of predeccessor'] + ', the last day that ' + + data['To Replace'] + ' served on the court.'

data['Nominate Hover'] = np.where(data['Gap Last Day to Nominate'].astype(int)>0,hover_text_nom_pos, hover_text_nom_neg)
data['Confirm Hover'] = np.where(data['Gap Last Day to Confirm Vote'].astype(int)>0,hover_text_con_pos, hover_text_con_neg)
data['Oath Hover'] = np.where(data['Oath Date']<data['Confirm Date'],'',hover_text_oath_pos)

data_post1900 = data[data['Oath Date'] > '01-01-1920']
data_deaths = data[data['Reason Left'] == 'D']
data_dems = data[data['Party']=='D']
data_reps = data[data['Party']=='R']


def get_graph(data):
    data['Judge Name'] = data['Last'] + ', ' + data['First']
    data['Judge Name'] = data['Judge Name'].astype(str)

    data = data.drop_duplicates(subset=['Judge Name'])
    judge_names = data['Judge Name'].values

    tooltips = [('', '@{Recess Hover}'),
                ('', '@{Nominate Hover}'),
                ('', '@{Confirm Hover}'),
                ('', '@{Oath Hover}')]
    source = ColumnDataSource(data)
    fig =figure(y_range = judge_names, height = 1600, width = 1200, tooltips=tooltips)
    fig.hbar(left = 'Recess', right = 'Gap Last Day to Nominate', y='Judge Name', source=source, color='#00BFB2', height=0.8, legend='Recess Appointment to Official Submission of Nomination to Senate')
    fig.hbar(left = 'Gap Last Day to Nominate', right = 'Gap Last Day to Confirm Vote', y='Judge Name', source=source, color='#028090', height=0.8, legend='Nomination to Confirmation')
    fig.hbar(left='Gap Last Day to Confirm Vote', right = 'Gap Last Day to Oath Date', y='Judge Name', source=source, color='#C64191', height=0.8, legend='Confirmation to Oath')
    fig.circle(x = 'First Judge Nom', y='Judge Name', source=source, color='black', radius=5, legend='Previous Non-Confirmed Nomination')
    fig.circle(x='Second Judge Nom', y='Judge Name', source=source, color='black', radius=5,
               legend='Previous Non-Confirmed Nomination')
    fig.circle(x='Third', y='Judge Name', source=source, color='black', radius=5,
               legend='Previous Non-Confirmed Nomination')
    fig.circle(x='Fourth', y='Judge Name', source=source, color='black', radius=5,
               legend='Previous Non-Confirmed Nomination')
    fig.circle(x='Fifth', y='Judge Name', source=source, color='black', radius=5,
               legend='Previous Non-Confirmed Nomination')
    fig.xaxis.axis_label = 'Days After (or Before) Predecessor''s Final Day on Court'
    fig.legend.title = 'Number of Days between Predecessor''s Last Day and:'
    fig.add_layout(fig.legend[0], 'right')


    ticks = [0, 46, 104, 123, 365, 730]
    fig.xaxis[0].ticker = ticks
    fig.xgrid[0].ticker = ticks

    mid_box = BoxAnnotation(left=46, right=123, fill_alpha=0.1, fill_color='green')
    fig.add_layout(mid_box)

    gb_citation = Label(x=400, y=1300, x_units='screen', y_units='screen',
                     text='Green box starts on election day 2020 (43 days after death of RBG) and ends on inauguration day 2021 (123 days). (104 days until new senate is sworn in)', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)

    bl_citation = Label(x=400, y=1350, x_units='screen', y_units='screen',
                     text='Black dashed line represents the last day served by the previous justice', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)

    fig.add_layout(gb_citation)
    fig.add_layout(bl_citation)

    fig.xaxis.major_label_orientation = "vertical"

    xhighlight = Span(location=0,
                                dimension='height', line_color='black',
                                line_dash='dashed', line_width=3)
    fig.add_layout(xhighlight)

    fig.toolbar.logo = None
    fig.toolbar_location = None
    return fig

tab1 = Panel(child=get_graph(data), title="All Confirmed Judges")
tab2 = Panel(child=get_graph(data_deaths), title="Judges Who Replaced a Justice Who Died While Serving")
tab3 = Panel(child=get_graph(data_post1900), title="Judges Last 100 Years")
tab4 = Panel(child=get_graph(data_dems), title="Judges Nominated By a Democrat President")
tab5 = Panel(child=get_graph(data_reps), title="Judges Nominated By a Republican President")
show(Tabs(tabs=[tab1,tab2,tab3, tab4, tab5]))