import os

from parse import main_parse, page_parse, target_parse, illustration_parse, chapter_parse

# target_dict = target_parse('target.txt')

# target_keys = list(target_dict.keys())

# url = target_dict[target_keys[0]]

# main_dict = main_parse(url)


# pic_content = req.get(url).content
# with open(os.path.join(pic_base_path, '{}.jpg'.format(index)), 'wb') as f:
#     f.write(pic_content)

main_dict = eval(open('temp.txt', 'r', encoding='utf-8').read())

for key in main_dict.keys():
    chapter_parse(main_dict, key, 'build')
