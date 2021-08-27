#!/usr/bin/env python
import sys
import argparse
from pathlib import Path 
import xmlToCsv
import csvToXml
import os
import time


def main():
    # print(sys.argv)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="inputfile")
    args = parser.parse_args()
    
    if not args.i:
        sys.exit()
      
    filename, file_extension = os.path.splitext(args.i)
    start_time = time.time()
    if(file_extension == ".xml"):
        xmlToCsv.convert_xml_to_csv(filename)
    elif file_extension == ".csv":
        csvToXml.convert_csv_to_xml(filename)
    else:
        print("file extension " + file_extension[1:] + " not supported")
        sys.exit()
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    
if __name__ == "__main__":
    main()