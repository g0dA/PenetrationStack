#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import dns.resolver
import os
import threading


dic_path = raw_input('\033[1;32m请输入域名字典文件的路径:\033[0m')
dic = open(dic_path,'r')
domain_list = dic.readlines()
dic.close()
takeover = []
def check_subdomain_takeover(domain):
    #if CNAME
    try:
        CNAME = dns.resolver.query(domain,'CNAME')
        for i in CNAME.response.answer:
            for j in i.items:
                cname = j.to_text()[:-1]
    
        # if equeal
        if cname not in domain:
        #ping test
            exit_code = os.system('ping -c 3 '+domain)
            if exit_code:
                print "\033[1;32m"+domain+" can takeover,CNAME is "+cname+"\033[0m"
                takeover.append(domain)
            else:
                print "\033[1;31m"+domain+" can't be takeover("+cname+" is alive)\033[0m"
        else:
            print "\033[1;31m"+domain+" can't be takeover(cname is "+cname+")\033[0m"
    except:
        print "\033[1;31m"+domain+" have no CNAME\033[0m"
    
    if takeover != []:
        print "\033[1;32m"+str(takeover)+" can be takeover :)"
    
if __name__ == '__main__':

    for domain in domain_list:
        t = threading.Thread(target=check_subdomain_takeover,args=(domain[:-1],))
        t.start()
   