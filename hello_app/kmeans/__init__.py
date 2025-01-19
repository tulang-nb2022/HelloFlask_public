

from sklearn.cluster import KMeans
import sklearn.preprocessing as preprocessing
import sklearn.metrics as metrics
import pandas as pd
import numpy as np
from scipy.spatial import distance
import os 

# Kmeans use cases:  customer segmentation, fraud detection, predicting account attrition, targeting client incentives, cybercrime identification, and delivery route optimization.
# Problem statement: implement a function cluster_customers() which will find best number of customers cluster based on historical balance account data. after this step, you compare results with old cluster assignment

def standardize(x,mean,sd):
    return np.round((x-mean)/sd,3)


def cluster_customers(data_path):
    # Access datasets by calling:
    data_train_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data_train.csv') # cluster col relates to cluster name from the old manually assigned cluster. 12 further cols describes customer account values in the last 12 mos
    data_test_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data_test.csv')
    data_train = pd.read_csv(data_train_file_path)
    data_test = pd.read_csv(data_test_file_path)
    
    # 1 Standardize all 12 variables 
    for col in ['account_1','account_2','account_3','account_4','account_5','account_6','account_7', 'account_8','account_9','account_10','account_11','account_12']:
        # Use statistics from data_train to standardize variables in both. 3 decimal places
        mean = data_train[col].mean() 
        sd = data_train[col].std()
        data_train[col+'_sd'] = data_train[col].apply(lambda x: standardize(x,mean,sd))
        data_test[col+'_sd'] = data_test[col].apply(lambda x: standardize(x,mean,sd))

    sd_train = data_train[[x for x in data_train.columns if '_sd' in x]]
    sd_test = data_test[[x for x in data_train.columns if '_sd' in x]]

    #2 Build k-means clustering
    wcss_list = []
    sd_train_np = sd_train.to_numpy()
    for i in range(2,10):
        kmeans = KMeans(init="k-means++",n_clusters=i,max_iter=50,n_init=10,random_state=0,tol=0.05)
        kmeans.fit(sd_train)
        centroids  = kmeans.cluster_centers_
        # Calculate Euclidean distance between centroids and each point
        distances = []
        for j in range(len(sd_train_np)):
            distances.append(distance.euclidean(sd_train_np[j],centroids[kmeans.labels_[j]]))
        wcss_list.append(sum([x**2 for x in distances]))

    # Smallest number where the diff between wcss for this number of clusters and for the next one is smaller than 20
    for d in range(0,len(wcss_list)-1):
        if abs(wcss_list[d]-wcss_list[d+1])<20:
            opt_cluster = d 

    # kmeans_opt
    kmeans_opt = KMeans(init="k-means++",n_clusters=opt_cluster,max_iter=50,n_init=10,random_state=0,tol=0.05)
    kmeans_opt.fit(sd_test)
    # kmeans_4
    kmeans_4 = KMeans(init="k-means++",n_clusters=4,max_iter=50,n_init=10,random_state=0,tol=0.05)
    kmeans_4.fit(sd_test)

    # Silhouette score calc; measures the similarity of a data point within its cluster (cohesion) compared to other clusters (separation) - based off of kmeans_opt and sd_train
    kmeans_opt_train = KMeans(init="k-means++",n_clusters=opt_cluster,max_iter=50,n_init=10,random_state=0,tol=0.05)
    kmeans_opt_train.fit(sd_train)
    cluster_labels = kmeans_opt_train.fit_predict(sd_train)
    silhouette_avg = metrics.silhouette_score(sd_train, cluster_labels)

    # Completeness score on kmeans_4/sd_train, sd_test; measures the extent to which all data points of a particular class are assigned to the same cluster.
    # Use like: sklearn.metrics.completeness_score(labels_true, labels_pred)

    # kmeans_4_train
    kmeans_4_train = KMeans(init="k-means++",n_clusters=4,max_iter=50,n_init=10,random_state=0,tol=0.05)
    kmeans_4_train.fit(sd_train)
    completeness = (metrics.cluster.completeness_score(data_train['cluster'], kmeans_4_train.labels_), metrics.cluster.completeness_score(data_test['cluster'], kmeans_4.labels_))

    # List of cluster names sorted in desc order by Euclidean distance between respective clusters center estimated by kmeans_opt and first observation in sd_test
    max_opt_distances = []
    sd_test_np = sd_test.to_numpy()
    for centroid in kmeans_opt.cluster_centers_:
        max_opt_distances.append(distance.euclidean(sd_test_np[0],centroid))

    return {
        "sd_train": sd_train,
        "sd_test": sd_test,
        "wcss": wcss_list,
        "kmeans_opt": kmeans_opt,
        "silhouette": silhouette_avg, # s-score (flost) based on grouping from kmeans_opt and sd_train
        "completeness": completeness, #  based on grouping from kmeans_opt, sd_train and sd_test
        "labels_predicted": kmeans_opt.labels_, #list of assigned clusters based on kmeans_opt and sd_test
        "max_opt": np.flip(np.argsort(max_opt_distances)), # list of cluster names sorted in desc order by Euclidean distance between respective clusters center estimated by kmeans_opt and first obs in sd_test
    }
