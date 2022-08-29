JSON Schema
===========

We are trying to make a more queryable schema and use the
OSCF document, here: https://github.com/ocsf/ocsf-docs/blob/main/Understanding%20OCSF.pdf for labels in JSON.


Schema Items in use.
===================

We will try to apply these  as we work on items.

Time
----

Note that an OSCF timestamp_t is in *milliseconds*  since the epoch

* ref_time:string  (original event time as encoded by the even producer. A string, because the producer could haev done anything.

* _time:timestamp_t "normalized" event occurrence time. (roughly the logger's belief when the time of the original event integer milliseconnds scine epoch.

other
-----

* Profile:string  Use like tags to identify what's collected and help with queries.
