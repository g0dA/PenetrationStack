#!/usr/bin/env python2
#coding=utf-8

import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#提取Version
    
def get_version(text,rule,patch):
    v = re.search(rule,text)
    if v:
        v=v.group()
        for p in patch:
            v = v.replace(p,'')
        return v
    return 'Other'

def Version_check(Version,Object):
    #True,error,header,content,index
    #判断是否能读取Vesion
    if len(Version)>1:
        point = Version[0]
        rule = Version[1]
        patch = Version[2].split(',')
        if point == 'True':
            version = rule
        elif point == 'header':
            version = get_version(str(Object[0]),rule,patch)
        elif point == 'error':
            version = get_version(Object[1],rule,patch)
        elif point == 'index':
            version = get_version(Object[2],rule,patch)
        else:
            if len(Object)>2:
                version = get_version(Object[3],rule,patch)
        if version != 'Other':
            return version
    return 'Other'
    
#单个规则清洗
def check_rule(text):
    Name,Rules,Type,Version=text.strip().split('=>')
    ervery_rule = Rules[1:-1].split('$')
    Version = Version.strip().split('%')
    return Name,ervery_rule[:-1],Type,Version

#单个检测对象属性清洗
def single_rule(rule):
    rule_list = rule.split('|',3)
    path = rule_list[0]
    point = rule_list[1]
    func = rule_list[2]
    match = rule_list[3]
    return path,point,func,match

def finger_check(url,fin):
    try:
        Url_base = url.strip('/')
        Url_error_base = url.strip('/')+'/is_test_error'
        #BaseRequest
        base_request = requests.get(Url_base, timeout=15, verify=False)
        #ErrorBaseRequest
        base_error_request = requests.get(Url_error_base, timeout=15, verify=False)
        
        #四条基础属性
        base_request_headers = base_request.headers
        base_request_content = base_request.text
        base_error_request_headers = base_error_request.headers
        base_error_request_content = base_error_request.text
        
        #单类型多线程
        for i in fin:
            Name,ervery_rule,Type,Version = check_rule(i)
            Object_list=[base_request_headers,base_error_request_content,base_request_content]
            
            #同类型不同规则不可多线程
            for j in ervery_rule:
                path,point,func,match = single_rule(j)
                #路径判断
                #BaseRequest
                if path == '/':
                    if point == 'header':
                        if func in base_request_headers:
                            if re.search(match,base_request_headers[func]):
                               return Name,Version,Type,Object_list
                    #only content
                    else:
                        if func == 'str':
                            if str(match) in base_request_content:
                                return Name,Version,Type,Object_list
                        else:
                            if re.search(match,base_request_content):
                               return Name,Version,Type,Object_list
                         #re or str   
                #ErrorBaseRequest
                elif path == '/is_test_error':
                    if point == 'header':
                        if func in base_error_request_headers:
                            if re.search(match,base_error_request_headers[func]):
                                return Name,Version,Type,Object_list
                    #only content
                    else:
                        #对比ErrorBase
                        if func == 'str':
                            if match in base_error_request_content:
                                return Name,Version,Type,Object_list
                        else:
                            if re.search(match,base_error_request_content):
                                return Name,Version,Type,Object_list 
                else:
                    #构造新请求
                    Uri = Url_base+path
                    new_request = requests.get(Uri, timeout=15, verify=False)
                    new_request_headers = new_request.headers
                    new_request_content = new_request.text
                    #只取第一个，指纹表中version获取页面写在第一条
                    Object_list.append(new_request_content)
                    
                    if point == 'header':
                        if func in new_request_headers:
                            if re.search(match,new_request_headers[func]):
                                return Name,Version,Type,Object_list
                    #only content
                    else:
                        #对比ErrorBase
                        if func == 'str':
                            if match in new_request_content:
                                return Name,Version,Type,Object_list
                        else:
                            if re.search(match,new_request_content):
                                return Name,Version,Type,Object_list
        return 'Other','Other','Other','Other'
    except Exception,e:
        return 'Other','Other','Other','Other'

def start(url):
    #设置检测顺序
    #先测试device，没有结果再检测其余两个
    finger_list = []
    with open('device.fin','r') as device:
        dev = device.readlines()
    finger_info = list(finger_check(url,dev))
    if finger_info[0] == 'Other':
        with open('server.fin','r') as server,open('frame.fin','r') as frame:
            ser = server.readlines()
            finger_info = list(finger_check(url,ser))
            version = Version_check(finger_info[1],finger_info[3])
            finger_info[1] = version
            del finger_info[3]
            finger_list.append(finger_info)
            fra = frame.readlines()
            finger_info = list(finger_check(url,fra))
            version = Version_check(finger_info[1],finger_info[3])
            finger_info[1] = version
            del finger_info[3]
            finger_list.append(finger_info)
            return finger_list
    version = Version_check(finger_info[1],finger_info[3])
    finger_info[1] = version
    del finger_info[3]
    finger_list.append(finger_info)
    return finger_list
                
if __name__ == '__main__':
    url = 'http://www.yongzai.net/'
    
    #第一个反参为Other，则没检测出来
    print start(url)
            
        


