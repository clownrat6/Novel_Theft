import re

from lxml import etree

def dict_save(dict, save_filepath):
    with open(save_filepath, 'w') as f:
        f.write(str(dict))

def dict_load(save_filepath):
    with open(save_filepath, 'r') as f:
        return eval(f.read())

def pic_write(content, save_filepath):
    with open(save_filepath, 'wb') as f:
        print(save_filepath)
        f.write(content)

def etree_string(root):
    ret = etree.tostring(root, encoding='utf-8').decode('utf-8')

    return ret

def match_between(a, b, string):
    left_bounding = re.search('{}.*'.format(a), string)
    if(left_bounding == None): return None
    left = left_bounding.group(0).replace('{}'.format(a), '')
    right_bounding = re.search('.*{}'.format(b), left)
    if(right_bounding == None): return None
    right = right_bounding.group(0).replace('{}'.format(b), '')
    
    return right

def num_to_word(num):
    word_sort = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if(num <= 0): return word_sort[nun]
    ret = ''
    while(num > 10):
        temp = num%10
        num = num/10
        ret += word_sort[temp]
    
    if(num != 0): ret += word_sort[num]

    return ret

def word_to_num(word):
    word_sort = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if(word in word_sort): return float(word_sort.index(word))
    if(word not in word_sort):
        try:
            return float(word)
        except:
            pass
            
    ret = 0.0

    if(len(word) == 2):
        ret += word_sort.index(word[0])*10 if(word[0] != '十') else 10
        ret += word_sort.index(word[1]) if(word[1] != '十') else 0
    
    return ret