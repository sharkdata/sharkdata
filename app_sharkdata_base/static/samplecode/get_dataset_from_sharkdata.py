#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# import json
# import urllib2
# import codecs
# 
# def execute():
#     """ 
#     Example code to get datasets from SHARKdata. Developed in Python 2.7. 
#     For Windows users we recommend Python(x,y) to install Python: http://code.google.com/p/pythonxy/
#     
#     This Python script can be executed directly in a terminal window:
#     $ python get_dataset_from_sharkdata.py
#     
#     The following output is expected:
#     1. A list of all avaliable datasets. Printed in the terminal window.
#     2. The content of the first available dataset. Printed in the terminal window.
#     3. The content of the first available datasets saved as a file in the same directory as the Python script. 
#        Character encoding in the file will be UTF-8. Change the row "character_encoding = 'utf8'" for other
#        encodings.
#        
#     For more options, read the documentation at http://test.sharkdata.se/documentation/
#     """
#     
#     # URL to the datasets part of SHARKdata.
#     sharkdata_url = 'http://sharkdata.se/datasets/'
# 
#     # Download a list of all available datasets. The JSON format is used.
#     datasets = json.load(urllib2.urlopen(sharkdata_url + 'list.json'))
#     
#     # Exit if no datasets are found. 
#     if len(datasets) < 1:
#         print('No datasets found. Script terminated.')
#         return
# 
#     # Print some info for all available datasets.
#     print('\nAvailable datasets on SHARKdata:' + '\n')
#     for dataset in datasets:
#         print(' Datatype: ' + dataset['datatype'] + ' Name: ' + dataset['dataset_name'])
#     
#     # Get the name of the first dataset in the list.
#     dataset_name = datasets[0]['dataset_name']
#     
#     # Download header and data and print the content. The text format is used.
#     print('\nPrint dataset content for: ' + dataset_name + '\n')
#     header_and_data = urllib2.urlopen(sharkdata_url + dataset_name + '/data.txt')
#     
#     for row in header_and_data:
#         # The text format character encoding is cp1252 (equal to windows-1252).
#         row = row.decode('cp1252')
# #        print(row.strip())
# 
#     # Download header and data and save to file.
#     dataset_name = datasets[0]['dataset_name']
#     filename = datasets[0]['dataset_file_name'].replace('.zip', '.txt')
#     character_encoding = 'utf8' # Some alternatives: cp1252, utf-8, utf-16, ascii, latin1, macroman.
#     row_delimiter = '\r\n'
#     print('\nDataset content for: ' + dataset_name + ' to file: ' + filename + '\n')
#     out_file = None
#     try:
#         out_file = codecs.open(filename, mode = 'w', encoding = character_encoding)
#         header_and_data = urllib2.urlopen(sharkdata_url + dataset_name + '/data.txt')
#         for row in header_and_data:
#             row = row.decode('cp1252')
#             out_file.write(row.strip() + row_delimiter)
#     finally:
#         if out_file: out_file.close()
# 
# 
# if __name__ == "__main__":
#     execute()
