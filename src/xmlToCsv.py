from collections import defaultdict
from io import TextIOWrapper
import xml.etree.ElementTree as xml_parser
import csv

table_tag = "CUser"
field_tag = "Fields"
instances_tag = "Instances"
field_subtags = ["Id", "Type", "Count", "EditorColumn", "Flags"]
new_table_identifier = "@@NewTable@@"

# parses fields into a dictionary of lists which can be indexed by the tags e.g. "Id"
def parse_fields(fields: list[xml_parser.Element]):
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

# collapses dict into list
def turn_indexdict_to_value(index_dict:dict):
    value = ""
    for index in index_dict:
        value += index_dict[index]
        if( index != list(index_dict.keys())[-1]):
            value += ","
    return value

# an instance in xml is turned into one row in csv.
# the dict content_rows is appended at index instance id with a list of entries in the order of the fields
def parse_instance(instance:xml_parser.Element, fields_dict:dict, types:set, content_rows:dict):
    instance_id = instance.attrib["Id"]
    # initialize dictionaries
    id_to_index_dict = {}
    id_list = fields_dict["Id"]
    
    # use index here because access to count field is required
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
    
    # fill dictionaries
    for type in types:
        fields_of_type = instance.findall(type)
        for field in fields_of_type:
            value = field.attrib[type]
            context = field.find("Field")
            id = context.attrib["Id"]
            if("Index" in context.attrib):
                index = context.attrib["Index"]
            else:
                index = "0"
            (id_to_index_dict[id])[index] = value

    # collapse dictionaries into a list in the correct order
    new_row = []
    for id in id_list:
        new_row.append(turn_indexdict_to_value(id_to_index_dict[id]))
    
    content_rows[instance_id] = new_row

# table consist of fields and instances. parse fields first
def parse_table(table:xml_parser.Element):
    fields = table.findall(field_tag)
    fields_dict = parse_fields(fields)
    types = set()
    for type in fields_dict["Type"]:
        types.add(type)
    instances = table.findall(instances_tag)
    content_rows = {}
    for instance in instances:
        parse_instance(instance, fields_dict, types, content_rows)
    return fields_dict, content_rows

# inserts id into the first entry of the list
def parse_row(id:str, values:list):
    values.insert(0, id)
    return values

# csv writer function after all the data has been parsed
def write_table_dict_to_csv(output:TextIOWrapper, header_rows:dict, content_rows:dict, title:str):
    csvwriter = csv.writer(output)
    csvwriter.writerow([new_table_identifier, title])
    for row in header_rows:
        csvwriter.writerow(parse_row(row, header_rows[row]))
    for row in content_rows:
        csvwriter.writerow(parse_row(row, content_rows[row]))
    output.write("\n")

def loop_over_tables_in_root(root:xml_parser.ElementTree, output:TextIOWrapper):
    userData_tables = root.findall(table_tag)
    for table in userData_tables:
        header_rows, content_rows = parse_table(table)
        write_table_dict_to_csv(output, header_rows, content_rows, table.attrib["id"])

def convert_xml_to_csv(input_filename:str, output_filename:str):
    root = xml_parser.parse(input_filename + ".xml")
    with open(output_filename + ".csv", "w", newline="") as output:
        loop_over_tables_in_root(root, output)