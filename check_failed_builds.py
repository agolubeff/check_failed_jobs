#!/usr/bin/python

import json 
import sys
import urllib2
import os.path

if len(sys.argv) < 2:
    print "Usage:", sys.argv[0], "filename"
    exit(1)

failed_number = 0
job_dict = {} 
failed_dict = {}
jobs_file = sys.argv[1]

if not os.path.isfile(jobs_file) and os.access(jobs_file, os.RW_OK):
    print "Job list file doesn't exist or can't be opened."
    exit(1)

with open(jobs_file) as f:
    for line in filter(None, (line.rstrip() for line in f)):
       try:
           url, bldno = (line.strip('\n').split(","))
       except ValueError, e:
           url, bldno = (line.strip('\n'),-1)

       job_dict[url] = bldno
       try:
           jenkinsStream = urllib2.urlopen( url + "/lastFailedBuild/api/json" )
       except urllib2.HTTPError, e:
           print url + "/lastFailedBuild/api/json:", e
           continue
       try:
           buildStatusJson = json.load( jenkinsStream )
       except Exception:
           continue
        
       if buildStatusJson["number"] > int(job_dict[url]):
           if job_dict[url] != '-1':
               failed_number += 1
               failed_dict[url] = buildStatusJson["number"]
       job_dict[url] = buildStatusJson["number"]
            
if failed_number > 0:
    print "You have " + str(failed_number) + " failed jobs since last run.\nLatest failed builds: "
    for k,v in failed_dict.items():
        print " ",k + "/" + str(v)

with open(jobs_file, "w") as out_file:
    for k,v in job_dict.items():
        out_file.write(k + "," + str(v) + '\n')

sys.exit(0)
