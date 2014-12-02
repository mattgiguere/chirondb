####Modifications

This document describes modifications made by hand to the chirondb MySQL database since 2014.12.02.

2014.12.02:
To help keep track of the observation used to determine the H-alpha EW a new column named `hrsrc_obsid` was added.

```SQL
ALTER TABLE halpha ADD (hrsrc_obsid INT);
```
