# SC2UserDataViewer

Small python script to speedup my editing of huge User Data tables (in my case: 40 colomn x 280 rows)

Can convert from xml to csv and backwards.
The generated file will be named the same except the file extension and placed inside the same folder.

When parsing an xml file it will add quotation marks to string and color-type entries to allow for arrays to work properly, but it will probably work without quotes for non-array fields.