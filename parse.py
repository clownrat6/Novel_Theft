import requests as req
from lxml import etree

def page_parse(url):

    req_obj = req.get(url)
    req_obj.encoding = 'gbk'

    raw_content = req_obj.text # get_obj.text.encode(req_obj.encoding).decode('gbk')    

    html = etree.HTML(raw_content)
    main = html.xpath('//div[@id="content"]')

    one_page = ""

    for i in main[0].getchildren():
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

