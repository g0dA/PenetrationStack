#!/usr/bin/env python2
#coding = utf-8

#Burpsuite module
from burp import IBurpExtender
from burp import IRequestInfo
from burp import IResponseInfo
from burp import IScanIssue
from burp import IScannerCheck


#python module
import sys
sys.path.append('/usr/lib/python2.7/site-packages') #INCLUDE YOUR lib
from array import array
import requests
#Extender describre



class BurpExtender(IBurpExtender,IRequestInfo,IResponseInfo,IScanIssue,IScannerCheck):
    
    
    def registerExtenderCallbacks(self,callbacks):
        
        #keep a reference to our callbacks object
        self._callbacks = callbacks
        
        #helper methods
        self._helpers = callbacks.getHelpers()
        
        #define name
        self._callbacks.setExtensionName("CorsScan")
        #register a scancheck
        callbacks.registerScannerCheck(self)
                        
        return

    def doPassiveScan(self,baseRequestResponse):
        issue = []
        
        vuldetail= self.cors_check(baseRequestResponse)
        if vuldetail[3] == 1:
            NewRequest = self._helpers.buildHttpMessage(vuldetail[0], vuldetail[1])
            
            baseRequestResponse = self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest)
            
            #mark re
            match = self.getMatches(baseRequestResponse,vuldetail[2])
            
            httpmsgs = [self._callbacks.applyMarkers(baseRequestResponse,None,match)]
               
            issue.append(ScanIssue(baseRequestResponse.getHttpService(), self._helpers.analyzeRequest(baseRequestResponse).getUrl(),httpmsgs, vuldetail[4], vuldetail[5], SEVERITY, CONFIDENCE, vuldetail[7], vuldetail[6], REMEDIATION_BACKGROUND))                

        return issue
    #payload code
    
    def cors_check(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = 'http://cors.check'
        vul = 0
        ISSUE_NAME="Cors Vulnerability"
        ISSUE_DETAIL="Cors"
        ISSUE_BACKGROUND="Origin: http://cors.check"
        REMEDIATION_DETAIL="Cors Vulnerability"
        #########################
        baseResponse = self._helpers.bytesToString(baseRequestResponse.getResponse())
        #baseResponse = self._helpers.analyzeResponse(baseRequestResponse)
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        requestHeaders = baseRequest.getHeaders()
        print baseResponse
        if 'Access-Control-Allow-Credentials: true' in baseResponse:
            for singleHeader in requestHeaders:
                if singleHeader.startswith("Origin:"):
                    payload = 'Origin: http://cors.check'
                        # Look for Content-Type Header)
                    singleHeader = payload
    
                new_headers.append(singleHeader)
                        
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            if re in NewResponse:
                vul = 1
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
    

class ScanIssue(IScanIssue):
    def __init__(self, httpService, url, httpmsg,issueName, issueDetail, severity, confidence, remediationDetail, issueBackground, remediationBackground):
        self._issueName = issueName
        self._httpService = httpService
        self._url = url
        self._httpMessages = httpmsg
        self._issueDetail = issueDetail
        self._severity = severity
        self._confidence = confidence
        self._remediationDetail = remediationDetail
        self._issueBackground = issueBackground
        self._remediationBackground = remediationBackground
  
  
    def getConfidence(self):
        return self._confidence
  
    def getHttpMessages(self):
        return self._httpMessages
        #return None
  
    def getHttpService(self):
        return self._httpService
  
    def getIssueBackground(self):
        return self._issueBackground
  
    def getIssueDetail(self):
        return self._issueDetail
  
    def getIssueName(self):
        return self._issueName
  
    def getIssueType(self):
        return 0
  
    def getRemediationBackground(self):
        return self._remediationBackground
  
    def getRemediationDetail(self):
        return self._remediationDetail
  
    def getSeverity(self):
        return self._severity
  
    def getUrl(self):
        return self._url