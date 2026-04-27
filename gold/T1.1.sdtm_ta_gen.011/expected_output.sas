/* ================================================================
   SDTM TA Domain Creation Program
   Study: CDISCPilot01
   Domain: TA (Trial Arms)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.ta_raw;
    set raw.ta;
run;

proc sort data=work.ta_raw; by USUBJID; run;

data sdtm.ta;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TASEQ 8;
    set work.ta_raw;

    retain TASEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "TA";

    if first.USUBJID then TASEQ = 0;
    TASEQ = TASEQ + 1;

    /* Domain-specific variable mappings for Trial Arms */
    /* ARMCD, ARM, TAETORD, ETCD, ELEMENT */

    keep STUDYID DOMAIN USUBJID TASEQ ARMCD, ARM, TAETORD, ETCD, ELEMENT;
run;

proc datasets library=sdtm nolist;
    modify ta;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TASEQ = "Sequence Number";
run; quit;

filename xout "path/to/output/ta.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select ta;
run;
libname xout clear;
filename xout clear;
