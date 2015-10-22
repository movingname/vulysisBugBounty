This repository contains all data and scripts for our paper:

An Empirical Study of Web Vulnerability Discovery Ecosystems.
Mingyi Zhao, Jens Grossklags and Peng Liu, ACM Conference on Computer and Communications Security (CCS) 2015

**Status**:

We still need to refactor the code and improve the workflow. Also, please contact us if you have any questions, 
comments or suggestions. Thank you!
muz127@ist.psu.edu

**Requirements**:

1. Python 3 (I used [Anaconda](http://continuum.io/downloads))

2. [MongoDB] (https://www.mongodb.org/)

** How to Run the Scripts**:

1. The `data_collection_scripts` folder has all scripts used to collect data from Wooyun. You can run them to get the latest data,
or you can simply import the mongodb data dump in `mongodb_dump.zip`.

2. The `data_analysis_scripts` folder has all scripts used to analyze the Wooyun data. Please setup the mongodb database and run the
mongodb demon before running the scripts.

3. The `scripts_hackerone` folder has all scripts for collecting and analyzing the HackerOne data. We use text files to store the HackerOne
data, so no MongoDB is needed.



**Paper Errata**:

[1] In Table 1, we wrote that Facebook's bug bounty program does not disclose vulnerability reports.
Well after submitting the camera-ready version of the paper, we found out that Facebook maintain a
list of their vulnerability reports disclosed through white hats' blogs. So in a sense, Facebook does partially
disclose reports.

The link for Facebook vulnerability disclosure:
https://www.facebook.com/notes/phwd/facebook-bug-bounties/707217202701640s