# -*- coding: utf-8 -*-
"""PRML_Minor_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lMaCLSo-pmVTd0En3ntpMg66LKquQzwL
"""



import pandas as pd
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import datetime

data_copy=pd.read_excel('Online_Retail.xlsx')
data=data_copy

# Remove null values
data = data.dropna()

#Removing Duplicates
data = data.drop_duplicates()


# Drop irrelevant columns
data = data.drop(['Description'], axis=1)

# Convert data types
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['CustomerID'] = data['CustomerID'].astype(int)

data

# Number of unique customers
num_customers = len(data['CustomerID'].unique())

# Number of unique transactions
num_transactions = len(data['InvoiceNo'].unique())

# Number of unique products
num_products = len(data['StockCode'].unique())

# Print the results
print('Number of unique customers:', num_customers)
print('Number of unique transactions:', num_transactions)
print('Number of unique products:', num_products)

import pandas as pd
import matplotlib.pyplot as plt


# Compute the percentage of orders from each country
country_counts = data['Country'].value_counts(normalize=True) * 100

# Create a bar plot of the results
fig, ax = plt.subplots(figsize=(10, 6))
country_counts.plot(kind='bar', ax=ax)
ax.set_xlabel('Country')
ax.set_ylabel('% of orders')
ax.set_title('% of orders by country')
plt.show()

"""# Case 1"""

data = data[data['Country'] == 'United Kingdom']
data = data.reset_index(drop=True)
data

count=0
for i in range(len(data["Quantity"])):
    if(data["Quantity"][i]<0):
        count+=1
print(f"The cancelled orders are {count} in number")

data=data[data["Quantity"]>0]
data = data.reset_index(drop=True)
data

# Number of unique customers
num_customers = len(data['CustomerID'].unique())

# Number of unique transactions
num_transactions = len(data['InvoiceNo'].unique())

# Number of unique products
num_products = len(data['StockCode'].unique())

# Print the results
print('Number of unique customers:', num_customers)
print('Number of unique transactions:', num_transactions)
print('Number of unique products:', num_products)

# Create a new column called 'InvoiceMonth'
data['InvoiceMonth'] = pd.to_datetime(data['InvoiceDate']).dt.to_period('M').dt.to_timestamp()

# Extract information about the first month of each transaction, grouped by CustomerID
first_month_data = data.groupby('CustomerID')['InvoiceMonth'].min().reset_index()
#First month to check how old the customer is based on the min value of the Invoice month
first_month_data

# Create a new column with the first date of the month
data['InvoiceMonth'] = pd.to_datetime(data['InvoiceDate']).dt.to_period('M').dt.to_timestamp()
data['CohortMonth'] = data.groupby('CustomerID')['InvoiceMonth'].transform('min')
data['CohortIndex'] = data['InvoiceMonth'].dt.month - data['CohortMonth'].dt.month + 1

# Calculate the difference in months between the InvoiceMonth and CohortMonth
def calculate_cohort_interval(df):
    df['CohortIndex'] = df['InvoiceMonth'].dt.to_period('M').astype(int) - df['CohortMonth'].dt.to_period('M').astype(int) + 1
    return df


data = data.groupby(['CohortMonth', 'CohortIndex']).apply(calculate_cohort_interval)

data["CohortIndex"].value_counts()

cohort_data = data.groupby(['CohortMonth', 'CohortIndex']).agg({'CustomerID': pd.Series.nunique}).reset_index()
cohort_matrix = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
print(cohort_matrix)
data[:]

# Step 3: Create cohort analysis matrix
cohort_counts = pd.pivot_table(data, index='CohortMonth', columns='CohortIndex', values='CustomerID', aggfunc=pd.Series.nunique)
cohort_sizes = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_sizes, axis=0)

# Step 5: Create heatmap
plt.figure(figsize=(10, 8))
plt.title('Retention Rates')
sns.heatmap(data=retention, annot=True, cmap='BuGn', fmt='.0%', vmin=0, vmax=0.5)
plt.show()

reference_date=data.InvoiceDate.max()
reference_date=reference_date+datetime.timedelta(days=1)#timedelta function returns to total number of seconds
print(data.InvoiceDate.max(),data.InvoiceDate.min())
reference_date

data['days_since_last_purchase']=reference_date-data.InvoiceDate
data['days_since_last_purchase_num']=data['days_since_last_purchase'].astype('timedelta64[D]')
data['days_since_last_purchase_num'].head()

customer_history_df=data.groupby('CustomerID').min().reset_index()[['CustomerID', 'days_since_last_purchase_num']]
customer_history_df.rename(columns={'days_since_last_purchase_num':'Recency'}, inplace=True)
print(customer_history_df.describe())
customer_history_df.head()

data.describe()

#Average quantity for each cohort
grouping = data.groupby(['CohortMonth', 'CohortIndex'])
cohort_data = grouping['Quantity'].mean()
cohort_data = cohort_data.reset_index()
average_quantity = cohort_data.pivot(index='CohortMonth',columns='CohortIndex',values='Quantity')
average_quantity.round(1)
average_quantity.index = average_quantity.index.date

#Build the heatmap
plt.figure(figsize=(15, 8))
plt.title('Average quantity for each cohort')
sns.heatmap(data=average_quantity,annot = True,vmin = 0.0,vmax =20,cmap="BuGn_r")
plt.show()

df=data
df

df['TotalSum'] = df['UnitPrice']* df['Quantity']

#Data preparation steps
print('Min Invoice Date:',df.InvoiceDate.dt.date.min(),'max Invoice Date:',
       df.InvoiceDate.dt.date.max())

df.head(3)

df['InvoiceDay'] = df['InvoiceDate'].apply(lambda x: datetime.datetime(x.year, x.month, x.day))

act_date = max(df['InvoiceDay'] + datetime.timedelta(1))
df['TotalSum'] = df['Quantity'] * df['UnitPrice']
df.drop(['CohortMonth', 'InvoiceMonth', 'CohortIndex'], axis=1, inplace=True)
df.head()

rfm = df.groupby('CustomerID').agg({
    'InvoiceDate' : lambda x: (act_date - x.max()).days,
    'InvoiceNo' : 'count',
    'TotalSum' : 'sum'
    
})


rfm.rename(columns = {'InvoiceDate' : 'Recency', 
                      'InvoiceNo' : 'Frequency', 
                      'TotalSum' : 'MonetaryValue'}, inplace = True)
CustomerID=[]
for i in rfm.index:
    CustomerID.append(i)
rfm["CustomerID"]=CustomerID

rfm.head()



#Building RFM segments
r_labels =range(4,0,-1)
f_labels=range(1,5)
m_labels=range(1,5)
r_quartiles = pd.qcut(rfm['Recency'], q=4, labels = r_labels)
f_quartiles = pd.qcut(rfm['Frequency'],q=4, labels = f_labels)
m_quartiles = pd.qcut(rfm['MonetaryValue'],q=4,labels = m_labels)
rfm = rfm.assign(R=r_quartiles,F=f_quartiles,M=m_quartiles)

# Build RFM Segment and RFM Score
def add_rfm(x) : return str(x['R']) + str(x['F']) + str(x['M'])
rfm['RFM_Segment'] = rfm.apply(add_rfm,axis=1 )
rfm['RFM_Score'] = rfm[['R','F','M']].sum(axis=1)

rfm_np=rfm.to_numpy()
rfm_np[:,0]

rfm_agg = rfm.groupby('RFM_Score').agg({
    'Recency' : 'mean',
    'Frequency' : 'mean',
    'MonetaryValue' : ['mean', 'count']
})

rfm_agg.rename(columns = {'mean' : 'Mean','count' : 'Count'},
               inplace = True)

rfm_agg.round(2).head()

rfm.groupby(['RFM_Segment']).size().sort_values(ascending=False)[:5]

rfm[rfm['RFM_Segment']=='211'].head()

rfm.groupby('RFM_Score').agg({'Recency': 'mean','Frequency': 'mean',
                             'MonetaryValue': ['mean', 'count'] }).round(1)

def segments(df):
    if df['RFM_Score'] > 9 :
        return 'Category1'
    elif (df['RFM_Score'] > 5) and (df['RFM_Score'] <= 9 ):
        return 'Category2'
    else:  
        return 'Category3'

rfm['General_Segment'] = rfm.apply(segments,axis=1)

rfm.groupby('General_Segment').agg({'Recency':'mean','Frequency':'mean',
                                    'MonetaryValue':['mean','count']}).round(1)

rfm_rfm = rfm[['Recency','Frequency','MonetaryValue']]
print(rfm_rfm.describe())

f,ax = plt.subplots(figsize=(10, 12))
plt.subplot(3, 1, 1); sns.distplot(rfm.Recency, label = 'Recency')
plt.subplot(3, 1, 2); sns.distplot(rfm.Frequency, label = 'Frequency')
plt.subplot(3, 1, 3); sns.distplot(rfm.MonetaryValue, label = 'Monetary Value')
plt.style.use('fivethirtyeight')
plt.tight_layout()
plt.show()

rfm['Recency'].replace(0, np.nan, inplace=True)
rfm['Frequency'].replace(0, np.nan, inplace=True)
rfm['MonetaryValue'].replace(0, np.nan, inplace=True)
rfm.dropna(inplace=True)
# rfm = rfm.rest_index(drop=True)
rfm

rfm_log = rfm[['Recency', 'Frequency', 'MonetaryValue']].apply(np.log, axis = 1)
rfm_log.dropna()
rfm = rfm.reset_index(drop=True)
rfm.describe()

rfm_log

rfm_log.replace([np.inf, -np.inf], np.nan, inplace=False)

scaler = StandardScaler()

scaler.fit(rfm_log)

rfm_normalized= scaler.transform(rfm_log)
rfm_normalized

rfm_normalized = pd.DataFrame(rfm_normalized,columns = ['Recency', 'Frequency', 'MonetaryValue'])
# rfm_normalized.replace([np.inf, -np.inf, 0], np.nan, inplace=True)
# rfm_normalized.dropna(inplace=True)
rfm_normalized

# plot the distribution of RFM values
f,ax = plt.subplots(figsize=(10, 12))
plt.subplot(3, 1, 1); sns.distplot(rfm_normalized.Recency, label = 'Recency')
plt.subplot(3, 1, 2); sns.distplot(rfm_normalized.Frequency, label = 'Frequency')
plt.subplot(3, 1, 3); sns.distplot(rfm_normalized.MonetaryValue, label = 'Monetary Value')
plt.style.use('fivethirtyeight')
plt.tight_layout()
plt.show

import numpy as np
import random

class KMeans:
    def __init__(self, n_clusters=8, max_iter=300, init='k-means++', random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.init = init
        self.random_state = random_state

    def fit(self, X):
        if self.init == 'k-means++':
            self.centroids = self.k_means_pp_init(X)
        else:
            self.centroids = self.random_init(X)

        for i in range(self.max_iter):
            old_centroids = np.copy(self.centroids)
            clusters = self.assign_clusters(X, self.centroids)
            self.centroids = self.update_centroids(X, clusters)

            if np.array_equal(old_centroids, self.centroids):
                break

        self.labels_ = self.predict(X)
        self.inertia_ = self.compute_inertia(X, clusters)

    def k_means_pp_init(self, X):
        n_samples, n_features = X.shape
        centroids = np.empty((self.n_clusters, n_features))

        # randomly select the first centroid
        random_idx = random.randint(0, n_samples - 1)
        centroids[0] = X[random_idx]

        # select remaining centroids using k-means++ algorithm
        for i in range(1, self.n_clusters):
            distances = np.empty((n_samples, i))
            for j in range(i):
                distances[:, j] = np.linalg.norm(X - centroids[j], axis=1)

            # choose next centroid using minimum distance squared
            prob = np.min(distances, axis=1) ** 2
            prob /= np.sum(prob)
            next_centroid_idx = np.random.choice(n_samples, p=prob)
            centroids[i] = X[next_centroid_idx]

        return centroids

    def random_init(self, X):
        n_samples, n_features = X.shape
        random_idx = np.random.choice(n_samples, size=self.n_clusters, replace=False)
        return X[random_idx]

    def assign_clusters(self, X, centroids):
        distances = np.empty((X.shape[0], self.n_clusters))
        for i in range(self.n_clusters):
            distances[:, i] = np.linalg.norm(X - centroids[i], axis=1)
        return np.argmin(distances, axis=1)

    def update_centroids(self, X, clusters):
        centroids = np.empty((self.n_clusters, X.shape[1]))
        for i in range(self.n_clusters):
            centroids[i] = np.mean(X[clusters == i], axis=0)
        return centroids

    def predict(self, X):
        distances = np.empty((X.shape[0], self.n_clusters))
        for i in range(self.n_clusters):
            distances[:, i] = np.linalg.norm(X - self.centroids[i], axis=1)
        return np.argmin(distances, axis=1)

    def compute_inertia(self, X, clusters):
        inertia = 0
        for i in range(self.n_clusters):
            inertia += np.sum((X[clusters == i] - self.centroids[i]) ** 2)
        return inertia

ks = range(1,8)
inertias=[]
for k in ks :
    # Create a KMeans clusters
    kc = KMeans(n_clusters=k)
    kc.fit(rfm_normalized.to_numpy())
    inertias.append(kc.inertia_)

# Plot ks vs inertias
f, ax = plt.subplots(figsize=(15, 8))
plt.plot(ks, inertias, '-o')
plt.xlabel('Number of clusters, k')
plt.ylabel('Inertia')
plt.xticks(ks)
plt.style.use('ggplot')
plt.title('What is the Best Number for KMeans ?')
plt.show()

#From the above implementation of elbow method we can see that the optimaal value for the k means is 3
kc = KMeans(n_clusters=3)
rfm_norm_np=rfm_normalized.to_numpy()
rfm_norm_np.shape
kc.fit(rfm_norm_np)
kc.labels_.shape
rfm['RFM Cluster'] = kc.labels_

rfm_s=rfm.groupby('RFM Cluster').agg({'Recency': 'mean','Frequency': 'mean',
                                         'MonetaryValue': ['mean', 'count']})


rfm_s.rename(columns = {'mean' : 'Mean','count' : 'Count'},
               inplace = True)



display(rfm_s.style.background_gradient(cmap='Pastel1'))

rfm['RFM Cluster']=rfm['RFM Cluster'].map({0: 'K_C1', 1: 'K_C2',2:'K_C3'})
rfm.sample(40)

rfm

rfm_normalized = pd.DataFrame(rfm_normalized,index=rfm.index,columns=rfm_rfm.columns)

rfm_normalized['K_Cluster'] = kc.labels_
rfm_normalized['General_Segment'] = rfm['General_Segment']
# rfm_normalized.shape
rfm_normalized['CustomerID'] = rfm['CustomerID']
rfm_normalized.reset_index(inplace = True)
rfm_normalized

#Melt the data into a long format so RFM values and metric names are stored in 1 column each
rfm_melt = pd.melt(rfm_normalized,id_vars=['CustomerID','General_Segment','K_Cluster'],value_vars=['Recency', 'Frequency', 'MonetaryValue'],
var_name='Metric',value_name='Value')
rfm_melt.head()

# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 8))

# create a line plot of 'Value' vs 'Metric', colored by 'General_Segment'
sns.lineplot(x='Metric', y='Value', hue='General_Segment', data=rfm_melt, ax=ax1)

# create a line plot of 'Value' vs 'Metric', colored by 'K_Cluster'
sns.lineplot(x='Metric', y='Value', hue='K_Cluster', data=rfm_melt, ax=ax2)

# add a title to the figure
fig.suptitle("Snake Plot of RFM", fontsize=24)

# display the figure
plt.show()

total_avg = rfm.iloc[:, 0:3].mean()

cluster_avg = rfm.groupby('General_Segment').mean().iloc[:, 0:3]
prop_rfm = cluster_avg/total_avg - 1

cluster_avg_K = rfm.groupby('RFM Cluster').mean().iloc[:, 0:3]
prop_rfm_K = cluster_avg_K/total_avg - 1

fig, ax = plt.subplots(ncols=2, figsize=(12,8))
sns.heatmap(prop_rfm, cmap= 'summer_r', fmt= '.2f', annot = True, ax=ax[0])
sns.heatmap(prop_rfm_K, cmap= 'summer_r', fmt= '.2f', annot = True, ax=ax[1])

ax[0].set_title('Heatmap of General RFM Level', size=15)
ax[1].set_title('Heatmap of RFM Cluster', size=15)

plt.show()

"""# Visualization

# #Unscaled-General_Segmentation
"""

sns.scatterplot(data=rfm,x="MonetaryValue",y="Frequency",hue="General_Segment")

sns.scatterplot(data=rfm,x="Recency",y="Frequency",hue="General_Segment")

sns.scatterplot(data=rfm,x="MonetaryValue",y="Recency",hue="General_Segment")

"""# #Scaled-General_Segmentation"""

sns.scatterplot(data=rfm_normalized,x="Recency",y="Frequency",hue="General_Segment")

sns.scatterplot(data=rfm_normalized,x="MonetaryValue",y="Frequency",hue="General_Segment")

sns.scatterplot(data=rfm_normalized,x="MonetaryValue",y="Recency",hue="General_Segment")

"""# #Unscaled-KMeans"""

sns.scatterplot(data=rfm,x="MonetaryValue",y="Frequency",hue="RFM Cluster")

sns.scatterplot(data=rfm,x="Recency",y="Frequency",hue="RFM Cluster")

sns.scatterplot(data=rfm,x="MonetaryValue",y="Recency",hue="RFM Cluster")



# import necessary libraries
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# load the online_retail dataset
df = pd.read_excel("Online_Retail.xlsx")

# preprocess the data by dropping rows with missing values and converting categorical variables to numerical values
df.dropna(inplace=True)
df["Country"] = df["Country"].astype("category")
df["Country_cat"] = df["Country"].cat.codes

# select the features to be used for PCA
features = ["Quantity", "UnitPrice", "CustomerID", "Country_cat"]

# standardize the features
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[features])

# perform PCA with 2 principal components
pca = PCA(n_components=2)
pca.fit(df_scaled)
pca_scores = pca.transform(df_scaled)

# add the PCA scores to the original dataframe
df["PC1"] = pca_scores[:, 0]
df["PC2"] = pca_scores[:, 1]

# visualize the results using a scatter plot
import matplotlib.pyplot as plt
plt.scatter(df["PC1"], df["PC2"])
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.show()



# import necessary libraries
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import LabelEncoder

# load the online_retail dataset
df = pd.read_excel("Online_Retail.xlsx")

# preprocess the data by dropping rows with missing values
df.dropna(inplace=True)

# encode the categorical variable "Country" to numerical values
le = LabelEncoder()
df["Country_cat"] = le.fit_transform(df["Country"])

# select the features and target variable for LDA
features = ["Quantity", "UnitPrice", "Country_cat"]
target = "InvoiceNo"

# convert the target variable to a one-dimensional array of labels
target_labels = df[target].astype("category").cat.codes.ravel()

# perform LDA with 1 component
lda = LinearDiscriminantAnalysis(n_components=1)
lda_scores = lda.fit_transform(df[features], target_labels)

# add the LDA scores to the original dataframe
df["LD1"] = lda_scores

# visualize the results using a scatter plot
import matplotlib.pyplot as plt
plt.scatter(df["LD1"], [0] * len(df))
plt.xlabel("LD1")
plt.ylim(-0.1, 0.1)
plt.show()
