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

def calculate_line_length(live_dict, key_len, value_len):
	for key in live_dict:
		if len(key) > key_len:
			key_len = len(key) + 2
		if len(live_dict[key]) > value_len:
			value_len = len(live_dict[key]) + 2
	return key_len + value_len*2 + 4 

def print_horizontal_line(n):
	for i in range(n):
		print '=',
	print '\n'
	return


def print_columns():
	print 'KERNEL PARAMETER',
	print ' ' * key_len,
	print 'ORG VALUE',
	print ' ' * value_len,
	print 'CONF VALUE',
	print ' ' * value_len,
	print 'LIVE VALUE',
	print ' ' * value_len,
	print '\n'
	return

def print_params(live_dict, key_len, value_len):
	for key in live_dict:
		if merge_dict[key] != live_dict[key]:
			print key,
			print ' ' * key_len,
			print org_dict[key],
			print ' ' * value_len,
			print merge_dict[key],
			print ' ' * value_len,
			print live_dict[key],
			print ' ' * value_len,
			print '\n'
	return


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
        if conf_dict[key] != org_dict[key]:
            merge_dict[key] = conf_dict[key]
    #print merge_dict

    live_list = subprocess.Popen(["sysctl", "-a"], stdout=subprocess.PIPE).communicate()[0]
    live_dict = lines_to_dict(live_list.strip().split('\n'))
    #print live_dict

    key_len = 0
    value_len = 0
    n = calculate_line_length(live_dict, key_len, value_len)
    print_horizontal_line(n)
    print_columns()
    print_horizontal_line(n)
    print_params(live_dict, key_len, value_len)
    print_horizontal_line(n)
