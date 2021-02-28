#!/usr/bin/env python3

VERSION = '1.0a1'

import os
import re
import sys
import argparse
import pathlib


def error(text):
    print('error: ' + text, file=sys.stderr)
    exit(1)

def warning(text):
    print('warning: ' + text, file=sys.stderr)

def check_option(args, option):
    if option not in args.__dict__:
        return
    
    value = args.__dict__[option]
    
    if len(value) < 2:
        error(f"option {option} has an invalid value {value}")
    elif len(value) == 2:
        if value[0] !='-' or not value[1].isalnum():
            error(f"option {option} has an invalid value {value}")
    elif len(option) > 2:
        if value[:2] != '--' or re.search(r'[^\w-_]', value[2:]):
            error(f"option {option} has an invalid value {value}")

    return

def format_option(name, value='', flag=False):
    if not value and not flag:
        return ''
        
    if flag:
        return name + ' '
    
    if len(name) > 2 and name[:2] == '--':
        return f"{name}={value} "
    
    return f"{name} {value} "
    
parser = argparse.ArgumentParser(description='Create connection parameters and .pgpass from postgres: URI', add_help=False)

parser.add_argument('uri', type=str, nargs='*',
                    help='uri (may be specified as components)')
parser.add_argument('--pgpass', dest='pgpass', type=pathlib.Path,
                    help='create or append to a .pgpass file at the specified path')
parser.add_argument('-d', '--dbname', dest='dbname', default='--dbname',
                    help='name of the parameter specifying the database')
parser.add_argument('-h', '--host', dest='host', default='--host',
                    help='name of the parameter specifying the host')
parser.add_argument('-p', '--port', dest='port', default='--port',
                    help='name of the parameter specifying the port')
parser.add_argument('-U', '--username', dest='username', default='--username',
                    help='name of the parameter specifying the username')
parser.add_argument('-w', '--no-password', dest='nopassword', default='--no-password',
                    help='name of the no-password parameter')
parser.add_argument('-W', '--password', dest='password', action='store_true', default=False,
                    help='generate a --password option')
parser.add_argument('--help', dest='print_help', action='store_true', default=False,
                    help='print help and exit')
parser.add_argument('--version', dest='print_version', action='store_true', default=False,
                    help='print version and exit')

args = parser.parse_args()

if args.print_version:
    print('Version ' + VERSION)
    if not args.print_help:
        exit(0)

if args.print_help:
    parser.print_help()
    exit(0)

if not len(args.uri):
    error("t least one uri component is required")

check_option(args, 'dbname')
check_option(args, 'host')
check_option(args, 'port')
check_option(args, 'username')
check_option(args, 'nopassword')

uri = ''.join(args.uri)

(scheme_user, _, host_path) = uri.partition('@')

if not scheme_user:
    error("no scheme/user component found")
    
if not host_path:
    error("no host/path component found")

(scheme, _, user_password) = scheme_user.partition('//')

if scheme != 'postgres:':
    error(f"scheme must be 'postgres:', found '{scheme}'")

if not user_password:
    error("no user/password component found")

(username, _, password) = user_password.partition(':')

if not username:
    error("no username found")

(host_port, _, database) = host_path.partition('/')

if not host_port:
    error("no host/port component found")

if not database:
    error("no database name found")

(host, _, port) = host_port.partition(':')

if not host:
    error("no host found")

if port and not port.isnumeric():
    error("port must be numeric")

if password and not args.pgpass:
    warning("password component included but .pgpass file not specified")

output = format_option(args.dbname, database)
output += format_option(args.host, host)
output += format_option(args.port, port)
output += format_option(args.username, username)

if args.password:
    output += format_option(args.password, flag=True)
else:
    output += format_option(args.nopassword, flag=True)

print(output)

if args.pgpass:
    with open(args.pgpass / '.pgpass', 'at') as pgpass_file:
        pgpass_tuple = [ host ]
        pgpass_tuple.append(port)
        pgpass_tuple.append(database)
        pgpass_tuple.append(username)
        pgpass_tuple.append(password)
        
        pgpass_line = [ (c if c else '*') for c in pgpass_tuple ]
        print(':'.join(pgpass_line), file=pgpass_file)
    
    os.chmod(args.pgpass / '.pgpass', 0o600)

        
