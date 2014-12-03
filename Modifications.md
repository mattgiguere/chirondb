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
