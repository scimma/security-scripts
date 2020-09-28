report.py is a driver programs that produces
reports of interest to AWS information security
and AWS resource management.


./report.py --listall
lists  available reports.

BY default allreports are printed.

./report.py --only <glob specific reports>

the Only option prints reports that match
a "glob" (e.g. file system wildcard type name.

The reporting stucutre used by the system
makes use of two kinds of objects.
Acquisition objecta get data about a topic
Reporting objects generate a report on
a specific concern

The acquisition and  reporting objects
commumunciate though a SQLLITE3 Database.
By default, this database is in memory and
is regenerated for each invocation of report.py


./report.py --dbfile <file>

The dbfile option writes information to an
SQLLITE3 database file cache, with lifetime of
about an hour.


