# -*- coding: utf-8 -*-
"""Youtube_Comments_Spam_Classifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dcTjMBZPMJpKJF-yC2fSkRbE1g4M_oq8

# Importing Libraries
"""

import numpy as np
import pandas as pd

"""# Importing Dataset"""

url = "https://drive.google.com/u/0/uc?id=1XzIeLE07nHzAAA_5tn1jpBK5jUXVJKQP&export=download&confirm=t&uuid=d4e9cdd6-d26e-4465-8d6a-56b77fb12d5c&at=ANzk5s5WEaHIfSx8QnlTchRlUPmG:1680160425959"

df = pd.read_csv(url)

"""# Dataset"""

df

"""# Handling Null Values"""

print(df.isnull().sum())  # prints columnwise missing values in dataset

# Identify null values in 'Comment (Actual)'
null_values = df['Comment (Actual)'].isnull()

# Drop rows with null values in 'Comment (Actual)'
df.drop(df[null_values].index, inplace=True)

print(df.isnull().sum())  # prints columnwise missing values in dataset

# Identify null values in 'Comment Author Channel ID'
null_values = df['Comment Author Channel ID'].isnull()

# Drop rows with null values in 'Comment Author Channel ID'
df.drop(df[null_values].index, inplace=True)

print(df.isnull().sum())  # prints columnwise missing values in dataset

"""# Dropping Unnecessary Columns"""

list(df.columns)

df=df.drop(df.columns[[0,4,6,8]], axis=1,)
list(df.columns)

"""# Final Dataset"""

rows, columns = df.shape
print("Number of rows : ", rows)
print("Number of columns : ", columns)

"""# Unique Youtube Videos"""

unique_videos = df['Video ID'].unique()
print("Number of Unique Videos After Preprocessing: ", len(unique_videos))

"""# Textual Preprocessing"""

'''
    Takes in a string of text, then performs the following:
    1. Remove all punctuation
    2. Remove all stopwords
    3. Return the cleaned text as a list of words
    4. Remove words
'''
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')


import string
def text_process(text):
    stemmer = WordNetLemmatizer()
    nopunc = [char for char in text if char not in string.punctuation]
    nopunc = ''.join([i for i in nopunc if not i.isdigit()])
    nopunc =  [word.lower() for word in nopunc.split() if word not in stopwords.words('english')]
    return [stemmer.lemmatize(word) for word in nopunc]

#testing the function with a sample text#
sample_text = "I Love IITJ 3000! But I hate 123Mess {Food}%456!"
print(text_process(sample_text))

"""# Vectorization of the Comments and Video Description"""

from sklearn.feature_extraction.text import TfidfVectorizer
# Reducing Features to 30000 and takeing only best features
tfidfconvert = TfidfVectorizer(analyzer = text_process, max_features = 30000).fit(df.iloc[:,3]) # Takes approx 15 min

len(tfidfconvert.vocabulary_)

# Vectorization of first 2000 comments
comments_transformed = tfidfconvert.transform(df.iloc[:20000 ,3]).toarray()

"""# Dimensionality Reduction with TruncatedSVD"""

from sklearn.decomposition import TruncatedSVD


# create a new TruncatedSVD object with the desired number of components
n_components = 80
svd = TruncatedSVD(n_components=n_components)

# fit the TruncatedSVD object to the data and transform the data
comments_transformed_pca = svd.fit_transform(comments_transformed)

print("Number of PCA :", len(comments_transformed_pca[0]))
print()

# plot the first two principal components
import matplotlib.pyplot as plt
plt.scatter(comments_transformed_pca[:, 0], comments_transformed_pca[:, 1])
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.show()

"""# K-Means Clustering"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

scores = []

for n_clusters in range(2, 21):
    kmeans = KMeans(n_init = 10,n_clusters=n_clusters, random_state=42)
    kmeans.fit(comments_transformed_pca)
    labels = kmeans.labels_
    sil_score = silhouette_score(comments_transformed_pca, labels)
    scores.append(sil_score)

# find the value of n_clusters that gives the maximum Silhouette score
best_n_clusters = np.argmax(scores) + 2  # add 2 because we started from 2 in the loop
best_sil_score = max(scores)
print("Best Value of N_Clusters : ", best_n_clusters)
print("Silhouette Score : ", best_sil_score)

kmeans = KMeans(n_init = 10, n_clusters=best_n_clusters, random_state=42)
kmeans.fit(comments_transformed_pca)
labels = kmeans.labels_

# ClusterWise Diving and Printing comments
comments_original = df.iloc[:1000,3]
vectorized_comments = {}
comments = {}
for i in range(17):
  vectorized_comments[i] = []
  comments[i] = []

for i in range(len(labels)):
  vectorized_comments[labels[i]].append(comments_transformed_pca[i])
  comments[labels[i]].append(comments_original[i])


for i in range(17):
  print()
  print("Cluster "+ str(i))
  print()
  index = 1
  for j in comments[i]:
    print(str(index) + ") " + j)
    index += 1
# No useful cluster formed which contains all spam comments

"""# Z-*Score* Method"""

from sklearn.ensemble import IsolationForest
from scipy.stats import zscore

# Labeling Spams and Non Spam Comments
labels1 = np.empty(len(comments_transformed_pca))
labels1.fill(0)

for i in range(200):
  z_scores = zscore(comments_transformed_pca[i*100:(i+1)*100])

  # Setting Threshold which detects best outliers(spam comment) by trail and testing error
  threshold = 2
  outlier_indices = np.where(np.abs(z_scores) > threshold)[0]
  labels1[outlier_indices] = 1




# Printing Spam and Non Spam Comments
comments_original = df.iloc[:20000,3].values

spam_comments = []
non_spam_comments = []

for i in range(len(comments_original)):
  if labels1[i] == 0:
    non_spam_comments.append(comments_original[i])
  elif labels1[i] == 1:
    spam_comments.append(comments_original[i])


z_scores = zscore(comments_transformed_pca)


print("Spam Comments : ")
index = 0
for comment in spam_comments:
  print(str(index) + ") " + comment)
  index += 1
print()

# Commented to see spam comments better
# print("Non-Spam Comments : ")
# index = 0
# for comment in non_spam_comments:
#   print(str(index) + ") " + comment)
#   index += 1

"""# LocalOutlierFactor Model"""

from sklearn.neighbors import LocalOutlierFactor

labels2 = np.empty(len(comments_transformed_pca))
labels2.fill(0)

for i in range(200):
  lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
  y_pred = lof.fit_predict(comments_transformed_pca[i*100:(i+1)*100])

  # Find the indices of the outlier points
  outlier_indices = np.where(y_pred == -1)[0]

  # Labeling Spams and Non Spam Comments
  labels2[outlier_indices] = 1


# Printing Spam and Non Spam Comments
comments_original = df.iloc[:20000,3].values

spam_comments = []
non_spam_comments = []

for i in range(len(comments_original)):
  if labels2[i] == 0:
    non_spam_comments.append(comments_original[i])
  elif labels2[i] == 1:
    spam_comments.append(comments_original[i])

print("Spam Comments")
index = 0
for comment in spam_comments:
  print(str(index) + ") " + comment)
  index += 1
print()

# Commented to see spam comments better
# print("Non Spam Comments")
# index = 0
# for comment in non_spam_comments:
#   print(str(index) + ") " + comment)

#   index += 1

"""# OneClassSVM Model"""

from sklearn import svm


# Labeling Spams and Non Spam Comments
labels3 = np.empty(len(comments_transformed_pca))
labels3.fill(0)

# Create an One-Class SVM object and fit the data
for i in range(200):
  clf = svm.OneClassSVM(nu=0.1, kernel='rbf', gamma=5)
  clf.fit(comments_transformed_pca[100*i:100*(i+1)])

# Predict the outliers
  y_pred = clf.predict(comments_transformed_pca)
  outlier_indices = np.where(y_pred == -1)
  labels3[outlier_indices] = 1


# Printing Spam and Non Spam Comments
comments_original = df.iloc[:20000,3].values

spam_comments = []
non_spam_comments = []


for i in range(len(comments_original)):
  if labels3[i] == 0:
    non_spam_comments.append(comments_original[i])
  elif labels3[i] == 1:
    spam_comments.append(comments_original[i])

print("Spam Comments")
index = 0
for comment in spam_comments:
  print(str(index) + ") " + comment)
  index += 1
print()

# Commented to see spam comments better
# print("Non Spam Comments")
# index = 0
# for comment in non_spam_comments:
#   print(str(index) + ") " + comment)

#   index += 1

"""# Ensemble Learning"""

# Getting Final Labels By Voting of 3 models
labels = []
for i in range(len(labels1)):
  spam = 0
  if(labels1[i] == 1):
    spam += 1
  if(labels2[i] == 1):
    spam += 1
  # if(labels3[i] == 1):
  #   spam += 1
  if(spam >= 1):
    labels.append(1)
  else:
    labels.append(0)

labels = np.array(labels)
# Printing Spam and Non Spam Comments
comments_original = df.iloc[:1000,3]

spam_comments = []
non_spam_comments = []

for i in range(len(comments_original)):
  if labels[i] == 0:
    non_spam_comments.append(comments_original[i])
  elif labels[i] == 1:
    spam_comments.append(comments_original[i])

print("Spam Comments")
index = 0
for comment in spam_comments:
  print(str(index) + ") " + comment)
  index += 1
print()

# Commented to see spam comments better
# print("Non Spam Comments")
# index = 0
# for comment in non_spam_comments:
#   print(str(index) + ") " + comment)

#   index += 1

"""# Decision Tree Classifier"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Knn did'nt gave effective results
# knn = KNeighborsClassifier(n_neighbors = 2)
# knn.fit(comments_transformed, labels)
# comments_transformed_remaining = tfidfconvert.transform(df.iloc[1000:,3])
# labels_remaining = knn.predict(comments_transformed_remaining)

clf = DecisionTreeClassifier(random_state=42)
clf.fit(comments_transformed, labels)
comments_transformed_remaining = tfidfconvert.transform(df.iloc[20000:,3])  # Takes Approx 17 minutes
labels_remaining = clf.predict(comments_transformed_remaining)


final_labels = np.concatenate([labels, labels_remaining])
comments_original = df.iloc[20000:,3].values

spam_comments = []
non_spam_comments = []

for i in range(len(comments_original)):
  if labels_remaining[i] == 0:
    non_spam_comments.append(comments_original[i])
  elif labels_remaining[i] == 1:
    spam_comments.append(comments_original[i])

print("Spam Comments")
index = 0
for comment in spam_comments:
  print(str(index) + ") " + comment)
  index += 1
print()