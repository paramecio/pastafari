#!/usr/bin/python3 -u

import os
import re
import argparse
import json
from subprocess import call, DEVNULL

def add_domain():

    parser=argparse.ArgumentParser(prog='add_domain.py', description='A tool for add domains to /etc/postfix/virtual_domains')

    parser.add_argument('--domain', help='The domain to add', required=True)

    parser.add_argument('--group', help='The group of the domain users', required=True)    

    parser.add_argument('--quota', help='Quota of this group', required=True)
    
    args=parser.parse_args()

    json_return={'error':0, 'status': 0, 'progress': 0, 'no_progress':0, 'message': ''}

    domain_check=re.compile('^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')

    group_check=re.compile('^[a-zA-Z0-9-_]+$')

    if not domain_check.match(args.domain) or not group_check.match(args.group):
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: domain or group is not valid'
        
        print(json.dumps(json_return))

        exit(1)

    json_return['progress']=25
    json_return['message']='Is a valid domain'

    print(json.dumps(json_return))

    #Check if domain exists
    line_domain=args.domain+' '+args.domain
    final_domains=[]
    with open('/etc/postfix/virtual_domains') as f:
        for domain in f:
            if domain.strip()==line_domain:
                json_return['error']=1
                json_return['status']=1
                json_return['progress']=100
                json_return['message']='Error: domain exists in this server'

                print(json.dumps(json_return))

                exit(1)
            else:
                final_domains.append(domain.strip())
    
    final_domains.append(line_domain)

    final_domains_file="\n".join(final_domains)
    
    json_return['progress']=50
    json_return['message']='The domain can be added to server'

    print(json.dumps(json_return))
    with open('/etc/postfix/virtual_domains', 'w') as f:
        if f.write(final_domains_file):
            json_return['progress']=75
            json_return['message']='Domain added'

            print(json.dumps(json_return))
        else:
            json_return['error']=1
            json_return['status']=1
            json_return['progress']=100
            json_return['message']='Error: cannot add the domain to file'

            print(json.dumps(json_return))

            exit(1)

    if call("postmap hash:/etc/postfix/virtual_domains",  shell=True, stdout=DEVNULL) > 0:
        
        json_return['error']=1
        json_return['status']=1
        json_return['progress']=100
        json_return['message']='Error: cannot refresh the domain mapper'

        print(json.dumps(json_return))

        exit(1)    
    
    json_return['status']=1
    json_return['progress']=75
    json_return['message']='Domain added sucessfully'

    print(json.dumps(json_return))

    # add user

    

    exit(0)



if __name__=='__main__':
    add_domain()

