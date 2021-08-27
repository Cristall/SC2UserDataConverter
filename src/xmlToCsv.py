from collections import defaultdict
from io import TextIOWrapper
import xml.etree.ElementTree as xml_parser

#Globals
table_tag = "CUser"
field_tag = "Fields"
instances_tag = "Instances"
field_subtags = ["Id", "Type", "Count", "EditorColumn", "Flags"]
new_table_identifier = "@@NewTable@@"

#turns the list of fields into a dictionary of lists which can be indexed by the tags e.g. "Id"
def turn_fields_into_dictionary(fields: list[xml_parser.Element]):
    fields_dic = defaultdict(list)
    for field in fields:
        for tag in field_subtags:
            if (tag not in field.attrib):
                subtag = field.findall(tag)
                if(subtag):
                    if(tag == "Flags"):
                        entry = ""
                        for flag_index in subtag:
                            entry += flag_index.attrib["index"] +":"+flag_index.attrib["value"] 
                            if flag_index != subtag[-1]:
                                entry += ","
                        fields_dic[tag].append(entry)
                    else:
                        fields_dic[tag].append(subtag[0].attrib["value"])
                else:
                    fields_dic[tag].append(None)
            else:
                fields_dic[tag].append(field.attrib[tag]) 
    return fields_dic

def turn_indexdict_to_value(index_dict:dict):
    value = ""
    for index in index_dict:
        value += index_dict[index]
        if( index != list(index_dict.keys())[-1]):
            value += ","
    return value

def parse_instance(instance:xml_parser.Element, fields_dict:dict, types:set, content_rows:dict):
    instance_id = instance.attrib["Id"]
    id_to_index_dict = {}
    #initialize dictionaries
    id_list = fields_dict["Id"]
    id = 0
    while (id < len(id_list)):
        something = {}
        counts = fields_dict["Count"]
        count_str = counts[id]
        count = 1
        if count_str != None:
            count = int(count_str)
        
        index = 0
        while (index < count):
            something[str(index)] = ""
            index += 1
        id_to_index_dict[id_list[id]] = something   
        id += 1
    
    #fill dictionaries
    for type in types:
        fields_of_type = instance.findall(type)
        for field in fields_of_type:
            value = field.attrib[type]
            if(type == "String" or type == "Color"):
                value = "\""+value +"\""
            context = field.find("Field")
            id = context.attrib["Id"]
            if("Index" in context.attrib):
                index = context.attrib["Index"]
            else:
                index = "0"
            (id_to_index_dict[id])[index] = value

    #collapse dictionaries into a list
    new_row = []
    for id in id_list:
        new_row.append(turn_indexdict_to_value(id_to_index_dict[id]))
    
    content_rows[instance_id] = new_row

def parse_fields_in_table(table:xml_parser.Element):
    fields = table.findall(field_tag)
    fields_dict = turn_fields_into_dictionary(fields)
    types = set()
    for type in fields_dict["Type"]:
        types.add(type)
    instances = table.findall(instances_tag)
    content_rows = {}
    for instance in instances:
        parse_instance(instance, fields_dict, types, content_rows)
    return fields_dict, content_rows
    
def write_row(writer:TextIOWrapper, id:str, values:list):
    writer.write(id+";")
    i:int = 0
    while(i < len(values)):
        string = values[i]
        i += 1
        if(string):
            writer.write(string)
        if(i != len(values)):
            writer.write(";")
    writer.write("\n")
    
def write_table_dict_to_csv(output:TextIOWrapper, header_rows:dict, content_rows:dict, title:str):
    output.write(new_table_identifier + ";" + title +"\n")
    for row in header_rows:
        write_row(output, row, header_rows[row])
    for row in content_rows:
        write_row(output, row, content_rows[row])
    output.write("\n")

def loop_over_tables_in_root(root:xml_parser.ElementTree, output:TextIOWrapper):
    userData_tables = root.findall(table_tag)
    for table in userData_tables:
        header_rows, content_rows = parse_fields_in_table(table)
        # print(header_rows)
        # print(content_rows)
        write_table_dict_to_csv(output, header_rows, content_rows, table.attrib["id"])

def convert_xml_to_csv(filename:str):
    root = xml_parser.parse(filename + ".xml")
    with open(filename + ".csv", "w", newline="") as output:
        loop_over_tables_in_root(root, output)