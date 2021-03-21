import bpy
import os
from os import path, walk

def base_name(path):
    return bpy.path.basename(path)

def split_name(path):
    filename, file_extension = os.path.splitext(path)
    return filename, file_extension

def filename(path):
    b = base_name(path)
    filename, file_extension = os.path.splitext(b)
    return filename

def fileext(path):
    b = base_name(path)
    filename, file_extension = os.path.splitext(b)
    return file_extension

def abspath(relpath):    
    return bpy.path.abspath(relpath)

def read_file_lines(path):
    with open(path) as f:
        lines = f.readlines()
    return lines

def get_files_in_dir(dir, prefix='', contains='', endswith='', case_sensitive=True):     
    #print('Searching for files in [{0}] with prefix [{1}]'.format(dir, prefix))
       
    files = []
    for (dirpath, dirnames, filenames) in walk(dir):
        for filename in filenames:            
            if prefix == '' or ((case_sensitive and filename.startswith(prefix)) or (not case_sensitive and filename.lower().startswith(prefix.lower()))):
                if contains == '' or ((case_sensitive and contains in filename) or (not case_sensitive and contains.lower() in filename.lower())):
                    if endswith == '' or ((case_sensitive and filename.endswith(endswith)) or (not case_sensitive and filename.lower().endswith(endswith.lower()))):

                        fullname = '{0}\{1}'.format(dirpath, filename)
                        fullname = fullname.replace('\\\\', '\\')
                        #print(fullname)
                        files.append(fullname)

    return files

def parse_csv(filepath, has_headers=True):
    headers = None
    rows = []
    lines = read_file_lines(filepath)

    for line in lines:
        line = line.strip('\n').strip('\r').strip('\t').strip(' ')
        if has_headers and not headers:
            headers = line.split(',')            
            continue
        
        lineset = {}
        splits = line.split(',')
        for index in range(len(splits)):
            header = index if not has_headers else headers[index]
            prop = splits[index]
            lineset[header] = prop
    
        rows.append(lineset)
    
    return headers, rows

def parse_csvs(filepaths, has_headers=True):
    headers = None
    rows = []
    for filepath in filepaths:
        h, r = parse_csv(filepath, has_headers)

        if not headers:
            headers = h
        rows.extend(r)
    
    return headers, rows