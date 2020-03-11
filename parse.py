import os
import re
import shutil
import pythoncom
import requests as req

from lxml import etree
from util import pic_write,num_to_word,match_between,word_to_num
from win32com.client import Dispatch

def target_parse(target_path):

    f = open(target_path, 'r', encoding='utf-8')
    lines = f.readlines()

    target_dict = {}
    for line in lines:
        target_name, target_url = tuple(line.split(':', 1))
        target_dict[target_name] = target_url
    
    return target_dict

def txt_page_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')[0]

    one_page = ""

    for i in main.getchildren():
        if(i.tail == None): continue
        preprocess = '    ' + i.tail.replace('\n', '').replace(chr(0xa0), '')
        one_page += preprocess + '\n'

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

    ret_str = [x+'\n' for x in image_url_list]
    ret_str = ''.join(ret_str)
    
    return ret_str

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

def chapter_parse(main_dict, chapter_num, base_path):

    # 单卷内的解析
    chapter_dict = main_dict[chapter_num]
    chapter_folder = os.path.join(base_path, chapter_num)
    
    if(not os.path.exists(chapter_folder)):
        os.makedirs(chapter_folder, 0x777)

    keys = chapter_dict.keys()
    index = 0
    for key in keys:
        index += 1
        gene_path = '{}/{}_{}.txt'.format(chapter_folder, index, key)
        print(gene_path)
        if(os.path.exists(gene_path)): continue
        f = open(gene_path, 'w', encoding='utf-8')
        if(key == "插图"): 
            f.write(illustration_page_parse(chapter_dict[key])) 
            f.close()
            continue
        f.write(txt_page_parse(chapter_dict[key]))
        f.close()

def pic_parse(url, filename):
    # 图像解析新方案，requests 的请求方式可能太粗糙了，不太行，所以换用迅雷的调用。
    # req_obj = req.get(url)

    # raw_content = req_obj.content
    # 这种方法毕竟还是存在缺点，实在不太好，需要手动操作一下。
    pythoncom.CoInitialize()
    # return raw_content
    thunder = Dispatch('ThunderAgent.Agent64.1')
    thunder.AddTask(url, filename)
    thunder.CommitTasks()
    pythoncom.CoUninitialize()

def cover_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    src = html.xpath('//div[@id="content"]//table//img//@src')[0]

    return src

def verify_completeness(target_txt_path):
    """
    to check if all of the illustration has been downloaded.
    """
    target_dict = target_parse(target_txt_path)

    for key in target_dict.keys():
        target_root = os.path.join('build', key)
        volume_list = os.listdir(target_root)
        for volume in volume_list:
            volume_path = os.path.join(target_root, volume)
            if(not os.path.isdir(volume_path)): continue
            chapter_list = os.listdir(volume_path)
            chapter_list = ['{}/\\'.format(x) for x in chapter_list]
            chapter_string = ''.join(chapter_list)
            if('插图' not in chapter_string): continue
            illus_name = re.search('[0-9]*_插图.*?\.txt', chapter_string)
            illus_name = illus_name.group(0)
            num = len(open(volume_path + '/' + illus_name, 'r').readlines())
            for i in range(1, num+1):
                pic_path = os.path.join(volume_path, 'illustration', '{}.jpg'.format(i))
                if(not os.path.exists(pic_path)): print("{} don't exits".format(pic_path))

def move_from_thunder(download_root):
    root_path = download_root
    file_list = os.listdir(root_path)
    for file in file_list:
        src_path = os.path.join(root_path, file)
        file = file.replace('_', '')
        file = file.replace('illustration', '_')
        name = re.search('[0-9]*.jpg', file)
        target = re.search('(?<=build).*(?=(第.*卷|番外))', file)
        if(target == None): continue
        target = target.group(0)
        # volume 才是卷的意思，😓
        file = file.replace('build{}'.format(target), '')
        volume = re.search('.*(?=_)', file)
        if(name == None or volume == None): continue
        name = name.group(0)
        volume = volume.group(0)
        dst_path = 'build/{}/{}/illustration/{}'.format(target, volume, name)
        shutil.move(src_path, dst_path)

def gene_info():
    root_path = 'build'
    target_list = os.listdir(root_path)
    for target in target_list:
        target_path = os.path.join(root_path, target)
        volume_list = os.listdir(target_path)
        None_list = []
        volume_dict = {}
        for volume in volume_list:
            index = match_between('第', '卷', volume)
            volume_path = os.path.join(target_path, volume)
            if(not os.path.isdir(volume_path)): continue
            if(index == None): 
                None_list.append(volume)
                continue
            volume_dict[volume] = word_to_num(index)
        sorted_volume_list = [x[0] for x in sorted(volume_dict.items(), key=lambda x:x[1])]
        sorted_volume_list += None_list
        for volume in sorted_volume_list:
            volume_path = os.path.join(target_path, volume)
            chapter_list = os.listdir(volume_path)
            temp = []
            for chapter in chapter_list:
                chapter_path = os.path.join(volume_path, chapter)
                if(not os.path.isfile(chapter_path)): continue
                if(chapter == 'info.txt'): continue
                temp.append(chapter)
            chapter_list = temp
            chapter_list = sorted(chapter_list, key=lambda x:int(x.split('_')[0]))
            # 还是把插图放在前面吧
            chapter_list = [chapter_list[-1]] + chapter_list[:-1]
            f = open('{}/info.txt'.format(volume_path), 'w', encoding='utf-8')
            index = 0
            for chapter in chapter_list:
                chapter_name = os.path.splitext(chapter)[0].split('_')[1]
                index += 1
                f.write('{}:{}\n'.format(index, chapter_name))
            f.close()

def parse_info(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        ret_dict = {}
        for line in lines:
            line = line.strip()
            index = int(line.split(':')[0])
            title = line.split(':')[1]
            ret_dict[index] = title

        return ret_dict