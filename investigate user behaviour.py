#!/usr/bin/env python
# coding: utf-8

# ---

# ***Project Description***
# 
# To investigate user behavior for the startup  company's app that sells food products. 
# 
# First study the sales funnel. Find out how users reach the purchase stage. How many users actually make it to this stage? How many get stuck at previous stages? Which stages in particular?
# Then look at the results of an A/A/B test. (Read on for more information about A/A/B testing.) The designers would like to change the fonts for the entire app, but the managers are afraid the users might find the new design intimidating. They decide to make a decision based on the results of an A/A/B test.
# The users are split into three groups: two control groups get the old fonts and one test group gets the new ones. Find out which set of fonts produces better results.
# 
# 

# In[1]:


get_ipython().system('pip install plotly -U')


# ## Step 1. Open the data file and read the general information

# In[2]:


import math
from scipy import stats
import pandas as pd
import datetime
from datetime import datetime
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import plotly.express as px
from plotly import graph_objects as go
import seaborn as sns


# In[3]:


df = pd.read_csv('/datasets/logs_exp_us.csv',sep='\t')


# In[4]:


df.head(10)


# ## Step 2. Prepare the data for analysis

# •	Rename the columns in a way that's convenient for you
# 
# •	Check for missing values and data types. Correct the data if needed
# 
# •	Add a date and time column and a separate column for dates
# 

# In[5]:


df.columns =['event_name','user_id','timestamp','experiment_id']
df['timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
#Return the local date corresponding to the POSIX timestamp
 
df.head()


# In[6]:


df.isnull().sum()


# In[7]:


df.info()


# In[8]:


df[df.duplicated()].count()


# In[9]:


for i in df[df.duplicated()].columns :
    print(i, ':', df[df.duplicated()][i].nunique())


# > Duplicated data are distributed in all events and experiment_id, and different time

# In[10]:


df[df.duplicated()]['experiment_id'].unique()


# In[11]:


print(df[df.duplicated()].groupby('experiment_id')['user_id'].value_counts())


# In[12]:


df[df.duplicated()]['timestamp'].dt.date.unique()


# In[13]:


df[df.duplicated()]['event_name'].unique()


# In[14]:


df= df.drop_duplicates()


# > Duplicated data are droped. These data do not show concentration on any attributes in the dataframe.

# In[15]:


df.event_name.unique()


# In[16]:


df.describe(include= 'all')


# In[17]:


df['time'] = pd.to_datetime(df['timestamp']) 
df['date'] = df['time'].dt.date
df['time'] = df['time'].dt.time


# In[18]:


df.head()


# ## Step 3. Study and check the data

# •	**How many events are in the logs?**
# 
# •	**How many users are in the logs?**
# 

# In[19]:


df['event_name'].nunique()


# >  5 different events

# In[20]:


df['user_id'].nunique()


# > There are 7551 different users in log

# **•	What's the average number of events per user?**

# In[21]:


print(df.groupby(['user_id'])['event_name'].count().mean().round(2))


# In[22]:


print(df.groupby(['user_id'])['event_name'].count().median().round(2))


# > Average number of events per users are about 32. But this will not represent avereage number of events as some users have 
# upto 2307 events as obtained below in events.describe method.
# > **20 events per user lies in the middle of per user events ranking.**

# In[23]:


events= df.groupby(['user_id'])['event_name'].count()


# In[24]:


events.head(4)


# In[25]:


events.describe()


# In[26]:


plt.figsize=( 18,8)
plt.subplot(1, 2, 1)
sns.distplot(events[events> 200], bins= 20)


plt.title('distribution of events per user');
plt.ylabel('proportion');

plt.grid()


plt.subplot(1, 2, 2)

#sns.distplot(events[events> 200], bins= 20)
plt.hist(events[events> 200], bins= 20)

plt.title('number of events per user');
plt.ylabel('number of users');
plt.xlabel('number of events (larger than 200 only)');
plt.grid()

plt.show()


# > Number of users who had number of events more than 200 are in small proportion.

# In[27]:


plt.figsize=( 18,8)
plt.subplot(1, 2, 1)
sns.distplot(events[events< 200], bins= 16)
plt.title('distribution of events per user');
plt.ylabel('proportion');

plt.grid()


plt.subplot(1, 2, 2)

#sns.distplot(events[events> 200], bins= 20)
plt.hist(events[events < 200], bins= 20)

plt.title('number of events per user');
plt.ylabel('number of users');
plt.xlabel('number of events (smaller than 200 only)');
plt.grid()

plt.show()


# > Number of users decrease geometrically as number of events per users increases. More than 2500 users have less than 13 events. The number of 
# events per user have geometric distribution ( half normal).

# In[28]:


df.groupby(['user_id'])['event_name'].nunique().reset_index().groupby(['event_name'])['user_id'].nunique()


# > 471 users go through all processes.

# **•	What period of time does the data cover? Find the maximum and the minimum date. Plot a histogram by date and time. Can you be sure that you have equally complete data for the entire period? Older events could end up in some users' logs for technical reasons, and this could skew the overall picture. Find the moment at which the data starts to be complete and ignore the earlier section. What period does the data actually represent?**

# **•	Did you lose many events and users when excluding the older data?**

# In[29]:


print(df['date'].min())
print(df['date'].max())


# > Data cover from 2019-07-25 to 2019-08-07

# In[30]:


plt.hist(df['date'], bins=25);
plt.title('number of events based on date');
plt.xlabel('date');
plt.ylabel('number of events');
plt.xticks(rotation= 90);

plt.grid()

plt.show()


# > Actually from 2019-08-01 to 2019-08-07 represent the data. So, excluding 2019-08-01 does not make significant loss of events and users

# 
# <div class="alert alert-success">
# <b>Reviewer's comment:</b> Yes, you are right.
# </div>

# ---

# In[31]:


df[df['date']< pd.to_datetime('2019, 8, 1')].shape


# In[32]:


df.shape


# > Older data can be removed as they made up only 1.16 % of whole data

# In[33]:


df[df['date']< pd.to_datetime('2019, 8, 1')].groupby('experiment_id')['user_id'].count()


# > Older data are distributed in all groups

# In[34]:


print('Unique users before 2019-08-01: {}'.format(df[df['date']< pd.to_datetime('2019, 8, 1')]['user_id'].nunique()))


# In[35]:


print('Unique users after 2019-08-01: {}'.format(df[df['date']>= pd.to_datetime('2019, 8, 1')]['user_id'].nunique()))


# In[36]:


print('Unique users in whole data {}'.format(df['user_id'].nunique()))


# In[37]:


print('Unique user lost on excluding data before 2019-08-01: {}'.format((df['user_id'].nunique()) - (df[df['date']>= pd.to_datetime('2019, 8, 1')]['user_id'].nunique())))


# The no. of unique users that will be lost on excluding data make only 0.22 % of all unique users.

# In[38]:


df= df[df['date']>= pd.to_datetime('2019, 8, 1')]


# In[39]:


plt.hist(df['date'], bins=25);
plt.title('number of events based on date');
plt.xlabel('date');
plt.ylabel('number of events');
plt.xticks(rotation= 90);

plt.grid()

plt.show()


# > After excluding older data,  significant number of activities can be seen for every day's bar.

# In[40]:


plt.hist(df['time'], bins=100);
plt.title('number of events based on time');
plt.xlabel('time');
plt.ylabel('number of events');
plt.xticks(rotation= 90);

plt.grid()

plt.show()


# Users activity gradually increase from midnight to  about four o'clock then it decreases gradually. The distribution of user activity
# seems to to be have normal distribution

# **•	Make sure you have users from all three experimental groups**

# In[41]:


test_1=df[df.experiment_id==246]['user_id'].unique()


# In[42]:


test_2=df[df.experiment_id==247]['user_id'].unique()


# In[43]:


test_3=df[df.experiment_id==248]['user_id'].unique()


# In[44]:


print(len(test_1), len(test_2), len(test_3))


# **Conclusion**
# > The log have 5 different events and each users have about 20 events in average ( median). Among 7534 unique users more than 2500 
# users have less than 13 events. Likewise the data older than '2019-08-01' make very small porportion (1.16 % ) of total data so they can be
# dropped.

# ## Step 4. Study the event funnel

# **•	See what events are in the logs and their frequency of occurrence. Sort them by frequency.**

# In[45]:


print(df.groupby('event_name')['user_id'].count().sort_values(ascending= False))


# Its obvious main screen has by far the greatest propertion of events.

# **•	Find the number of users who performed each of these actions. Sort the events by the number of users. Calculate the proportion of users who performed the action at least once.**

# In[46]:


print(df.groupby('event_name')['user_id'].nunique().sort_values(ascending= False))


# In[47]:


print(df.groupby('event_name')['user_id'].nunique().sort_values(ascending= False)/df.user_id.nunique())


# about 1.5 % of users do not appear in main screen . should have some technical problem. About 47 % users make payment which is very high conversion rate.

# **•	In what order do you think the actions took place. Are all of them part of a single sequence? You don't need to take them into account when calculating the funnel.**

# In[48]:


print(df.groupby([ 'user_id', 'event_name'])[ 'user_id', 'event_name', 'timestamp'].head(20))


# In[49]:


print(df[df['user_id']== 3518123091307005509][['event_name','timestamp']].head(20))


# The user has visited main screen first then cart screen followed by payment screen for the first visit on 2019-08-01. But on second visit 
# on the same day offer screen after main screen. For top 20 logs the user has not gone through 'tutorial'. 

# In[50]:


action_time=df.sort_values(by=['timestamp'])
action_time.head()


# In[51]:


actions_time=action_time.groupby([ 'user_id', 'event_name'])['timestamp'].count()
actions_time.head(25)


# > The user '7702139951469979' has more than double logs  in offer screen than main screen suggests that user has checked many offers.

# >The result of users propertion in different stage:
#     
# MainScreenAppear                0.985168
#     
# OffersScreenAppear              0.610912
# 
# CartScreenAppear                0.496491
# 
# PaymentScreenSuccessful         0.469739
# 
# Tutorial                        0.112171 **
# 
# 
# >suggest the sequence of events in general. But the evidence of cart screen visit without offer screen  visit are also seen.

# > In general sequence of order follow **MainScreenAppear, OffersScreenAppear, CartScreenAppear, PaymentScreenSuccessful** , 
# 
# but there are 
# exception where users skip **Offer Screen** at first and they check offer multiple time later.

# **•	Use the event funnel to find the share of users that proceed from each stage to the next. 
# (For instance, for the sequence of events A → B → C, calculate the ratio of users at stage B to the number of users at stage A
#  and the ratio of users at stage C to the number at stage B.)**
# 
# **•	At what stage do you lose the most users?**
# 
# **•	What share of users make the entire journey from their first event to payment?**
# 

# In[ ]:





# In[52]:


funnel_shift= df.groupby('event_name')['user_id'].nunique().sort_values(ascending= False).reset_index()
funnel_shift=funnel_shift[0:4]
funnel_shift


# In[53]:


funnel_shift['change%']= funnel_shift['user_id'].pct_change()


# In[54]:


funnel_shift


# > Most of users are lost in Main screen. the conversion rate from main screen to offer screen is by far the lowest. ( Users who went to Tutorial page is not considred)

# In[55]:


#conversion=funnel_shift.sort_values(by= 'user_id', ascending= False).reset_index()
#conversion['change%']= 0
#conversion['change%']= conversion['user_id'].pct_change()
#conversion


# >5% of users who added order to cart screen dropped in payment screen. This seems low but it is very crucial as user who already add
#  order could not pay for order may be due to technical issues (for example payment method)

# In[56]:


funnel_by_groups= []
for i in df.experiment_id.unique():
    experiment_id= df[df.experiment_id== i ].groupby(['event_name', 'experiment_id'])['user_id'].nunique().sort_values(ascending= False)[0:4].reset_index()
    print(experiment_id)
    print('\n')
    funnel_by_groups.append(experiment_id)
    


# In[57]:


funnel_by_groups= pd.concat(funnel_by_groups)
funnel_by_groups.head(7)


# In[58]:


#conda install -c plotly plotly=4.14.3


# In[ ]:





# In[59]:



fig = px.funnel(funnel_by_groups,  x='user_id',  y='event_name', color='experiment_id', title='event funnel');
fig.show()


# > The groups seems to be homogeneously divided as the conversion rate on each step looks similar for all groups. The conversion 
# is lowest in first stage as already mention in earlier step.

# In[60]:



print(
    'share of users make the entire journey from their first event to payment  {:.2f}'\
    .format(funnel_shift.iloc[3, 1 ]/funnel_shift.iloc[0, 1])
)


# **Conclusion**

# *By far the greatest propertion of users in different events is in the following order:
# MainScreenAppear (0.98), OffersScreenAppear (0.61), CartScreenAppear (0.49) and PaymentScreenSuccessful (0.46)

# Most of users are lost in Main screen. the conversion rate from main screen to offer screen is by far the lowest. 

# 48% of users make entire journey from main screen appear to payment

# ## Step 5. Study the results of the experiment
# 
# **•	How many users are there in each group?**
# 

# In[61]:


df.groupby(['experiment_id'])['user_id'].nunique()


# In[62]:


print('Number of users from  group  246, 247 and 248 are {}, {} and {} respectively.'      .format(len(test_1), len(test_2), len(test_3)))


# In[63]:


df.groupby('user_id')['experiment_id'].nunique().reset_index().query('experiment_id > 1').count()


# > None of the users are in more than one group.

# **•	We have two control groups in the A/A test, where we check our mechanisms and calculations. See if there is a 
# statistically significant difference between samples 246 and 247**.

# **•	Select the most popular event. In each of the control groups, find the number of users who performed this action. Find their share. Check whether the difference between the groups is statistically significant. Repeat the procedure for all other events (it will save time if you create a special function for this test). Can you confirm that the groups were split properly?**

# In[64]:


pivot = df.pivot_table(index='event_name', values='user_id', columns='experiment_id', aggfunc=lambda x: x.nunique()).reset_index()
pivot


# In[65]:


print('Null Hpothesises:')
for i in df.experiment_id.unique():
    if i<248:
            x= i+1
    else:
            x= i-2
    for k in pivot.event_name.unique():
        print("There is no significant difference for",k, 'in groups',i, 'and', x)
        
print('\n\n')
        
print('Alternative Hpothesises:')
for i in df.experiment_id.unique():
    if i<248:
            x= i+1
    else:
            x= i-2
    for k in pivot.event_name.unique():
        print("There is no significant difference for",k, 'in groups',i, 'and', x)
        


# >**Null and alternative hypotheses are formulated to check each wheather event's occurence are siginificantly different or not among 
# given groups**
# 
# > The test will be performed within four steps from here:

# In[66]:


def check_hypothesis(group1, group2, success1,successes2, trials1, trials2, event,  alpha):
    #let's start with successes, using 
    #successes1=pivot[pivot.event_name==event][group1].iloc[0]
    #successes2=pivot[pivot.event_name==event][group2].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    #trials1=df[df.experiment_id==group1]['user_id'].nunique()
    #trials2=df[df.experiment_id==group2]['user_id'].nunique()
    
    #proportion for success in the first group
    p1 = successes1/trials1

   #proportion for success in the second group
    p2 = successes2/trials2

    # proportion in a combined dataset
    p_combined = (successes1 + successes2) / (trials1 + trials2)

  
    difference = p1 - p2
    
    
    z_value = difference / math.sqrt(p_combined * (1 - p_combined) * (1/trials1 + 1/trials2))

  
    distr = stats.norm(0, 1) 


    p_value = (1 - distr.cdf(abs(z_value))) * 2

    print('p-value: ', p_value)

    if (p_value < alpha):
        print("Reject H0 for",event, 'in groups',group1, 'and',group2)
    else:
        print("Fail to Reject H0 for", event,'in groups',group1, 'and',group2) 


# ---

# In[67]:



for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(246, 247, successes1,successes2, trials1, trials2, i, alpha=0.05)


# In[68]:


for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(246, 248, successes1,successes2, trials1, trials2, i, alpha=0.05)


# In[69]:


for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(247, 248, successes1,successes2, trials1, trials2, i, alpha=0.05)


# > **As all of the hypotheses are failed to rejected, group split could be considered properly splited.**

# **•	Do the same thing for the group with altered fonts. Compare the results with those of each of the control groups for each event in isolation. Compare the results with the combined results for the control groups. What conclusions can you draw from the experiment?**

# In[70]:


pivot1= pivot.copy(deep=True)
pivot1.columns= ['event_name', 'control1', 'control2', 'test']
pivot1['control']= pivot1['control1']+pivot1['control2']
pivot1


# In[71]:


df1= df.copy(deep=True)


# In[72]:


df1.loc[df1.experiment_id == 246, "experiment_id"] = "control"
df1.loc[df1.experiment_id == 247, "experiment_id"] = "control"
df1.loc[df1.experiment_id == 248, "experiment_id"] = "test"


# In[73]:


df1.head()


# In[74]:


print('Null Hpothesises:')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control and test group')
print('\n\n')

print('alternative Hpothesises:')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control and test group')

        


# In[75]:


trials1=df[df.experiment_id=='control']['user_id'].nunique()


# In[76]:



    
for i in pivot1.event_name.unique():
    #let's start with successes, using 
    successes1=pivot1[pivot1.event_name==i]['control'].iloc[0]
    successes2=pivot1[pivot1.event_name==i]['test'].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df1[df1.experiment_id=='control']['user_id'].nunique()
    trials2=df1[df1.experiment_id=='test']['user_id'].nunique()
    check_hypothesis('control', 'test', successes1,successes2, trials1, trials2, i, alpha=0.05)


# >**No significant difference between control and test group as non of the event's hypothesis is rejected**

# **•	What significance level have you set to test the statistical hypotheses mentioned above? Calculate how many statistical hypothesis tests you carried out. With a statistical significance level of 0.1, one in 10 results could be false. What should the significance level be? If you want to change it, run through the previous steps again and check your conclusions.**

# In[77]:


pivot.head()


# In[78]:


print('Null Hpothesises: (alpha= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in 246 and 248 group')
print('\n\n')
    
print('Alternative Hpothesises: (alpha= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is  significant difference for",k, 'in 246 and 248 group')
        


# In[79]:


for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(246, 247, successes1,successes2, trials1, trials2, i, alpha=0.1)


# In[80]:


print('Null Hpothesises: (alpha= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in 247 and 248 group')
print('\n\n')
    
print('Alternative Hpothesises: (alpha= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is  significant difference for",k, 'in 247 and 248 group')
        


# In[81]:


for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(247, 248, successes1,successes2, trials1, trials2, i, alpha=0.05)


# > There is no significant statistical difference between  group '247' and '248'

# In[82]:


print('Null Hpothesises: alpha(0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control  and test group')

print('\n\n')
    
print('Alternative Hpothesises: (alpha= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control  and test group')
        


# In[83]:


for i in pivot.event_name.unique():
    #let's start with successes, using 
    successes1=pivot[pivot.event_name==i][246].iloc[0]
    successes2=pivot[pivot.event_name==i][247].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df[df.experiment_id==246]['user_id'].nunique()
    trials2=df[df.experiment_id==247]['user_id'].nunique()
    check_hypothesis(246, 247, successes1,successes2, trials1, trials2, i, alpha=0.05)


# In[84]:


print('Null Hpothesises: ( Bonferroni correction , alphaa= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control  and test group')

print('\n\n')
    
print('Alternative Hpothesises: ( Bonferroni correction , alphaa= 0.1)')
  
for k in pivot.event_name.unique():
    print("There is no significant difference for",k, 'in control  and test group')


# > **As 10 test are performed on the given dataframe, so the probability of error raised to 10 times of probability of error in each test.
# So, in order to overcome possible error alpha value should be divided by 10**

# In[85]:


for i in pivot1.event_name.unique():
    #let's start with successes, using 
    successes1=pivot1[pivot1.event_name==i]['control'].iloc[0]
    successes2=pivot1[pivot1.event_name==i]['test'].iloc[0]
    
    #for trials we can go back to original df or used a pre-aggregated data
    trials1=df1[df1.experiment_id=='control']['user_id'].nunique()
    trials2=df1[df1.experiment_id=='test']['user_id'].nunique()
    check_hypothesis('control', 'test', successes1,successes2, trials1, trials2, i, alpha=0.01)


# **Even after bonferroni correction, none of the hypothesis is rejected. so it can be concluded that changing the font do not make significant 
# difference in any event by users.**

# **Conclusion**
# 
# Each group have about 2500 users
# 
# Neither control groups are significantly different nor they are different from test group (both individually and together)
# 
# As  10 test are performed in dataframe, for bonferroni correction alpha should be divided by 10. So for test performed at alpha = 0.1, after correction alpha should be 0.01

# **Overall Conclusion**
# 

# >All null hypothesis are failed to reject. This mean on A/A test and and A/B test failed to reject any hypothesis. 
# That indicate no significant difference in any event between combined control and test group also control group 1 (experiment id = 246) and 
# control group 2 (experiment id= 247).
# 
# > so, it can be concluded that changing font do not make significant difference in any events.

# 
