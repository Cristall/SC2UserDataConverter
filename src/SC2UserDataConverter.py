#!/usr/bin/env python
import sys
import xmlToCsv
import csvToXml
import os

def main():
    input_path:str
    output_path:str
    if len(sys.argv) < 2:
        input_path = input("Enter path: ")
    elif (len(sys.argv) == 2):
        input_path = sys.argv[1]
        output_path = input_path
    elif (len(sys.argv) == 3):
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        raise Exception("Too many Arguments. Excepts 1 or 2.")

    input_filename, input_file_extension = os.path.splitext(input_path)
    output_filename, output_file_extension = os.path.splitext(output_path)
    
    if(input_file_extension == ".xml"):
        xmlToCsv.convert_xml_to_csv(input_filename, output_filename)
    elif input_file_extension == ".csv":
        csvToXml.convert_csv_to_xml(input_filename, output_filename)
    else:
        print("file extension " + input_file_extension[1:] + " not supported")
        sys.exit()
    
if __name__ == "__main__":
    main()
