#!/usr/bin/env python
import re
import subprocess

except_src = './except_list.txt'
org_src = './sysctl.conf.org'
conf_src = '/etc/sysctl.conf'

def lines_to_dict(lines):
    dict = {}
    lines[:] = [s.split('#')[0].strip() for s in lines if re.match(r'^[^ #]+', s)]
    lines[:] = [re.sub(r'\s+', ' ', s) for s in lines]
    for line in lines:
        dict[line.split('=')[0].strip()] = line.split('=')[1].strip()
    return dict


if __name__ == "__main__":
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
