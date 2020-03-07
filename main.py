import os
import time
import threading
import _thread

from parse import target_parse
from thread_task import target_main_thread_list, target_pic_thread_list
from arg_parser import arg_parser

# base information
target_dict = target_parse('target.txt')
base_path = 'build'

arg = arg_parser()
arg.add_val('--task', 'main')
arg_dict = arg()

thread_list = []
if(arg_dict['--task'] == 'main'):
    thread_list = target_pic_thread_list(target_dict, base_path)
    print("txt content downloading!!")
else if(arg_dict['--task'] == 'picture'):
    thread_list = target_main_thread_list(target_dict, base_path)
    print("illustration downloading!!")

for thread in thread_list:
    thread.start()

for thread in thread_list:
    thread.join()

print("done!!")
