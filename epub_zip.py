import os
import re
import shutil
import zipfile

from parse import parse_info
from util import match_between
from lxml import etree
from copy import deepcopy
from util import etree_string

def get_container(opf_path):
    head = '<?xml version="1.0" encoding="UTF-8" ?>'
    add_str = """<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{}" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""".format(opf_path)

    return head + '\n' + add_str

def get_mimetype():
    return 'application/epub+zip'

def get_css(template_css_path='material/template.css'):
    with open(template_css_path) as f:
        return f.read()

def create_navnode(navNode_, id, playorder, html, label, namespace):
    navNode = deepcopy(navNode_)
    attr = navNode.attrib
    attr['id'] = id
    attr['playOrder'] = playorder
    text = navNode.xpath('//x:text', namespaces={'x':namespace})[0]
    text.text = label
    content_html = navNode.xpath('//x:content', namespaces={'x':namespace})[0]
    attr = content_html.attrib
    attr['src'] = html

    return navNode

def create_item(item_, id, href):
    item = deepcopy(item_)
    attr = item.attrib
    attr['id'] = id
    attr['href'] = href

    return item

def create_itemref(itemref_, idref):
    itemref = deepcopy(itemref_)
    attr = itemref.attrib
    attr['idref'] = idref

    return itemref

def get_ncx(title, author, info_dict, template_ncx_path='material/template.ncx'):
    namespace = 'http://www.daisy.org/z3986/2005/ncx/'
    ncx_f = etree.parse(template_ncx_path)
    root = ncx_f.getroot()
    root_children = root.getchildren()
    docTitle = root_children[1].getchildren()[0]
    docTitle.text = title
    docAuthor = root_children[2].getchildren()[0]
    docAuthor.text = author
    navMap = root_children[3]
    navNode_c = navMap.xpath('//x:navPoint[@id="coverpage"]', namespaces={'x': namespace})[0]
    index = 0
    for key in info_dict.keys():
        index += 1
        navMap.append(create_navnode(navNode_c, 'chapter' + str(key), str(index), \
                      'chapter{}.html'.format(key), info_dict[key], namespace))
    
    head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC
     "-//NISO//DTD ncx 2005-1//EN"
     "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n"""
    
    return head + etree_string(root)

def get_opf(info_dict, build_path, template_ncx_path='material/template.opf'):
    namespace = 'http://www.idpf.org/2007/opf'
    ncx_f = etree.parse(template_ncx_path)
    root = ncx_f.getroot()
    root_children = root.getchildren()
    manifest = root_children[1]
    spine = root_children[2]
    item_cov = manifest.xpath('x:item[@id="coverpage"]', namespaces={'x': namespace})[0]
    itemref_cov = spine.xpath('x:itemref[@idref="coverpage"]', namespaces={'x': namespace})[0]
    for key in info_dict.keys():
        manifest.append(create_item(item_cov, 'chapter' + str(key), 'chapter{}.html'.format(key)))
        spine.append(create_itemref(itemref_cov, 'chapter' + str(key)))
    pic_cov = manifest.xpath('x:item[@id="cover-image"]', namespaces={'x': namespace})[0]
    pics = [x for x in os.listdir(os.path.join(build_path, 'OPS', 'images')) if(x != 'cover.jpg')]
    for pic in pics:
        manifest.append(create_item(pic_cov, str(pic), 'images/{}'.format(pic)))
    head = """<?xml version="1.0" encoding="UTF-8" ?>\n"""
    return head + etree_string(root)

def get_chapter(txt_path, template_html_path='material/template.html'):
    namespace = "http://www.w3.org/1999/xhtml"
    html_f = etree.parse(template_html_path)
    root = html_f.getroot()
    root_children = root.getchildren()
    head_title = root_children[0].xpath('//x:title', namespaces={'x': namespace})[0]
    head_title.text = os.path.splitext(os.path.split(txt_path)[1])[0].split('_')[1]
    div = root_children[1].xpath('//x:div', namespaces={'x': namespace})[0]
    title = div.xpath('//x:h3//x:b', namespaces={'x': namespace})[0]
    title.text = os.path.splitext(os.path.split(txt_path)[1])[0].split('_')[1]

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if(line == '\n' or line == '    \n'): continue
            p = etree.Element('p')
            p.text = line
            div.append(p)
    
    return etree_string(root)

def get_illustration(illustration_path, template_html_path='material/template.html'):
    namespace = "http://www.w3.org/1999/xhtml"
    html_f = etree.parse(template_html_path)
    root = html_f.getroot()
    root_children = root.getchildren()
    div = root_children[1].xpath('//x:div', namespaces={'x': namespace})[0]
    title = div.xpath('//x:h3//x:b', namespaces={'x': namespace})[0]
    title.text = '插图'  
    pic_list = os.listdir(illustration_path)
    pic_list = sorted(pic_list, key=lambda x: int(os.path.splitext(x)[0]))
    for pic in pic_list:
        p = etree.Element('p')
        p.set('style', "text-indent:0em")
        img = etree.Element('img')
        img.set('src', "images/{}".format(pic))
        p.append(img)
        div.append(p)

    return etree_string(root)

def construct_epub(book_name, author, build_path, raw_root_path):
    info_dict = parse_info(raw_root_path + '\info.txt')
    if(not os.path.exists('{}/META-INF'.format(build_path))):
        os.makedirs('{}/META-INF'.format(build_path), 0x777)
    if(not os.path.exists('{}/OPS'.format(build_path))):
        os.makedirs('{}/OPS'.format(build_path), 0x777)
    if(not os.path.exists('{}/OPS/css'.format(build_path))):
        os.makedirs('{}/OPS/css'.format(build_path), 0x777)
    shutil.copy('material/template.css', '{}/OPS/css/main.css'.format(build_path))
    shutil.copy('material/mimetype', '{}/mimetype'.format(build_path))
    shutil.copy('material/container.xml', '{}/META-INF/container.xml'.format(build_path))
    shutil.copy('material/coverpage.html', '{}/OPS/coverpage.html'.format(build_path))
    if(os.path.exists(raw_root_path + '/illustration') and not os.path.exists('{}/OPS/images'.format(build_path))):
        shutil.copytree(raw_root_path + '/illustration', '{}/OPS/images'.format(build_path))
        shutil.copy('{}/OPS/images/1.jpg'.format(build_path), '{}/OPS/images/cover.jpg'.format(build_path))
        
    with open('{}/OPS/sen.ncx'.format(build_path), 'w', encoding='utf-8') as f:
        ncx = get_ncx(book_name, author, info_dict)
        f.write(ncx)
    with open('{}/OPS/sen.opf'.format(build_path), 'w', encoding='utf-8') as f:
        opf = get_opf(info_dict, build_path)
        f.write(opf)

    flag = 0
    for index,item in info_dict.items():
        with open('{}/OPS/chapter{}.html'.format(build_path, index), 'w', encoding='utf-8') as f:
            if('插图' in item):
                path = os.path.join(raw_root_path, 'illustration')
                f.write(get_illustration(path))
                flag = 1
            else:
                # 没有插图的特殊的短篇还不知道怎么处理，暂时先放置吧。
                if(flag): index = index - 1
                path = os.path.join(raw_root_path, '{}_{}.txt'.format(index, item))
                f.write(get_chapter(path))

target_list = ['一', '二', '三', '四', '五', '六']
for target in target_list:
    target = '第{}卷'.format(target)
    raw_root_path = r'F:\大学\项目\轻文解析器\build\被学生胁迫这事儿是犯罪吗？\{}'.format(target)
    build_path = 'try'
    if(os.path.exists(build_path)):
        shutil.rmtree(build_path)
    construct_epub('被学生胁迫这事儿是犯罪吗？', '相乐总', build_path, raw_root_path)
    file_walk = os.walk(build_path)
    f = zipfile.ZipFile('{}/{}.epub'.format(build_path, target), 'w', zipfile.ZIP_DEFLATED)
    for root,sub,file in file_walk:
        root_re = root.replace(build_path, '.')
        for sin in file:
            f.write(os.path.join(root, sin), os.path.join(root_re, sin))
    f.close()
    shutil.move('{}/{}.epub'.format(build_path, target), '{}.epub'.format(target))
    shutil.rmtree(build_path)