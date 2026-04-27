/* ================================================================
   SDTM QS Domain Creation Program
   Study: CDISCPilot01
   Domain: QS (Questionnaires)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.qs_raw;
    set raw.qs;
run;

proc sort data=work.qs_raw; by USUBJID; run;

data sdtm.qs;
    length STUDYID $12 DOMAIN $2 USUBJID $11 QSSEQ 8;
    set work.qs_raw;

    retain QSSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "QS";

    if first.USUBJID then QSSEQ = 0;
    QSSEQ = QSSEQ + 1;

    /* Domain-specific variable mappings for Questionnaires */
    /* QSTESTCD, QSTEST, QSORRES, QSSTRESC, QSSTRESN, VISITNUM */

    keep STUDYID DOMAIN USUBJID QSSEQ QSTESTCD, QSTEST, QSORRES, QSSTRESC, QSSTRESN, VISITNUM;
run;

proc datasets library=sdtm nolist;
    modify qs;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              QSSEQ = "Sequence Number";
run; quit;

filename xout "path/to/output/qs.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select qs;
run;
libname xout clear;
filename xout clear;
