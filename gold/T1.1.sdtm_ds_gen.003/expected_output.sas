/* ================================================================
   SDTM DS Domain Creation Program
   Study: CDISCPilot01
   Domain: DS (Disposition)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.ds_raw;
    set raw.ds;
run;

proc sort data=work.ds_raw; by USUBJID; run;

data sdtm.ds;
    length STUDYID $12 DOMAIN $2 USUBJID $11 DSSEQ 8;

    retain DSSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "DS";

    if first.USUBJID then DSSEQ = 0;
    DSSEQ = DSSEQ + 1;

    /* Domain-specific variable mappings for Disposition */
    /* DSDECOD, DSTERM, DSCAT, DSSTDTC, DSENDTC, VISIT, VISITNUM */

    keep STUDYID DOMAIN USUBJID DSSEQ DSDECOD, DSTERM, DSCAT, DSSTDTC, DSENDTC, VISIT, VISITNUM;
run;

proc datasets library=sdtm nolist;
    modify ds;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              DSSEQ = "Sequence Number";
run; quit;

proc export data=sdtm.ds
    outfile="path/to/output/ds.xpt"
    dbms=xport replace;
run;
