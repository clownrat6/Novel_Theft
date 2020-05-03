import os
import time
import threading
import _thread

from epub import epub_zip
from util import parse_info
from arg_parser import arg_parser
from parse import one_stage_parse,two_stage_parse
from thread import download_txt,download_illustration
from concurrent.futures import wait,ALL_COMPLETED

def main_process(_url):
    # 获取小说文字，插图，名字，作者
    novel_name,author_name,novel_content_url = one_stage_parse(_url)
    content_dict = two_stage_parse(novel_content_url)

    build_dir = 'build/{}'.format(novel_name)

    # 下载小说文字，与插图
    txt_thread_pool = download_txt(content_dict, build_dir)
    illustration_thread_pool = download_illustration(content_dict, build_dir)
    all_task = txt_thread_pool + illustration_thread_pool
    wait(all_task, return_when=ALL_COMPLETED)
    # 打包成 eupb
    epub_zip(novel_name, author_name, 'test', build_dir)

if __name__ == '__main__':
    a = arg_parser()

    a.add_val('--url', 'none')
    a.add_val('--txt', 'none')

    parse_dict = a()
    if(parse_dict['--url'] != 'none'):
        # 现在是以单本书为单元的程序了
        # 主页 url
        main_page_url = parse_dict['--url']
        main_process(main_page_url)
    elif(parse_dict['--txt'] != 'none'):
        txt_path = parse_dict['--txt']
        url_list = parse_info(txt_path)
        for url in url_list:
            main_process(url)
