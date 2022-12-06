#Libraries Required
import PySimpleGUI as sg
import os
import time
import datetime as dt
import logging as lg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#==============================================================================
#File for logging
#App warnings and errors are logged here for maintenance
lg.basicConfig(filename='Water_UI_debug.log', encoding='utf-8', level=lg.DEBUG)
lg.debug('Log file for Water App, start '+ time.asctime())
#===============================================================================
#Aesthetics
sg.theme('BlueMono')
#===============================================================================
class SourceFile:
    '''This class will store the information of the file loaded.'''
    def __init__(self,sourcefile):
        self.DR=dict()
        try:
            df=open(sourcefile, 'r')
            records=[]
            for line in df.readlines():
                records.append(line.strip().split(','))
            df.close()
            lg.info('File load successful')
        except:
            lg.warning('Source file not loaded')
        try:
            for k in range(len(records[0])):#top line
                self.DR[(records[0][k]).replace('"','')]=[
                    float(records[w][k]) if (records[w][k]).replace('.','').isnumeric() else (records[w][k]).replace('"','') for w in range(1,len(records))]
        except:
            lg.warning('File content problem')     
#=============================================================================
def WQI_calc(x):
    '''This function calculates water quality index.
The method of calculation can be updated as per latest research'''
    #pH,TDS,TH,Bicarbonate,Chloride,Sulphate,Nitrate,Fluoride,Calcium,Magnesium,Iron,Manganese,Zinc
    #component weights(higher weight-more important)
    wgt=[4,4,2,3,3,4,5,4,2,2,4,4,1]
    #government accepted standard values
    st_val=[7.5,1250,450,488,625,300,72.5,1.25,137.5,65,0.65,0.2,10]
    qv=0
    sv=0
    for k in range(len(x)):
        if x[k]!=-1:#include only the measurements available
            qv=qv+(x[k]/st_val[k])*wgt[k]
            sv=sv+wgt[k]
    return(round(qv/sv,2))
#=========================================================================
data_2=[['Source Name',-1]]
#=========================================================================
#GUI Design
#=========================================================================
#Tabbed Layout
layout1 = [[sg.Text('Profiling Panel')],#static
           [sg.Text('Choose Source File'),
            sg.FileBrowse(key='sourcefile_1')],
           [sg.Button('Load Samples Data')],
           [sg.OptionMenu(values=['Parameter'],
                          default_value='',
                          key='Prm'),
            sg.Button('Display Comparisons')],
           [sg.Canvas(size=(400,400),
                     key='valuegraph')]]

layout2 = [[sg.Text('Calculator Panel')],#static
           [sg.Text('Choose Source File'),
            sg.FileBrowse(key='sourcefile_2')],
           [sg.Button('Load Data for WQI')],
           [sg.Button('Display WQI')],
           [sg.Table(values=data_2,
                     headings=['Name','WQI'],
                     key='TABLE_2',
                     display_row_numbers=True,
                     auto_size_columns=False,
                     enable_events=True)]]

layout3 = [[sg.Text('Time Series Panel')],#static
           [sg.Text('Choose Source File'),
            sg.FileBrowse(key='sourcefile_3')],
           [sg.Button('Load Periodic Measurements')],
           [sg.Button('Display Time Series')],
           [sg.Canvas(size=(400,400),
                     key='timegraph')]]

layout4 = [[sg.Text('Chlorophyll Panel')],#static
           [sg.Text('Choose Lake'),
            sg.OptionMenu(values=['L','R','T'],
                          default_value='',
                          key='lake')],
           [sg.Text('Choose Year'),
            sg.OptionMenu(values=['2013','2014','2015'],
                          default_value='',
                          key='yr')],
           [sg.Button('Load Chlorophyll Values')],
           [sg.Button('Display Chart')],
           [sg.Canvas(size=(400,400),
                     key='chlagraph')]]

tabgroups=[[sg.TabGroup([[sg.Tab('Data Profiling',layout1),
                          sg.Tab('WQI Calculator',layout2),
                          sg.Tab('WQI Change over time',layout3),
                          sg.Tab('Chlorophyll Values',layout4)]],
                        tab_location='centertop'
                        ),sg.Button('Exit')]]

window = sg.Window('Water Quality App', tabgroups,
                   finalize=True,element_justification='center')
#==============================================================================
f1=plt.Figure(figsize=(5,5))
ax1=f1.add_subplot(111)
fig_cnv_agg_1=FigureCanvasTkAgg(f1,window['valuegraph'].TKCanvas)

f2=plt.Figure(figsize=(5,5))
ax2=f2.add_subplot(111)
fig_cnv_agg_2=FigureCanvasTkAgg(f2,window['timegraph'].TKCanvas)

f3=plt.Figure(figsize=(5,5))
ax3=f3.add_subplot(111)
fig_cnv_agg_3=FigureCanvasTkAgg(f3,window['chlagraph'].TKCanvas)

while True:
    event, values = window.read()

    if event == 'Exit':
        lg.info('Close down through Exit Button')
        break
    if event == sg.WIN_CLOSED:
        lg.info('Close down through Red Cross')
        break
    #==========================================================================
    #Data Loading
    #==========================================================================
    if event == 'Load Samples Data':
        AT1=SourceFile(values['sourcefile_1'])
        try:
            window['Prm'].update(values=sorted(list(set(AT1.DR['Parameter']))))
        except:
                lg.warning('Relevant content not found, Load error')
    if event == 'Load Data for WQI':
        AT2=SourceFile(values['sourcefile_2'])
        try:
            window['Prm'].update(values=sorted(list(set(AT2.DR['Parameter']))))
        except:
                lg.warning('Relevant content not found, Load error')
    if event == 'Load Periodic Measurements':
        AT3=SourceFile(values['sourcefile_3'])
        try:
            window['Prm'].update(values=sorted(list(set(AT3.DR['Parameter']))))
        except:
                lg.warning('Relevant content not found, Load error')
    if event == 'Load Chlorophyll Values':
        datapath="C:\\Users\\Rayjay\\OneDrive\\Documents\\CIND 820"
        AT4=SourceFile(datapath+'\\bilstm_chlapred'+values['lake']+'_'+values['yr']+'.csv')
    #==========================================================================
    #Graph building/table building
    #==========================================================================
    if (event=='Display Comparisons'):
        place_names=[]
        chosen_value=[]
        try:
            colnames=[w for w in AT1.DR.keys()]
            place_names=[AT1.DR["Name"][k] for k in range(len(AT1.DR["Name"])) if AT1.DR["Parameter"][k]==values['Prm']]
            chosen_value=[AT1.DR["Measure"][k] for k in range(len(AT1.DR["Name"])) if AT1.DR["Parameter"][k]==values['Prm']]

            ax1.cla()
            ax1.barh(place_names,chosen_value)
            ax1.set_title('Comparison:'+values['Prm'])
            fig_cnv_agg_1.draw()
            fig_cnv_agg_1.get_tk_widget().pack(side='top',fill='both',expand=0)
            window.refresh()
        except:
            lg.warning('Relevant content not found, Display error')
    #==========================================================================
    if (event=='Display WQI'):
        try:
            data_2=[]
            for k in range(len(AT2.DR['Name'])):
                x=[AT2.DR['pH'][k] if 'pH' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['TDS'][k] if 'TDS' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['TH'][k] if 'TH' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Bicarbonate'][k] if 'Bicarbonate' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Chloride'][k] if 'Chloride' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Sulphate'][k] if 'Sulphate' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Nitrate'][k] if 'Nitrate' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Fluoride'][k] if 'Fluoride' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Calcium'][k] if 'Calcium' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Magnesium'][k] if 'Magnesium' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Iron'][k] if 'Iron' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Manganese'][k] if 'Manganese' in AT2.DR.keys() else -1 for w in range(1)]+[AT2.DR['Zinc'][k] if 'Zinc' in AT2.DR.keys() else -1 for w in range(1)]
                data_2.append([AT2.DR['Name'][k],WQI_calc(x)])
            
            window['TABLE_2'].update(values=data_2)
            window.refresh()
        except:
            lg.warning('Relevant content not found, Display error')
    #===========================================================================
    if (event=="Display Time Series"):
        try:
            event_period=[]
            wqi_value=[]
            for k in range(len(AT3.DR['Name'])):
                x=[AT3.DR['pH'][k] if 'pH' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['TDS'][k] if 'TDS' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['TH'][k] if 'TH' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Bicarbonate'][k] if 'Bicarbonate' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Chloride'][k] if 'Chloride' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Sulphate'][k] if 'Sulphate' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Nitrate'][k] if 'Nitrate' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Fluoride'][k] if 'Fluoride' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Calcium'][k] if 'Calcium' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Magnesium'][k] if 'Magnesium' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Iron'][k] if 'Iron' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Manganese'][k] if 'Manganese' in AT3.DR.keys() else -1 for w in range(1)]+[AT3.DR['Zinc'][k] if 'Zinc' in AT3.DR.keys() else -1 for w in range(1)]
                event_period.append(dt.datetime.strptime(AT3.DR['ActivityStartDate'][k], '%d-%m-%Y'))
                wqi_value.append(WQI_calc(x))

            ax2.cla()
            ax2.plot(event_period,wqi_value)
            ax2.set_title('Time Series')
            fig_cnv_agg_2.draw()
            fig_cnv_agg_2.get_tk_widget().pack(side='top',fill='both',expand=0)
            window.refresh()
        except:
            lg.warning('Relevant content not found, Display error')
    #============================================================================
    if (event=="Display Chart"):
        try:
            event_period=[]
            actual_value=[]
            predicted_value=[]
            for k in range(len(AT4.DR['DoY'])):
                event_period.append(AT4.DR['DoY'][k])
                actual_value.append(AT4.DR['Actual'][k])
                predicted_value.append(AT4.DR['Predicted'][k])

            ax3.cla()
            ax3.plot(event_period,actual_value,color='xkcd:blue green')
            ax3.scatter(event_period,predicted_value,s=10,c='xkcd:dark orange')
            ax3.set_title('Chlorophyll Values')
            fig_cnv_agg_3.draw()
            fig_cnv_agg_3.get_tk_widget().pack(side='top',fill='both',expand=0)
            window.refresh()
        except:
            lg.warning('Relevant content not found, Display error')
    #=============================================================================
lg.info('App close down')        
window.close()
