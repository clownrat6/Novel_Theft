import os
import threading

from parse import main_parse, txt_page_parse, target_parse, \
                  illustration_page_parse, chapter_parse, pic_parse, cover_parse
from util import pic_write

def target_thread(url, target_key, base_path):
    target_path = '{}/{}'.format(base_path, target_key)

    if not os.path.exists(target_path):
        os.makedirs(target_path, 0x777)

    main_dict = main_parse(url)

    # 下载书籍部分
    for key in main_dict.keys():
        chapter_parse(main_dict, key, target_path)

    # 下载封面
    cover_url = url.replace('https://', '')
    cover_url = cover_url.replace('http://', '')
    cover_url = cover_url.split('/')
    cover_url = 'https://' + cover_url[0] +  '/book/' + str(cover_url[3]) + '.htm'
    cover_url = cover_parse(cover_url)
    print(cover_url)
    cover_path = target_path + '/cover.jpg'
    if(os.path.exists(cover_path)): return None
    pic_write(pic_parse(cover_url), cover_path)

def target_main_thread_list(target_dict, base_path):
    target_keys = list(target_dict.keys())
    # 创建线程
    thread_list = []
    for target in target_keys:
        thread_single = threading.Thread(target=target_thread, \
                        args=(target_dict[target], target, base_path))
        thread_list.append(thread_single)

    return thread_list

def pic_download_thread_list(txt_path):
    base_path = os.path.split(txt_path)[0]
    save_path = os.path.join(base_path, 'illustration')

    if(not os.path.exists(save_path)):
        os.makedirs(save_path, 0x777)
    
    thread_list = []
    with open(txt_path, 'r') as f:
        lines = f.readlines()
        index = 0
        for line in lines:
            index += 1
            pic_path = os.path.join(save_path, '{}.jpg'.format(index))
            if(os.path.exists(pic_path)): continue
            line = line.strip()
            pic_thread = threading.Thread(target=lambda save_path,url:pic_write(pic_parse(url), save_path), \
                                          kwargs={"save_path":pic_path, "url":line})
            thread_list.append(pic_thread)
    
    return thread_list

def target_pic_thread_list(target_dict, base_path):
    target_keys = list(target_dict.keys())
    # 创建线程
    thread_list = []
    for target_key in target_keys:
        target_path = os.path.join(base_path, target_key)
        
        chapter_list = os.listdir(target_path)
        
        for chapter in chapter_list:
            if(chapter == 'cover.jpg'): continue
            chapter_path = os.path.join(target_path, chapter)
            item_list = os.listdir(chapter_path)
            for item in item_list:
                if('插图' in item): 
                    item_path = os.path.join(chapter_path, item)
                    additional = pic_download_thread_list(item_path)
                    thread_list += additional

    return thread_list

            