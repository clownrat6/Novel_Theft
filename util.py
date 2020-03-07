

def dict_save(dict, save_filepath):
    with open(save_filepath, 'w') as f:
        f.write(str(dict))

def dict_load(save_filepath):
    with open(save_filepath, 'r') as f:
        return eval(f.read())

def pic_write(content, save_filepath):
    with open(save_filepath, 'wb') as f:
        f.write(content)