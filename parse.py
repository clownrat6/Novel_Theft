import os
import re
import shutil
import pythoncom
import requests as req

from lxml import etree
from util import pic_write,num_to_word,match_between,word_to_num
from win32com.client import Dispatch

def one_stage_parse(url):
    """
    小说主页解析，获取内容为：
        1. 小说名字
        2. 作者姓名
        3. 小说目录的 url
    """
    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')[0]

    content = main.getchildren()[0].getchildren()

    # 小说名字
    novel_name = content[0].xpath('.//b')[0].text
    # 作者姓名
    author_name = content[0].xpath('.//td[@width="20%"]')[1].text
    author_name = author_name.split('：')[1]
    # 小说目录的 url
    novel_content_url = content[5].xpath('.//a//@href')[0]

    return novel_name,author_name,novel_content_url

def two_stage_parse(url):
    """
    小说目录以及内容解析，解析得到一个装有文字内容和图片内容的字典。
    {"第一卷":{"序章":..., "第一章":..., "插图":...},...}
    """
    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text

    html = etree.HTML(raw_content)
    content_table = html.xpath('//table')[0]

    volume_list = content_table.xpath('.//tr')

    ret_dict = {}
    volume_head = None
    for tr in volume_list:
        head = tr.xpath('.//td[@class="vcss"]')
        if(len(head) != 0):
            volume_head = head[0].text
            ret_dict[volume_head] = {}
        else:
            chapter_list = tr.xpath('.//td[@class="ccss"]')
            for td in chapter_list:
                a_list = td.xpath('.//a')
                if(len(a_list) == 0): continue
                a = a_list[0]
                chapter_head = a.text
                txt_page_url = url.replace('index.htm', a.xpath('.//@href')[0])
                ret_dict[volume_head][chapter_head] = txt_page_url

    volume_name_list = list(ret_dict.keys())
    for volume in volume_name_list:
        if('插图' not in list(ret_dict[volume].keys())):
            ret_dict.pop(volume)

    return ret_dict

def txt_page_parse(url, save_path=None):

    req_obj = req.get(url.strip())
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')[0]

    one_page = ""

    for i in main.getchildren():
        if(i.tail == None): continue
        preprocess = '    ' + i.tail.replace('\n', '').replace(chr(0xa0), '')
        one_page += preprocess

    if(save_path != None):
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(one_page)

    return one_page

def illustration_page_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')[0]

    image_list = main.xpath('//div[@class="divimage"]')

    image_url_list = []
    index = 0
    for image in image_list:
        index += 1
        url = image.getchildren()[0].xpath('@href')[0]
        image_url_list.append(url)

    return image_url_list

def pic_parse(url, save_path=None):
    # timeout 元组第一个参数为连接超时时间，第二个参数为读取超时时间
    i = 0
    while(i < 3):
        try:
            req_obj = req.get(url, timeout=(3, 10))
            break
        except req.exceptions.RequestException:
            i += 1
    
    if(i == 3): 
        print('{} 已经尝试超过三次均失败。'.format(save_path))
        assert False, 'Fxxk up'

    raw_content = req_obj.content

    if(save_path != None):
        pic_write(raw_content, save_path)

    return raw_content
