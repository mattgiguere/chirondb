#chirondb

**A repository of code for working with the CHIRON Database**

[![MIT-Lic](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/mattgiguere/shellScripts/blob/master/LICENSE)

###File Descriptions
---------------------------------
- **addEnviron.py**: a python command line tool for reading in data from the CHIRON environmental logs (e.g. temperatures measurements, pressure measurements, setpoints) and adding that data to the `chirondb` MySQL database.
 - **arguments**:
   - *date*: the date of a logs to restore in yymmdd format.
 - **examples**:

    - From the command line:
    ```sh
    addEnviron.py 150314
    ```

    - From within Python:
    ```python
    import addEnviron as ae
    as.addEnviron(150314)
    ```


- **addVds.ipynb**: An IPython notebook describing the code in the `addVds.py` file.

- **addVds.py**: A python script to import IDL velocity data structures into the chirondb MySQL database.
 - **arguments**
   - *star*: The name of the star (typically the HD number) to be read and imported into the database.
   - *tag*: The "tag" of the file. Different tags indicate something different about the RV analysis. For example, a tag of "a" was appended to the vd filename to indicate that the way the point spread function (PSF) was handled changed for the Fourier Transform Spectrograph (FTS) scan of the iodine cell. A tag of "f" was added to the vd filename for analysis carried out prior to the FTS PSF modification.
   - *startnum*: The Doppler analysis creates a separate vd file for every observation. Specifying the optional *startnum* argument will only add a subset of the vd files to the database, starting from *startnum* and extending to through the remainder of the files in the directory.
 - **examples**
   - From the comman line:
    ```sh
    addVds.py 10700 a 0
    ```
   - From within Python:
   ```python
   import addVds as vd
   vd.addVds('10700', 'a', startnum=0)
   ```


- **chironDBObject.ipynb**: An IPython notebook that was used for the debugging on `chironObject.py`


- **chironObject.py**: A python script that contains a class with methods to add information about an observation to the chiron MySQL database. This can be called in several ways.
   - **examples**:

    - From the command line:
     ```python
     chironObject(rawName)
     ```
    where `rawName` is the name of the observation you want to add to the database.

    - From within Python:
    ```python
    import chironObject as co
    co.kapowObservation(rawName)
    ```


- **getChironFiles.py**: a python command line tool for reading in data from FITS file and adding it to the `chirondb` MySQL database.

 - **arguments**:
   - *rootdir*: the directory where the FITS files are stored
   - *minDate*: if driving for multiple dates *minDate* specifies the inclusive start date in yymmdd format.
   - *maxDate*: similar to *minDate*, *maxDate* specifies the inclusive end date when adding multiple nights worth of data to the database. *maxDate* should also be in yymmdd format.

 - **example**: An example of how to add entries into the CHIRON Database is:

    ```python
    python getChironFiles.py /raw/mir7/ 140101 140110
    ```
