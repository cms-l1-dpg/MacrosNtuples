#!/bin/python3

import argparse
import os

automation_path = os.path.dirname(os.path.abspath(__file__))

# parse commands to be executed as arguments
parser = argparse.ArgumentParser(description="wrapper running script on htcondor")
parser.add_argument('cmd', nargs='+', type=str, help='commands to be executed')
args = parser.parse_args()

concatenated_cmd = ' '.join(args.cmd)
concatenated_cmd = concatenated_cmd.replace("___", " ")
concatenated_cmd = f'cd {automation_path}; ' + concatenated_cmd

print('command executed: ' + concatenated_cmd)
os.system(concatenated_cmd)
