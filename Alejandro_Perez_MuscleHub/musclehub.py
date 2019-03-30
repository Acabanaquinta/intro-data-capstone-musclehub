#!/usr/bin/env python
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# In[60]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[61]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[62]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[63]:


df_visits = sql_query('''
SELECT *
FROM visits
''')
# df_visits.head()


# In[64]:


df_tests = sql_query('''
SELECT *
FROM fitness_tests
''')
# df_tests.head()


# In[65]:


df_appli = sql_query('''
SELECT *
FROM applications
''')
# df_appli.head()


# In[66]:


df_purchases = sql_query('''
SELECT *
FROM purchases
''')
# df_purchases.head()


# ---

# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[67]:


df_visits = df_visits.loc[df_visits.visit_date >= '7-1-17', :]
all_data = df_visits           .merge(df_tests, on=['first_name', 'last_name', 'email', 'gender'], how="left")           .merge(df_appli, on=['first_name', 'last_name', 'email', 'gender'], how="left")           .merge(df_purchases, on=['first_name', 'last_name', 'email', 'gender'], how="left")

all_data = all_data[['first_name', 'last_name', 'gender', 'email',                     'visit_date', 'fitness_test_date',                     'application_date', 'purchase_date']]
all_data.head()


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[68]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[69]:


all_data['ab_test_group'] = all_data.fitness_test_date.apply(lambda x:
                                                             'B' if pd.isnull(x) else 'A')
all_data.head()


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[70]:


ab_counts = all_data.groupby('ab_test_group').email.count().reset_index()
ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[71]:


plt.style.use('ggplot')
fig1, ax1 = plt.subplots(figsize= (8, 8))
labels_pie = ['A', 'B']
plt.pie(ab_counts['email'], autopct='%0.2f%%')
ax1.legend(labels_pie, loc=4)
ax1.set_title('Group A vs Group B in %')
plt.savefig('ab_test_pie_chart.png', bbox_inches='tight')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[72]:


all_data['is_application'] = all_data.application_date.apply(lambda x:
                                                             'Application' if pd.notnull(x)
                                                             else 'No Application')
all_data.head()


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[73]:


app_counts = all_data.groupby(['is_application', 'ab_test_group']).email.count().reset_index()
app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[74]:


app_pivot = all_data.groupby(['is_application', 'ab_test_group']).email.count().unstack('is_application')
app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[75]:


app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[76]:


app_pivot['Percent with Application'] = (app_pivot['Application'] / app_pivot['Total']) * 100.
app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[77]:


from scipy.stats import chi2_contingency

contingency = [[250, 2254],
               [325, 2175]]
          

chi2_stat, pvalue, dof, t = chi2_contingency(contingency)
print('There is a significant difference as the pvalue is < 0.05: {:.5f}'.format(pvalue))


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[78]:


all_data['is_member'] = all_data.purchase_date.apply(lambda x:
                                                     'Member' if pd.notnull(x)
                                                      else 'Not Member')
all_data.head()


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[79]:


just_apps = all_data.loc[pd.notnull(all_data.application_date), :]
just_apps = just_apps.reset_index(drop=True)


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[80]:


member_pivot = just_apps.groupby(['ab_test_group', 'is_member']).email.count().unstack('is_member')
member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = (member_pivot['Member'] / member_pivot['Total']) * 100.

member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[81]:


contingency = [[200, 50],
               [250, 75]]
          

chi2_stat, pvalue, dof, t = chi2_contingency(contingency)
print('There is no significant difference as the pvalue is > 0.05: {:.5f}'.format(pvalue))


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[82]:


final_member_pivot = all_data.groupby(['ab_test_group', 'is_member']).email.count().unstack('is_member')
final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = (final_member_pivot['Member'] / final_member_pivot['Total']) * 100.

final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[83]:


contingency = [[200, 2304],
               [250, 2250]]
          

chi2_stat, pvalue, dof, t = chi2_contingency(contingency)
print('There is significant difference as the pvalue is < 0.05: {:.5f}'.format(pvalue))


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[89]:


x1_values_side_by_side = [2.*x + 0.8*1 for x in range(0, 3)]
x2_values_side_by_side = [2.*x + 0.8*2 for x in range(0, 3)]
x_ticks = [(x + y) / 2 for x, y in zip(x1_values_side_by_side, x2_values_side_by_side)]

A = [app_pivot.iloc[0, 3],
     member_pivot.iloc[0, 3],
     final_member_pivot.iloc[0, 3]]
A = [x/100 for x in A]
B = [app_pivot.iloc[1, 3],
     member_pivot.iloc[1, 3],
     final_member_pivot.iloc[1, 3]]
B = [x/100 for x in B]

plt.style.use('ggplot')
fig2, ax2 = plt.subplots(figsize=(10, 8))
plt.bar(x1_values_side_by_side, A, label='Fitness Test')
plt.bar(x2_values_side_by_side, B, label='No Fitness Test')
plt.legend()
ax2.set_xticks(x_ticks)
ax2.set_xticklabels(['Complete Application', 'Member once Applied', 'Member once Visited'])
ax2.set_ylabel('Percentage')
ax2.set_title('Percentage of Membership During Each Funnel Stage')
y_ticks = ax2.get_yticks()
ax2.set_yticklabels(['{:.1%}'.format(x) for x in y_ticks])
plt.savefig('Percentage of Membership During Each Funnel Stage.png', bbox_inches='tight')
plt.show()


# In[85]:


app_pivot


# In[ ]:




