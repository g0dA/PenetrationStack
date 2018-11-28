#!/usr/bin/env python
from web3 import Web3, HTTPProvider, IPCProvider
import requests
import json
import multiprocessing


#默认端口为8545或者8546
#检测是否到达最高
def blocknumber(ip):
    try:
        web3 = Web3(HTTPProvider('http://'+ip+':8545'))
        if web3.eth.blockNumber > 5310000:
            #print('http://'+ip.strip()+':8545 ==> the blockNumber is:'+str(web3.eth.blockNumber))
            return True
    except:
        return False

#获取节点所有的用户
def accounts(ip):
    accounts_req = '{"jsonrpc":"2.0","method":"eth_accounts","params":[""],"id":1}' 
    
    url = 'http://'+ip+':8545'
    accounts = requests.post(url,data=accounts_req,headers=headers)
    if 'result' in json.loads(accounts.text).keys():
        account_list = json.loads(accounts.text)['result']
        if len(account_list) > 0:
            return account_list
        else:
            return 0
    else:
        return 0

#获取对应帐号的余额
def getblance(ip,account):
    
    balance_req = '{"jsonrpc":"2.0","method":"eth_getBalance","params":["'+account+'", "latest"],"id":1}' 
    
    url = 'http://'+ip+':8545'
    
    blanceNum = requests.post(url,data=balance_req,headers=headers)
    blance = json.loads(blanceNum.text)['result']
    if blance != '0x0':
        print('http://'+ip+':8545 ==> the blockNumber of '+account+' is '+str(blance))
    else:
        return 0

def run(ip):
    if blocknumber(ip):
        accounts_list = accounts(ip)
        if accounts_list:
            pool = multiprocessing.Pool()
            for account in accounts_list:
                pool.apply_async(getblance, args=(ip, account))
            pool.close()
            pool.join()
            
        

if __name__ == "__main__":
    headers = {'Content-Type':'application/json'}
    ips = open('1.txt','r')
    for ip in ips:
        try:
            run(ip.strip())
        except:
            pass
    
    
