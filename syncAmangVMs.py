#!/usr/bin/python

import time
import os
import hashlib
import cPickle as cp 
import shutil 

import logging

class SyncFundamental():
    def __init__(self,sourceDir = "/home/fabio/tmp/test",destDir = "/home/fabio/test"):
        #default env variables.
        self.linkoping = "150.132.35.142"
        self.name = "efuguxu"
        self.perfBaseDir = sourceDir 
        self.perfDestDir = destDir
        self.localMD5file = self.perfDestDir+os.sep+"oldMD5"
        #local variables.
        self.oldDict = {} 
        self.curDict = {}
        #initialize the logging module.
        Logging()
        
    #get the whole file md5s in recursion and store them into a dictionary.    
    def getCurMD5Dict(self,baseDir):
        for f in os.listdir(baseDir):
            fullFileName = baseDir+os.sep+f
            if os.path.isdir(fullFileName) and not f.startswith("."):
                self.getCurMD5Dict(fullFileName)
            elif os.path.isfile(fullFileName):
                with open(fullFileName) as f :
                    content = f.read()
                #get the file md5 checksum and store them in a Dictionary
                md5 = hashlib.md5(content)
                self.curDict[fullFileName] = md5.hexdigest()

    def getOldMD5Dict(self):
        if os.path.exists(self.localMD5file):
            logging.info("loading oldDict ...")
            self.oldDict = cp.load(open(self.localMD5file,"rb"))
        else :
            self.oldDict = {}

    def dumpFile(self,dataToDump):
        if dataToDump : 
            #print "self.localMD5file : ",self.localMD5file
            cp.dump(dataToDump,open(self.localMD5file,"wb"))

    def checkMD5(self,oldMD5Dict,curMD5Dict):
        diffList = []
        if oldMD5Dict :
            for key in oldMD5Dict: 
                if oldMD5Dict[key] != curMD5Dict[key]:
                    diffList.append(key)
            return diffList
                    
        else:
            return curMD5Dict 
    def syncPreparation(self):
        #preparision steps :
        #1. get the old md5 values
        #2. get the current md5 values
        #3. check the old and current md5 and get the changed file name if there's any
        #4. synchronization the changed file from source to dest.
        #5. dump the current md5 value into file as the old. 
        
        #1. get the old md5 values
        self.getOldMD5Dict()
        #2. get the current md5 values
        self.getCurMD5Dict(self.perfBaseDir)
        #3. compare the old and new md5 value
        #diffList = []
        diffList = self.checkMD5(self.oldDict,self.curDict)         
        #print "oldDict : ",self.oldDict
        #print "curDict : ",self.curDict
        #print "diffList : ",diffList
        #4. synchronization the file 
        if diffList :          
            self.syncPerfFile(diffList)
        else :
            logging.info("the current project is the latest, nothing to copy...")
        #5. update the backup md5 file.
        self.dumpFile(self.curDict)

    def syncPerfFile(self,fileList):
        logging.info("[SYNC] : synchronization starting ...")
        tmpDir = self.perfBaseDir
        for key in fileList :
            #print "key:",key
            baseFolder = key[key.rfind(tmpDir[tmpDir.rfind("/")+1 : ]) : key.rfind("/")] 
            #print "baseFolder : ",baseFolder
            subTargetDir = self.perfDestDir+os.sep+baseFolder
            if not os.path.exists(subTargetDir):
                #print "making subFolders : ",subTargetDir
                os.makedirs(subTargetDir)
            #print "subTargetDir : ",subTargetDir
            logging.info("[SYNC] : %s -> %s"%(key,subTargetDir))
            shutil.copy(key,subTargetDir)    
            #print "---------------------------------------------"
        logging.info("[SYNC] : synchronization completed ...")
        
class Logging(object):
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(filename)s %(levelname)s %(message)s [line:%(lineno)d]',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=os.getcwd()+os.sep+'sync.log',
            filemode='a')

class SyncSchedule(object):
    def __init__(self):
        self.updateInterval = 180.0   
        self.syncFund = SyncFundamental()
    def updateProcess(self):
        while True : 
            self.syncFund.syncPreparation()            
            time.sleep(self.updateInterval)

if __name__ == "__main__":
    scheduleIns = SyncSchedule()
    scheduleIns.updateProcess()
