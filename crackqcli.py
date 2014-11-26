#!/usr/bin/env python
#
# Vitaly Nikolenko
# vnik@hashcrack.org
# v0.11

import requests
import json
import sys
import getopt
import os

SERVER = 'http://hashcrack.org'
ENDPOINTS = {
                'user_email' : '/crackq/v0.1/user_email',
                'submit'     : '/crackq/v0.1/submit'
            }
API_KEY = None

def usage(argv0):
    print '%s [-t|--type] md5|ntlm hash' % argv0
    print '-t --type        hash type, either md5 or ntlm'
    print '-h --help        help'

def validate_hash(_hash):
    if len(_hash) != 32:
        print 'Invalid hash'
        return False
    try:
        int(_hash, 16)
    except ValueError:
        print 'The hash is not in hex'
        return False

    return True

def save_config():
    global API_KEY

    home_path = os.getenv("HOME")
    sys.stdout.write('Enter your api key: ')
    key = sys.stdin.readline().strip()

    try:
        conf = open(home_path + '/.crackq', 'w')
    except IOError:
        print 'Cannot write to %s' % home_path
        sys.exit(-1)
        
    conf.write('key:%s\n' % key)
    API_KEY = key

def load_config():
    global API_KEY

    home_path = os.getenv("HOME")
    try:
        conf = open(home_path + '/.crackq', 'r')
        for l in conf.readlines():
            k, v = l.split(':')
            if k == 'key':
                API_KEY = v.strip()
        if not API_KEY:
            print 'api key is not found'
            sys.exit(-1)
    except IOError:
        save_config()

if __name__ == '__main__':
    _hash = None
    _type = None

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 't:h', ['type=', 'help'])
    except getopt.GetoptError as err:
        print str(err)
        usage(sys.argv[0])
        sys.exit(-1)

    for o, a in optlist:
       if o in ('-h', '--help'):
           usage(sys.argv[0])
           sys.exit()
       if o in ('-t', '--type'):
           _type = a

    if len(args) != 1:
       usage(sys.argv[0])
       sys.exit(-1)

    _hash = args[0]
     
    if not validate_hash(_hash):
        sys.exit(-1)
                
    if not _type or (_type != 'ntlm' and _type != 'md5'):
        print 'Hash type is invalid'
        sys.exit(-1)

    load_config()
 
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'key': API_KEY}
    r = requests.post(SERVER + ENDPOINTS['user_email'], data=json.dumps(data), headers=headers)

    if r.status_code != 200:
        print 'There was an error retrieving user information.'
        print r.json()['msg']
        sys.exit(-1)

    print 'Results will be emailed to %s' % r.json()['email']
    data = {'key': API_KEY, 'hash': _hash, 'type': _type}
    r = requests.post(SERVER + ENDPOINTS['submit'], data=json.dumps(data), headers=headers)

    if r.status_code != 201:
        print 'There was an error submitting the hash.'

    print r.json()['msg']
