import os
import threading

from parse import main_parse, page_parse, target_parse, \
                  illustration_parse, chapter_parse

def target_thread(url, target_key, base_path):
    target_path = '{}/{}'.format(base_path, target_key)

    if not os.path.exists(target_path):
        os.makedirs(target_path, 0x777)

    main_dict = main_parse(url)

    for key in main_dict.keys():
        chapter_parse(main_dict, key, target_path)

def pic_download_thread(txt_path):
    base_path = os.path.split(txt_path)[0]
    save_path = os.path.join(base_path, 'illustration')

    if(not os.path.exists(save_path)):
        os.makedirs(save_path, 0x777)
    
    with open(txt_path, 'r') as f:
        lines = f.readlines()
        for line in lines: