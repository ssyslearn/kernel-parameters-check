#!/usr/bin/env python
import re
import subprocess


def lines_to_dict(lines):
    dict = {}
    lines[:] = [s.split('#')[0].strip() for s in lines if re.match(r'^[^ #]+', s)]
    lines[:] = [re.sub(r'\s+', ' ', s) for s in lines]
    for line in lines:
        dict[line.split('=')[0].strip()] = line.split('=')[1].strip()
    return dict

def calculate_line_length(live_dict, except_list):
	key_len = 0
	value_len = 0
	for key in live_dict:

		if key in except_list:
			continue

		if len(key) > key_len:
			key_len = len(key) + 2
		if len(live_dict[key]) > value_len:
			value_len = len(live_dict[key]) + 2
	return key_len + value_len*2 + 4 , key_len, value_len

def print_horizontal_line(n):
	for i in range(n):
		print '=',
	print '\n'


def print_columns():
	print '%*s %*s %*s %*s\n' % (-key_len, 'KERNEL PARAMETER', -value_len, 'ORG VALUE', -value_len, 'CONF VALUE', -value_len, 'LIVE VALUE')

def print_params(except_list, merge_dcit, live_dict, key_len, value_len):
	for key in live_dict:
		if key in except_list:
			continue
		if key in merge_dict:
			if key not in org_dict:
				org_dict[key] = ""
				if merge_dict[key] != live_dict[key]:
					print '%*s %*s %*s %*s\n' % (-key_len, key, -value_len, org_dict[key], -value_len, merge_dict[key], -value_len, live_dict[key])
			else:
				if merge_dict[key] != live_dict[key]:
					print '%*s %*s %*s %*s\n' % (-key_len, key, -value_len, org_dict[key], -value_len, merge_dict[key], -value_len, live_dict[key])


if __name__ == "__main__":
    except_src = './except_list.txt'
    org_src = './sysctl.conf.org'
    conf_src = '/etc/sysctl.conf'
    
    merge_dict = {}

    with open(except_src, 'r') as f:
        except_list = f.read().splitlines()
    #print except_list

    with open(org_src, 'r') as f:
        org_lines = f.read().splitlines()
        org_dict = lines_to_dict(org_lines)
        merge_dict = lines_to_dict(org_lines)
    #print org_dict

    with open(conf_src, 'r') as f:
        conf_lines = f.read().splitlines()
        conf_dict = lines_to_dict(conf_lines)
    #print conf_dict

    for key in conf_dict:
		merge_dict[key] = conf_dict[key]
    #print merge_dict

    live_list = subprocess.Popen(["sysctl", "-a"], stdout=subprocess.PIPE).communicate()[0]
    live_dict = lines_to_dict(live_list.strip().split('\n'))
    #print live_dict

    n, key_len, value_len = calculate_line_length(live_dict, except_list)
    print_horizontal_line(n)
    print_columns()
    print_horizontal_line(n)
    print_params(except_list, merge_dict, live_dict, key_len, value_len)
    print_horizontal_line(n)
