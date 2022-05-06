# SC2UserDataConverter

Small python script to speedup the editing of huge User Data tables (in my case: 40 columns x 280 rows)

Can convert from xml to csv and backwards.
The generated file will be named the same except the file extension and placed inside the same folder.

Terminal execution allows for 2 arguments, first input, second output path. Output path is optional and will default to input path if not present.
If no argument is given, promt will ask for a path to be entered manually.
