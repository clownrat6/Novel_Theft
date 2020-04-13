import os
import requests

from util import pic_write
from parse import txt_page_parse,illustration_page_parse,pic_parse
from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED

def download_txt(get_dict, base_dir):
    executor = ThreadPoolExecutor(max_workers=10)
    thread_task_list = []
    volume_list = get_dict.keys()
    ifcomplete = True
    for volume in volume_list:
        volume_dir = os.path.join(base_dir, volume)
        chapter_list = get_dict[volume].keys()
        if('插图' not in chapter_list): continue
        if(not os.path.exists(volume_dir)):
            os.makedirs(volume_dir, 0x777)
        index = 0
        for chapter in chapter_list:
            if(chapter == '插图'): continue
            index += 1
            txt_page_url = get_dict[volume][chapter]
            chapter_txt_path = os.path.join(volume_dir, '{}${{{}}}.txt'.format(index, chapter))
            if(os.path.exists(chapter_txt_path)): continue
            ifcomplete = False
            thread_task_list.append(executor.submit(txt_page_parse, txt_page_url, chapter_txt_path))
    
    if(ifcomplete): print('txt source has been downloaded completely.')
    return thread_task_list

def download_illustration(get_dict, base_dir):
    executor = ThreadPoolExecutor(max_workers=10)
    thread_task_list = []
    volume_list = get_dict.keys()
    ifcomplete = True
    for volume in volume_list:
        volume_dir = os.path.join(base_dir, volume)
        if(not os.path.exists(volume_dir)):
            os.makedirs(volume_dir, 0x777)
        chapter_list = get_dict[volume].keys()
        for chapter in chapter_list:
            if(chapter != '插图'): continue
            illustration_page_url = get_dict[volume][chapter]
            chapter_illustration_path = os.path.join(volume_dir, '{}'.format(chapter))
            if(not os.path.exists(chapter_illustration_path)):
                os.mkdir(chapter_illustration_path)
            illustration_url_list = illustration_page_parse(illustration_page_url)
            illustration_path = os.path.join(chapter_illustration_path, 'cover.jpg')
            if(not os.path.exists(illustration_path)):
                thread_task_list.append(executor.submit(pic_parse, illustration_url_list[0], illustration_path))
            index = 0
            for illustration in illustration_url_list:
                index += 1
                illustration_path = os.path.join(chapter_illustration_path, '{}.jpg'.format(index))
                if(os.path.exists(illustration_path)): continue
                ifcomplete = False
                print(illustration_path, 'downloading...')
                thread_task_list.append(executor.submit(pic_parse, illustration, illustration_path))
    
    if(ifcomplete): print('illustration source has been downloaded completely.')
    return thread_task_list
            