#!/usr/bin/env python
import sys
import xmlToCsv
import csvToXml
import os

def main():
    path:str
    if len(sys.argv) < 2:
        path = input("Enter path: ")
    else:
        path = sys.argv[1]
    filename, file_extension = os.path.splitext(path)
    if(file_extension == ".xml"):
        xmlToCsv.convert_xml_to_csv(filename)
    elif file_extension == ".csv":
        csvToXml.convert_csv_to_xml(filename)
    else:
        print("file extension " + file_extension[1:] + " not supported")
        sys.exit()
    
if __name__ == "__main__":
    main()