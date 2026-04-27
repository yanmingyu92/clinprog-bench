/* ================================================================
   SDTM TE Domain Creation Program
   Study: CDISCPilot01
   Domain: TE (Trial Elements)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.te_raw;
    set raw.te;
run;

proc sort data=work.te_raw; by USUBJID; run;

data sdtm.te;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TESEQ 8;
    set work.te_raw;

    retain TESEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "TE";

    if first.USUBJID then TESEQ = 0;
    TESEQ = TESEQ + 1;

    /* Domain-specific variable mappings for Trial Elements */
    /* ETCD, ELEMENT, TESTRL, TEENRL, TEDUR */

    keep STUDYID DOMAIN USUBJID TESEQ ETCD, ELEMENT, TESTRL, TEENRL, TEDUR;
run;

proc datasets library=sdtm nolist;
    modify te;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TESEQ = "Sequence Number";
run; quit;

filename xout "path/to/output/te.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select te;
run;
libname xout clear;
filename xout clear;
