#chirondb

**A repository of code for working with the CHIRON Database**

[![MIT-Lic](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/mattgiguere/shellScripts/blob/master/LICENSE)

###Descriptions
---------------------------------
- **getChironFiles.py**: a python command line tool for reading in data from FITS file and adding it to the `chirondb` MySQL database.

 - **arguments**:
   - *rootdir*: the directory where the FITS files are stored
   - *minDate*: if driving for multiple dates *minDate* specifies the inclusive start date in yymmdd format.
   - *maxDate*: similar to *minDate*, *maxDate* specifies the inclusive end date when adding multiple nights worth of data to the database. *maxDate* should also be in yymmdd format.

 - **example**: An example of how to add entries into the CHIRON Database is:

    ```python
    python getChironFiles.py /raw/mir7/ 140101 140110
    ```
