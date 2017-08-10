#!/usr/bin/env python
import re
import subprocess

def lines_to_dict(lines):
    dict = {}
    lines[:] = [s.strip() for s in lines if re.match(r'^\s*[^ #]+', s)]
    lines[:] = [re.sub(r'\s+', ' ', s) for s in lines]
    for line in lines:
        dict[line.split('=')[0].strip()] = line.split('=')[1].strip()
    return dict

def calculate_line_length(except_list, live_dict):
    key_len = 0
    value_len = 0
    combined = "|".join(except_list) or "No Exception List"
    for key in live_dict:
        if re.match(combined, key):
            continue
        if len(key) > key_len:
            key_len = len(key) + 2
        if len(live_dict[key]) > value_len:
            value_len = len(live_dict[key]) + 2
    return key_len + value_len*3 + 2, key_len, value_len

def print_horizontal_line(n):
    print '=' * n, '\n'

def print_columns():
    print '%*s %*s %*s %*s\n' % (-key_len, 'KERNEL PARAMETER', -value_len, 'ORG VALUE', -value_len, 'CONF VALUE', -value_len, 'LIVE VALUE')

def verify_params(except_list, merge_dict, live_dict, key_len, value_len):
    diff_list = []
    live_load_list = []
    combined = "|".join(except_list) or "No Exception List"
    for key in live_dict:
        if re.match(combined, key):
            continue
        if key in merge_dict:
            if key not in org_dict:
                # only sysctl -p OR both p and w
                org_dict[key] = ""
                if merge_dict[key] != live_dict[key]:
                    diff_list.append(key)
            else:
                # just set /etc/sysctl.conf, but not p
                if merge_dict[key] != live_dict[key]:
                    diff_list.append(key)
        else:
            # only sysctl -w OR live_value ( ex. fs.xfs.* )
            org_dict[key] = ""
            merge_dict[key] = ""
            live_load_list.append(key)
    return diff_list, live_load_list


if __name__ == "__main__":
    except_src = './except_list.txt'
    org_src = './sysctl.conf.org'
    conf_src = '/etc/sysctl.conf'

    merge_dict = {}

    with open(except_src, 'r') as f:
        except_list = f.read().splitlines()
        except_list[:] = [s.split('#')[0].strip() for s in except_list if re.match(r'^\s*[^ #]+', s)]

    with open(org_src, 'r') as f:
        org_lines = f.read().splitlines()
        org_dict = lines_to_dict(org_lines)
        merge_dict = org_dict.copy()

    with open(conf_src, 'r') as f:
        conf_lines = f.read().splitlines()
        conf_dict = lines_to_dict(conf_lines)

    for key in conf_dict:
        merge_dict[key] = conf_dict[key]

    live_list = subprocess.Popen(["sysctl", "-a"], stdout=subprocess.PIPE).communicate()[0]
    live_dict = lines_to_dict(live_list.strip().split('\n'))

    n, key_len, value_len = calculate_line_length(except_list, live_dict)

    # print different parameters from live value
    print_horizontal_line(n)
    print_columns()
    print_horizontal_line(n)
    diff_list, live_load_list = verify_params(except_list, merge_dict, live_dict, key_len, value_len)
    for key in diff_list:
        print '%*s %*s %*s %*s\n' % (-key_len, key, -value_len, org_dict[key], -value_len, merge_dict[key], -value_len, live_dict[key])
    print_horizontal_line(n)
    print 'total', len(diff_list)

    # print live load parameters
    print_horizontal_line(n)
    print '%*s %*s' % (-key_len, 'Live Load Parameter', -value_len, 'LIVE VALUE')
    print_horizontal_line(n)
    for key in live_load_list:
        print '%*s %*s\n' % (-key_len, key, -value_len, live_dict[key])
    print_horizontal_line(n)
    print 'total', len(live_load_list)
