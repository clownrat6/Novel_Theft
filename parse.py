import os
import requests as req

from lxml import etree

def target_parse(target_path):

    f = open(target_path, 'r', encoding='utf-8')
    lines = f.readlines()

    target_dict = {}
    for line in lines:
        target_name, target_url = tuple(line.split(':', 1))
        target_dict[target_name] = target_url
    
    return target_dict

def page_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')[0]

    one_page = ""

    for i in main.getchildren():
        if(len(i.tail) == 2): continue
        preprocess = '    ' + i.tail.replace('\n', '').replace(chr(0xa0), '')
        one_page += preprocess + '\n' + '\n'

    return one_page

def main_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//table[@class="css"]')
    content = main[0].getchildren()

    result = {}

    chapter_head = None
    for i in content:
        cols = i.getchildren()
        if(len(cols) == 1):
            chapter_head = cols[0].text
            result[chapter_head] = {}
            continue

        if(chapter_head != None):
            for col in cols:
                a_tag = col.getchildren()
                if(len(a_tag) == 0): continue
                a_tag = a_tag[0]
                url_local = a_tag.xpath('@href')[0]
                col_name = a_tag.text
                result[chapter_head][col_name] = url.replace('index.htm', url_local)

    return result

def illustration_parse(url):

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

    ret_str = [x+'\n' for x in image_url_list]
    ret_str = ''.join(ret_str)
    
    return ret_str

def chapter_parse(main_dict, chapter_num, base_path):

    # 单卷内的解析
    chapter_dict = main_dict[chapter_num]
    chapter_folder = os.path.join(base_path, chapter_num)
    
    if(not os.path.exists(chapter_folder)):
        os.makedirs(chapter_folder, 0x777)
    
    keys = chapter_dict.keys()
    for key in keys:
        f = open('{}/{}.txt'.format(chapter_folder, key), 'w', encoding='utf-8')
        if(key == "插图"): 
            f.write(illustration_parse(chapter_dict[key])) 
            f.close()
            continue
        f.write(page_parse(chapter_dict[key]))
        f.close()