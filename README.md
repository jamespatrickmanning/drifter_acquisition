# drifter_acquisition

These are routines developed over the past few decades to acquire satellite-tracked drifter data and prepare it for processing.
The full story of this development (with links to various detailed notes) is currently stored in the "drift_overview" googledoc at:

https://docs.google.com/document/d/1JwuvELNuJnx6OV4QjebwDt9m1HNjVQ4q4QrfiGm6pqY/edit

There is also a set of code to deal with the metadata processing such as "update_drift_header.py" and "get_web_driftheader.py" which prepares data for the old "drift_header" ORACLE table. 

Note: The code in this folder now includes the "fixfix.py" routine which does the QA/QC prior to loading tracks in the database.
There is also some code for processing USCG data and other miscellaneous utilities.

In addition to this repo,  I keep a backup version of the drifter code in a backup Linux machine in my basement. However, the most up-to-date code is probably on my kitchen-table-Linux machine.
