import os
import threading

from parse import main_parse, txt_page_parse, target_parse, \
                  illustration_page_parse, chapter_parse, pic_parse
from util import pic_write

def target_thread(url, target_key, base_path):
    target_path = '{}/{}'.format(base_path, target_key)

    if not os.path.exists(target_path):
        os.makedirs(target_path, 0x777)

    main_dict = main_parse(url)

    for key in main_dict.keys():
        chapter_parse(main_dict, key, target_path)

def target_main_thread_list(target_dict, base_path):
    target_keys = list(target_dict.keys())
    # 创建线程
    thread_list = []
    for target in target_keys:
        thread_single = threading.Thread(target=target_thread, \
                        args=(target_dict[target], target, base_path))
        thread_list.append(thread_single)
    
    return thread_list

def pic_download(txt_path):
    base_path = os.path.split(txt_path)[0]
    save_path = os.path.join(base_path, 'illustration')

    if(not os.path.exists(save_path)):
        os.makedirs(save_path, 0x777)
    
    with open(txt_path, 'r') as f:
        lines = f.readlines()
        index = 0
        for line in lines:
            index += 1
            pic_path = os.path.join(save_path, '{}.jpg'.format(index))
            if(os.path.exists(pic_path)): continue
                print(pic_path)
            line = line.strip()
            pic_write(pic_parse(line), pic_path)

def target_pic_thread_list(target_dict, base_path):
    target_keys = list(target_dict.keys())
    # 创建线程
    thread_list = []
    for target_key in target_keys:
        target_path = os.path.join(base_path, target_key)
        
        chapter_list = os.listdir(target_path)
        
        for chapter in chapter_list:
            chapter_path = os.path.join(target_path, chapter)
            item_list = os.listdir(chapter_path)
            for item in item_list:
                if('插图' in item): 
                    item_path = os.path.join(chapter_path, item)
                    item_thread = threading.Thread(target=pic_download, kwargs={"txt_path":item_path})
                    thread_list.append(item_thread)

    return thread_list

            