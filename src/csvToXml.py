from collections import defaultdict
from io import TextIOWrapper
import xml.etree.ElementTree as xml_parser
import csv

# const strings
table_tag = "CUser"
field_tag = "Fields"
instances_tag = "Instances"
new_table_identifier = "@@NewTable@@"

# helper function to split flags and array type entries
def string_to_list(line:str,seperator:str=";"):
    line = line.strip("\n")
    line = line.strip("\r")
    index_line = 0
    length = len(line)
    list = [None]
    index_list = 0
    inside_string = False
    while(index_line < length):
        char = line[index_line]
        if(char == "\""):
            inside_string = not inside_string
        if(char == seperator and inside_string == False):
            list.append(None)
            index_list += 1
        else:
            if(list[index_list] == None):
                list[index_list] = char
            else:
                list[index_list] += char
        index_line += 1
    if(inside_string == True):
        raise Exception("Quotation marks not matching in line:\n" + line)
    return list

# main function to interpret csv lines and convert it into xml tree
def loop_over_lines(input:TextIOWrapper, catalog:xml_parser.Element):
    csvreader = csv.reader(input)
    current_table:xml_parser.Element
    ids = []
    types = []
    counts = []
    for values in csvreader:
        if len(values) == 0:
            #empty line
            continue
        
        if(values[0] == new_table_identifier):
            # create a new UserData object (table), first 5 lines contain the field data
            current_table = xml_parser.Element(table_tag)
            current_table.set("id", values[1])
            catalog.append(current_table)
            
            ids = csvreader.__next__()
            types = csvreader.__next__()
            counts = csvreader.__next__()
            columns = csvreader.__next__()
            flags = csvreader.__next__()
            
            # iterate over all list simultaneously
            index = 1
            while index < len(ids):
                new_field = xml_parser.Element(field_tag)
                current_table.append(new_field)
                new_field.set("Id", ids[index])
                new_field.set("Type", types[index])
                if(counts[index] != ""):
                    new_field.set("Count", counts[index])
                if(columns[index] != ""):
                    new_field.set("EditorColumn", columns[index])
                if(flags[index] != ""):
                    flag_list = (flags[index]).split(";")
                    if flag_list:
                        for flag in flag_list:
                            indiv_flag = flag.split(":")
                            new_flag = xml_parser.Element("Flags")
                            new_field.append(new_flag)
                            new_flag.set("index", indiv_flag[0])
                            new_flag.set("value", indiv_flag[1])
                index += 1
        else:
            # create a new instance (row) for the current UserData
            new_instance = xml_parser.Element(instances_tag)
            new_instance.set("Id", values[0])
            current_table.append(new_instance)
            index = 1
            
            while index < len(ids):
                if(values[index] == ""):
                    #entry is empty
                    index += 1
                    continue
                type = types[index]
                
                if(counts[index] != "" and counts[index] != "1"):
                    # array type field
                    count = int(counts[index])
                    value_list = string_to_list(values[index],";")
                    i = 0
                    while i < count:
                        if(value_list[i] == None):
                            i +=1
                            continue
                        # if(type == "String" or type == "Color"):
                        #     value_list[i]= value_list[i].replace("\"","")
                        new_value = xml_parser.Element(type)
                        new_value.set(type, value_list[i])
                        new_instance.append(new_value)
                        
                        new_context = xml_parser.Element("Field")
                        new_context.set("Id", ids[index])
                        if(i != 0):
                            new_context.set("Index", str(i))
                        new_value.append(new_context)
                        i += 1
                else:
                    # singular entry
                    new_value = xml_parser.Element(type)
                    new_value.set(type, values[index])
                    new_instance.append(new_value)
                    new_context = xml_parser.Element("Field")
                    new_context.set("Id", ids[index])
                    new_value.append(new_context)
                
                index += 1

# wrapper function for extended utility
def convert_csv_to_xml(input_filename:str,output_filename:str):
    with open(input_filename + ".csv", "r", newline="") as input:
        catalog = xml_parser.Element("Catalog")
        root = xml_parser.ElementTree(catalog)
        loop_over_lines(input, catalog)
        xml_parser.indent(root, space="    ")
        root.write(output_filename+".xml", encoding="utf-8" ,xml_declaration=True)
    file_string:str
    
    # the xml library uses ' instead of " and adds whitespaces at the end of tags if they are closed
    # this is to keep it close to sc2 editor formatting
    with open(output_filename+".xml", "r", newline="",encoding='utf8') as file:
        file_string = file.read()
        file_string = file_string.replace(" />", "/>")
        file_string = file_string.replace("\'", "\"")
    with open(output_filename+".xml", "w", newline="",encoding="utf8") as file:
        file.write(file_string+"\r\n")