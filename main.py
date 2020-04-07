import os
import time
import threading
import _thread

from epub import epub_zip
from parse import one_stage_parse,two_stage_parse
from thread import download_txt,download_illustration

# 现在是以单本书为单元的程序了
# 主页 url
main_page_url = 'https://www.wenku8.net/book/2488.htm'

# 获取小说文字，插图，名字，作者
novel_name,author_name,novel_content_url = one_stage_parse(main_page_url)
content_dict = two_stage_parse(novel_content_url)

# 下载小说文字，与插图
download_txt(content_dict, 'build')
download_illustration(content_dict, 'build')
# 打包成 eupb
epub_zip(novel_name, author_name, 'test', 'build')
