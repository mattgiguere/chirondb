####Modifications

This document describes modifications made by hand
to the chirondb MySQL database since 2014.12.02.

2014.12.02:
To help keep track of the observation used to
determine the H-alpha EW a new column named
`hsrc_obsid` was added.

```sql
ALTER TABLE halpha ADD (hrsc_obsid INT);
```

and when things crashed and I finally got to the
root of the problem I fixed my typo:

```sql
ALTER TABLE halpha DROP (hrsc_obsid INT);
ALTER TABLE halpha ADD (hsrc_obsid INT);
```

There were some additional issues attempting to
execute this SQL statement; each attempt resulted
in my SQL session hanging. Looking into the cause:

```sql
SHOW FULL PROCESSLIST;
```
showed that there was a METADATA LOCK error. Some
searching around to find the root of the cause was
unsuccessful, and kill all current processes didn't
fix it either, but restarting SQL did the trick.

** *2014.12.03* **:
I deleted entries in the `halpha` table that were all
NULLs. I'm not sure how those entries were added, but
I suspect it occurs when running `getChironObservation.py`.
I also modified `driveHalpha.py` to update the hsrc_obsid
column.

The hsrc_obsids for the entries already in the DB should
just be equal to their respective `observation_id`s. This
was easily updated using the SQL statement:

```sql
UPDATE halpha SET hsrc_obsid=observation_id WHERE hsrc_obsid IS NULL;
```

Checking the results of this command shows that it
behaved as expected!

2014.12.09:

I want to keep track of when entries are added to the
halpha table. To do so, I added a `datecreated` column:

```sql
ALTER TABLE halpha ADD (datecreated DATETIME);
```

2014.12.10:

Added the `spectra` table to store the reduced
spectra for all the observations:

```sql
CREATE TABLE spectra (spec_id INT AUTO_INCREMENT PRIMARY KEY);
ALTER TABLE spectra ADD (observation_id INT, rawFilename varchar(128), echelleOrder INT);
ALTER TABLE spectra ADD (wavelength FLOAT, flux FLOAT, normFlux FLOAT, dateAdded DATETIME);
```
Its really not necessary to break the table creation
lines up the way I did, but it was useful for debugging
that `order` could not be a column name since
it is a MySQL command.

2014.12.14:

I added two more indexes (in addition to the automatic
 index on spec_id) on the observation_id and
 rawFilename. These are the two most searched
 parameters and will greatly speed up searches. I
 added these indexes using the following command:

 ```sql
 ALTER TABLE spectra ADD INDEX (observation_id),
 ADD INDEX (rawFilename);
 ```

2014.12.16:

There were a few outlier Eps Eri observations that
I want to inspect the coordinates of. Unfortunately
the decimal degree coordinates are only in the DB
going back to early September. I can add the
remainder of the decimal degree (decdeg)
coordinates right within MySQL. This needs to be
executed for both the right ascension and the
declination.

####Right Ascension

To test things out, I will see if my code recreates
the first `obs_ra_decdeg` entry in the DB:
```sql
select obnm, obs_ra_decdeg,
obs_ra, obs_dec_decdeg, obs_dec
FROM observations WHERE object='22049' and
extract(year from date_obs)=2014 and
obnm='achi140929.1145';
```
which returned
```sh
+-----------------+---------------+-------------+----------------+-------------+
| obnm            | obs_ra_decdeg | obs_ra      | obs_dec_decdeg | obs_dec     |
+-----------------+---------------+-------------+----------------+-------------+
| achi140929.1145 |       53.2353 | 03:32:56.48 |       -9.46225 | -09:27:44.1 |
+-----------------+---------------+-------------+----------------+-------------+
1 row in set (0.02 sec)
```
Calculating the decimal degree ra within MySQL:
```sql
UPDATE observations SET obs_ra_decdeg=
(MID(obs_ra, 1, 2) +
MID(obs_ra, 4, 2)/60 +
MID(obs_ra, 7, 5)/3600)*15.
WHERE object='22049' AND
obnm='achi140929.1145';
```
And then querying for the results again returns
the same thing:
```sh
+-----------------+---------------+-------------+----------------+-------------+
| obnm            | obs_ra_decdeg | obs_ra      | obs_dec_decdeg | obs_dec     |
+-----------------+---------------+-------------+----------------+-------------+
| achi140929.1145 |       53.2353 | 03:32:56.48 |       -9.46225 | -09:27:44.1 |
+-----------------+---------------+-------------+----------------+-------------+
1 row in set (0.00 sec)
```

To add the remainder
of the `obs_ra_decdeg` values I used the following
command:

```sql
UPDATE observations SET obs_ra_decdeg=
(MID(obs_ra, 1, 2) +
MID(obs_ra, 4, 2)/60 +
MID(obs_ra, 7, 5)/3600)*15.
WHERE object='22049' AND
obs_ra_decdeg IS NULL;
```

And running this on all observations:
```sql
UPDATE observations SET obs_ra_decdeg=
(MID(obs_ra, 1, 2) +
MID(obs_ra, 4, 2)/60 +
MID(obs_ra, 7, 5)/3600)*15.
WHERE obs_ra IS NOT NULL AND
obs_ra_decdeg IS NULL;
```

Results in

```sql
Query OK, 251264 rows affected (14.69 sec)
Rows matched: 251264  Changed: 251264  Warnings: 0
```

###2014.12.17
####Declination

The declination will be slightly trickier since
there are both positive and negative values.
In addition to using the `MID/SUBSTR/SUBSTRING`
routine, I will extract the hemisphere of the
object (positive or negative) using the
`SUBSTRING_INDEX` function.

To test this out, I have identified a junk
observation in the northern hemisphere that
has `obs_dec specified, but not `obs_dec_decdeg`.

```sql
SELECT MID(obs_dec, 1, 2) +
       MID(obs_dec, 4, 2)/60. +
       MID(obs_dec, 7, 5)/3600 AS decdeg
   FROM observations
   WHERE SUBSTRING_INDEX(obs_dec, ':', 1)>0 AND
      obs_dec_decdeg IS NULL AND
      observation_id = 12955;
```

That works. Now to execute on the full DB:

```sql
SELECT MID(obs_dec, 1, 2) +
       MID(obs_dec, 4, 2)/60. +
       MID(obs_dec, 7, 5)/3600 AS decdeg
   FROM observations
   WHERE SUBSTRING_INDEX(obs_dec, ':', 1)>0 AND
      obs_dec_decdeg IS NULL;
```

Resulted in

```sql
+--------------------+
| decdeg             |
+--------------------+
| 11.966638888888887 |
.
.
.
+--------------------+
31098 rows in set (1.15 sec)

```
And now to update everything:
```sql
UPDATE observations
SET obs_dec_decdeg =
   MID(obs_dec, 1, 2) +
   MID(obs_dec, 4, 2)/60. +
   MID(obs_dec, 7, 5)/3600
WHERE SUBSTRING_INDEX(obs_dec, ':', 1)>0 AND
   obs_dec_decdeg IS NULL;
```
which resulted in:
```sql
Query OK, 31098 rows affected (3.36 sec)
Rows matched: 31098  Changed: 31098  Warnings: 0

```

####Updating all negative declinations:

```sql
SELECT MID(obs_dec, 1, 3),
       MID(obs_dec, 5, 2),
       MID(obs_dec, 8, 5),
       obs_dec, object
   FROM observations
   WHERE SUBSTRING_INDEX(obs_dec, ':', 1)<0 AND
      obs_dec_decdeg IS NULL AND
      imagetyp='object'
      LIMIT 5;
```

That looks good. Now to try the calculation:

```sql
UPDATE observations
SET obs_dec_decdeg =
   MID(obs_dec, 1, 3) -
   MID(obs_dec, 5, 2)/60. -
   MID(obs_dec, 8, 5)/3600.
WHERE SUBSTRING_INDEX(obs_dec, ':', 1)<0 AND
   obs_dec_decdeg IS NULL;
```
which resulted in:
```sql
Query OK, 213226 rows affected (9.69 sec)
Rows matched: 213226  Changed: 213226  Warnings: 0

```

###2014.12.20
To quickly determine which nights have already
been added to the table, I have added an
additional column, `nightObserved`, and an
index on that column.

```sql
ALTER TABLE spectra ADD COLUMN nightObserved INT,
ADD INDEX (nightObserved);
```

###2014.12.21
This failed with the error

```sql
ERROR 1878 (HY000): Temporary file write failure.
```

I searched around and this is due to a lack a
free space. Behind the scenes MySQL creates
a copy of the table being ALTERed. Since the
spectra table lives on another drive and the
size of the table exceeds the size of the
internal drive of the server, it can no
longer ALTER the table.

I got around this by changing the `tmp` directory
for the database to the external drive where
the database is stored, `tous`. I first
attempted to do this following MySQL's
[directions](http://dev.mysql.com/doc/refman/5.0/en/temporary-files.html)
of modifying my path, but that didn't work.
Instead, I modified the `my.cnf` file:

```sh
which mysql
mysql: 	 aliased to /usr/local/mysql/bin/mysql
cd /usr/local/mysql
sudo emacs my.cnf
```

and then added the line
```sh
tmpdir /tous/tmp
```
The MySQL server was then restarted. After this
modification the GUI interface in System
Preferences no longer works, but the MySQL
server can still be started via the command
line:

```sh
/usr/local/mysql/bin/mysqld
```
And then checking to make sure `tmpdir` has
indeed been updated, I ran the commands:

```sh
/usr/local/bin/mysql/bin/mysqld --verbose --help
```

and

```sh
/usr/local/bin/mysql/bin/mysqladmin variables
```

Both options showed that the tmpdir has indeed
been updated to point to `/tous/tmp`.

I then reran the command:
```sql
ALTER TABLE spectra ADD COLUMN nightObserved INT,
ADD INDEX (nightObserved);
```

###2014.12.23
This finally finished:

```sql
mysql> ALTER TABLE spectra ADD COLUMN nightObserved INT,
    -> ADD INDEX (nightObserved);
Query OK, 0 rows affected (1 day 13 hours 23 min 0.25 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql>
```

To fill in all the `nightObserved` rows, the following
statement was executed:

```sql
UPDATE spectra SET nightObserved=MID(rawFilename, 11, 6) WHERE nightObserved IS NULL;
```

###2015.01.03
####drop temp tables
There are a few temporary tables that I'd like to clean up.
These are

- \#Tableau_sid_00032...
- tempObsIds
- tempobnms

To remove them permanently I'll use the command

```sql
DROP TABLE table_name
```

MySQL didn't like the Tableau table; my guess is because
of the # out front. A workaround is including ` marks
on either side of the name:

```sql
DROP TABLE `#Tableau_sid_00032...`;
```

and that worked. I dropped the other two temp tables
without the need for the tick characters.

I also need to remove and readd observations in
 the DB from the night of 140725. Observations
 from that night were added, and the
filenames were later changed. This has caused
problems when using the database to query for
observations, and then restoring the FITS files
for analysis.

I created the file `tableListFull.txt` that contains
 the names of all tables that were affected by this.
 Currently, `tableListFull.txt` is everything in
 `tableList.txt` plus `halpha` and `spectra`. These
 tables are not included in `tableList.txt` because
 that file is used to determine which tables are
 appended to when running `getChironFiles.py`. Since
 I do not want rows full of `NULL` values, these
 two tables are not listed in `tableList.txt`.
 `tableListFull.txt` will be used both for reference,
 and also by a new routine that will delete
 observations from a given night and re-add them.

###2015.01.04

####delete rows from 140725
I created an IPython notebook, called
`deleteNights.ipynb`, which describes the code to
delete all rows from all tables that contain
observation information for a given night.

To test out `deleteNights`, I used a test
query:

```sql
SELET COUNT(*) FROM table_name
WHERE observation_id in
(SELECT observation_id FROM observations
  WHERE MID(rawfilename, 11, 6)='140725');
```

This is query is contained in a FOR loop that
cycles over the table_names.

That returned the expected result for all tables.
Now to `DELETE` all rows:

```sql
DELETE FROM table_name
WHERE observation_id in
(SELECT observation_id FROM observations
  WHERE MID(rawfilename, 11, 6)='140725');
```

That returned a `None` value for each table. I then
reran the test code, which returned zeroes for each
table, demonstrating that the DELETE code in fact
worked. I also executed the test code (SELECT
  COUNT(*)) on the night of `140726` to make sure
I didn't accidentally delete more than just the
night of interest. Thankfully, I did not.

####spectra Table
An instance of `storeSpectra.py` ran into a
problem over break. The error message was

```sql
DataError: (1264, u"Out of range value for column 'spec_id' at row 305")
```

This was due to using a normal `INT` for the
index data type. The solution was to change
the data type of spec_id to `BIGINT`:

```sql
ALTER TABLE spectra MODIFY spec_id BIGINT;
```

I'll now be able to add up to 9 Quadrillion
rows.

###2015.01.05

####auto incrementing spec_id
After over 7 hours, the `ALTER TABLE` command
from yesterday successfully completed:

```sql
mysql> ALTER TABLE spectra MODIFY spec_id BIGINT;
Query OK, 2093569024 rows affected (7 hours 35 min 5.18 sec)
Records: 2093569024  Duplicates: 0  Warnings: 0
```

The only problem I have now is that it removed
the auto incrementing extra. Here is the column
description before:

```sql
mysql> describe spectra;
+----------------+--------------+------+-----+---------+----------------+
| Field          | Type         | Null | Key | Default | Extra          |
+----------------+--------------+------+-----+---------+----------------+
| spec_id        | int(11)      | NO   | PRI | NULL    | auto_increment |

```

And here is the column description after:
```sql
mysql> describe spectra;
+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+----------------+--------------+------+-----+---------+-------+
| spec_id        | bigint(20)   | NO   | PRI | 0       |       |
```

Now it won't accept a `NULL` value (or pandas `None`)
and auto increment it to the next spec_id. To
fix this, I issued the command:

```sql
ALTER TABLE spectra MODIFY spec_id BIGINT AUTO INCREMENT DEFAULT NULL;
```

I tested this on a test table and it seems to be
the correct fix; I'll know in ~7.5 hours whether
or not it really worked.

###2015.01.09

####expmetercounts Table
I added a table to `chirondb` to store the exposure meter counts information, `expmetercounts`. The columns are described in `table/ExpmeterCountsTables.txt`. The command used to add the table was:

```sql
CREATE TABLE expmetercounts (expmcts_id BIGINT AUTO_INCREMENT PRIMARY KEY);
ALTER TABLE expmetercounts ADD (observation_id INT, time DATETIME, mjdtime DOUBLE, counts FLOAT);
ALTER TABLE expmetercounts ADD (original_time FLOAT(11,6), filename VARCHAR(128), dateAdded TIMESTAMP);
```

and then add an index on mjdtime and time:

```sql
ALTER TABLE expmetercounts ADD INDEX (mjdtime), ADD INDEX (time);
```
