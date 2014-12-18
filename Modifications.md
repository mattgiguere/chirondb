####Modifications

This document describes modifications made by hand
to the chirondb MySQL database since 2014.12.02.

2014.12.02:
To help keep track of the observation used to
determine the H-alpha EW a new column named
`hsrc_obsid` was added.

```SQL
ALTER TABLE halpha ADD (hrsc_obsid INT);
```

and when things crashed and I finally got to the
root of the problem I fixed my typo:

```SQL
ALTER TABLE halpha DROP (hrsc_obsid INT);
ALTER TABLE halpha ADD (hsrc_obsid INT);
```

There were some additional issues attempting to
execute this SQL statement; each attempt resulted
in my SQL session hanging. Looking into the cause:

```SQL
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

```SQL
UPDATE halpha SET hsrc_obsid=observation_id WHERE hsrc_obsid IS NULL;
```

Checking the results of this command shows that it
behaved as expected!

2014.12.09:

I want to keep track of when entries are added to the
halpha table. To do so, I added a `datecreated` column:

```SQL
ALTER TABLE halpha ADD (datecreated DATETIME);
```

2014.12.10:

Added the `spectra` table to store the reduced
spectra for all the observations:

```SQL
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

 ```SQL
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
```SQL
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
```SQL
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

```SQL
UPDATE observations SET obs_ra_decdeg=
(MID(obs_ra, 1, 2) +
MID(obs_ra, 4, 2)/60 +
MID(obs_ra, 7, 5)/3600)*15.
WHERE object='22049' AND
obs_ra_decdeg IS NULL;
```

And running this on all observations:
```SQL
UPDATE observations SET obs_ra_decdeg=
(MID(obs_ra, 1, 2) +
MID(obs_ra, 4, 2)/60 +
MID(obs_ra, 7, 5)/3600)*15.
WHERE obs_ra IS NOT NULL AND
obs_ra_decdeg IS NULL;
```

Results in

```SQL
Query OK, 251264 rows affected (14.69 sec)
Rows matched: 251264  Changed: 251264  Warnings: 0
```

####Declination

The declination will be slightly trickier since
there are both positive and negative values.
Instead of using the `MID/SUBSTR/SUBSTRING`
routine, I should extract the contents of the
obs_dec string using 
