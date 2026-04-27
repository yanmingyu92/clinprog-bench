/* ================================================================
   SDTM RELREC Domain Creation Program
   Study: CDISCPilot01
   Domain: RELREC (Related Records)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.relrec_raw;
    set raw.relrec;
run;

proc sort data=work.relrec_raw; by USUBJID; run;

data sdtm.relrec;
    length STUDYID $12 DOMAIN $2 USUBJID $11 RELRECSEQ 8;
    set work.relrec_raw;

    retain RELRECSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "RELREC";

    if first.USUBJID then RELRECSEQ = 0;
    RELRECSEQ = RELRECSEQ + 1;

    /* Domain-specific variable mappings for Related Records */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, RELTYPE, RELID */

    keep STUDYID DOMAIN USUBJID RELRECSEQ RDOMAIN, USUBJID, IDVAR, IDVARVAL, RELTYPE, RELID;
run;

proc datasets library=sdtm nolist;
    modify relrec;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              RELRECSEQ = "Sequence Number";
run; quit;

filename xout "path/to/output/relrec.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select relrec;
run;
libname xout clear;
filename xout clear;
