from collections import defaultdict
from io import TextIOWrapper
import xml.etree.ElementTree as xml_parser

table_tag = "CUser"
field_tag = "Fields"
instances_tag = "Instances"
new_table_identifier = "@@NewTable@@"

def string_to_list(line:str,seperator:str=";"):
    line = line.strip("\n")
    line = line.strip("\r")
    index_line = 0
    length = len(line)
    list = []
    list.append(None)
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

def loop_over_lines(input:TextIOWrapper, catalog:xml_parser.Element):
    lines = input.readlines()
    line_index = 0
    
    current_table:xml_parser.Element
    ids = []
    types = []
    counts = []
    while line_index < len(lines):
        values = string_to_list(lines[line_index])
        if values[0] == None:
            line_index += 1
            continue
        if(values[0] == new_table_identifier):
            current_table = xml_parser.Element(table_tag)
            current_table.set("id", values[1])
            catalog.append(current_table)
            
            # read fields data
            line_index += 1
            ids = string_to_list(lines[line_index])
            line_index += 1
            types = string_to_list(lines[line_index])
            line_index += 1
            counts = string_to_list(lines[line_index])
            line_index += 1
            columns = string_to_list(lines[line_index])
            line_index += 1
            flags = string_to_list(lines[line_index])
            index = 1
            while index < len(ids):
                new_field = xml_parser.Element(field_tag)
                current_table.append(new_field)
                new_field.set("Id", ids[index])
                new_field.set("Type", types[index])
                if(counts[index] != None):
                    new_field.set("Count", counts[index])
                if(columns[index] != None):
                    new_field.set("EditorColumn", columns[index])
                if(flags[index] != None):
                    flag_list = (flags[index]).split(",")
                    if flag_list:
                        for flag in flag_list:
                            indiv_flag = flag.split(":")
                            new_flag = xml_parser.Element("Flags")
                            new_field.append(new_flag)
                            new_flag.set("index", indiv_flag[0])
                            new_flag.set("value", indiv_flag[1])
                index += 1
        else:
            #create new instance and fill it
            new_instance = xml_parser.Element(instances_tag)
            new_instance.set("Id", values[0])
            current_table.append(new_instance)
            index = 1
            
            while index < len(ids):
                if(values[index] == None):
                    index += 1
                    continue
                type = types[index]
                
                if(counts[index] != None and counts[index] != "1"):
                    count = int(counts[index])
                    value_list = string_to_list(values[index],",")
                    i = 0
                    while i < count:
                        if(type == "String" or type == "Color"):
                            value_list[i]= value_list[i].replace("\"","")
                        if(value_list[i] == None):
                            i +=1
                            continue
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
                    if(type == "String" or type == "Color"):
                        values[index]=values[index].replace("\"","")
                    new_value = xml_parser.Element(type)
                    new_value.set(type, values[index])
                    new_instance.append(new_value)
                    new_context = xml_parser.Element("Field")
                    new_context.set("Id", ids[index])
                    new_value.append(new_context)
                
                index += 1
        line_index += 1


def convert_csv_to_xml(input_filename:str,output_filename:str):
    with open(input_filename + ".csv", "r", newline="") as input:
        catalog = xml_parser.Element("Catalog")
        root = xml_parser.ElementTree(catalog)
        
        loop_over_lines(input, catalog)
        # print("")
        xml_parser.indent(root, space="    ",)
        root.write(output_filename+".xml", encoding="utf-8" ,xml_declaration=True)