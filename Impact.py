#%%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
from scipy.stats import linregress
from itertools import repeat
import matplotlib.patches as mpatches

#%%
def data_grab(breakthrough: str) -> dict:
    """This function collects the data from a folder and makes it usable by the rest of the program

    Args:
        breakthrough (string): folder name

    Returns:
        dictionary: all data contained in folder sorted by source
    """
    datalist = glob.glob('%s/*' %breakthrough)
    datadict = {'wos': [], 
                'altmetric' : []}
    for file in datalist:
        print(file)
        if '.csv' in file:
            altmetric = pd.read_csv(file)
            altmetric['Date'] = pd.to_datetime(altmetric['Date'])
            altmetric['datedelta'] =  (altmetric['Date'] - altmetric['Date'].min())  / np.timedelta64(1,'D')
            altmetric['Year'] = altmetric['Date'].dt.strftime('%Y')
            datadict['altmetric'].append(altmetric)
        elif '.txt' in file:
            wos = pd.read_csv(file, delimiter = '\t')
            datadict['wos'].append(wos)
        else:
            pass
    return datadict

def scoring(combidata: dict, finance: float, employees: float, benefit: float, weightings: dict) -> pd.DataFrame:
    """Creates a weighted score for the data and scores inputted

    Args:
        combidata (dict): data from the web of science and altmetrics
        finance (float): inputted value for finance
        employees (float): inputted value for employees
        benefit (float): inputted value for benefits
        weightings (dict): score weightings for each section

    Returns:
        pd.DataFrame: dataframe ready for plotting
    """
    wos_data = combidata['wos'][0]
    wos_slope = linregress(wos_data['Publication Years'],wos_data['Record Count']).slope
    wos_score = (np.arctan(wos_slope)/(np.pi/2)) * weightings['wos']
    temp = combidata['altmetric'][0]
    if len(combidata['altmetric']) > 1:
        for num in range(1,len(combidata['altmetric'],1)):
            temp = temp + combidata['altmetric'][num+1]
    else:
        pass
    temp['news'] = list(repeat(0,len(temp)))
    temp['social'] = list(repeat(0,len(temp)))
    for col in temp.columns:
        if col == 'Twitter mentions' or col == 'Weibo mentions' or col == 'Facebook mentions' or col == 'Google+ mentions' or col == 'LinkedIn mentions' or col == 'Reddit mentions' or col == 'Pinterest mentions' or col == 'Video mentions':
            temp['social'] = temp['social'] + temp[col]
        elif col == 'News mentions' or col == 'Blog mentions':
            temp['news'] = temp['news'] + temp[col]
    
    temp1 = temp[['news','social','Year']]
    temp1 = temp1.groupby(by = ['Year']).sum()
    print(temp1)
    
    altnews_slope = linregress(range(int(temp1.index.min()),int(temp1.index.max()) ,1),temp1['news']).slope # change date range to correct units
    altnews_score = (np.arctan(altnews_slope)/(np.pi/2)) * weightings['altmetrics_news'] 
    altsocial_slope = linregress(range(int(temp1.index.min()),int(temp1.index.max()),1), temp1['social']).slope 
    altsocial_score = (np.arctan(altsocial_slope)/(np.pi/2)) * weightings['altmetrics_social']
    weighted_finance = finance * weightings['finance']/100
    weighted_employees = employees * weightings['employees']/100
    weighted_benefit = benefit * weightings['benefits']/100
    total = wos_score + altnews_score + altsocial_score + weighted_finance + weighted_employees + weighted_benefit   
    print(wos_slope)

    sections = ['wos','Altmetrics News','Altmetrics Social','Finance','Employees','Benefits','Total']
    scores = [wos_score,altnews_score,altsocial_score,weighted_finance,weighted_employees,weighted_benefit,total]
    scored = pd.DataFrame({'Section':sections,'Weighted Scores': scores})
    return scored

def graphing(data: pd.DataFrame,name: str):
    """Creates the plot for the scores to shows where the score comes from

    Args:
        data (pd.DataFrame): The adjusted and scored data
        name (str): folder name, this will be used to label the graph
    """
    theta = np.linspace(0.0, 2 * np.pi, 6, endpoint=False)
    radii = list(data['Weighted Scores'])[0:6]
    width = list(repeat((2*np.pi)/6,6))
    colors = plt.cm.viridis(np.linspace(0,1,6))
    mult = np.pi/180
    ax = plt.subplot(projection='polar')
    ax.bar(theta, radii, width=width, bottom=0.0, color=colors, alpha=0.5)
    ax.set_title('%s' %name)
    wos = mpatches.Patch(color=colors[0],alpha = 0.5, label='Web of Science')
    news = mpatches.Patch(color=colors[1],alpha = 0.5, label='News')
    social = mpatches.Patch(color=colors[2],alpha = 0.5, label='Social')
    finance = mpatches.Patch(color=colors[3],alpha = 0.5, label='Finance')
    employees = mpatches.Patch(color=colors[4],alpha = 0.5, label='Employees')
    benefits = mpatches.Patch(color=colors[5],alpha = 0.5, label='Benefits')
    #ax.legend(loc='upper left', handles=[wos,news,social,finance,employees,benefits])
    ax.set_xticks([0,60*mult,120*mult,180*mult,240*mult,300*mult],["               Paper Count","          News Mentions","Social Mentions           ","Finance    ","Employees","Benefits"])
    plt.show()


############################ USER INPUT SECTION##################################
folder = 'FLASH Radiotherapy'       #Put in name of folder                         #
                                                                                #
finance =43.8   #enter finance score as float                                  #
employees = 28.8  #enter employees score as float                               #
benefits = 90   #enter benefits score as float                                #
                                                                                #
weightings = {'wos' : 30,                                                       #
              'altmetrics_news': 25,                                            #
              'altmetrics_social':5,                                            #
              'finance':15,                                                     #
              'employees':15,                                                   #
              'benefits':10}                                                    #
                                                                                #
#################################################################################

combidata = data_grab(folder)

scores = scoring(combidata, finance, employees, benefits, weightings)
print(scores)
score = []
sections = ['wos','Altmetrics News','Altmetrics Social','Finance','Employees','Benefits','Total']
scores = pd.DataFrame({'Section':sections,'Weighted Scores':score})
graphing(scores,folder)





    





# %%
