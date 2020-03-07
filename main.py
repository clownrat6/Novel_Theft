import os
import time
import threading
import _thread

from parse import target_parse
from thread_task import target_thread

target_dict = target_parse('target.txt')

target_keys = list(target_dict.keys())

base_path = 'build'

# 创建线程
thread_list = []
for target in target_keys:
    thread_single = threading.Thread(target=target_thread, args=(target_dict[target], target, base_path))
    thread_list.append(thread_single)

for thread in thread_list:
    thread.start()

for thread_list in thread_list:
    thread.join()

thread_list = threading.enumerate()

print(thread_list)
