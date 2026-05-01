/* ================================================================
   SDTM SUPPLB Domain Creation Program
   Study: CDISCPilot01
   Domain: SUPPLB (Supplemental LB)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.supplb_raw;
    set raw.supplb;
run;

proc sort data=work.supplb_raw; by USUBJID; run;

data sdtm.supplb;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUPPLBSEQ 8;
    set work.supplb_raw;

    retain SUPPLBSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SUPPLB";

    if first.USUBJID then SUPPLBSEQ = 0;
    SUPPLBSEQ = SUPPLBSEQ + 1;

    /* Domain-specific variable mappings for Supplemental LB */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL */

    keep STUDYID DOMAIN USUBJID SUPPLBSEQ RDOMAIN  USUBJID  IDVAR  IDVARVAL  QNAM  QVAL  QLABEL;
run;

proc datasets library=sdtm nolist;
    modify supplb;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUPPLBSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/supplb.xpt);
filename xout "path/to/output/supplb.xpt";
libname  xout xport;
data xout.supplb;
    set sdtm.supplb;
    drop SUPPLBSEQ;
run;
libname xout clear;
filename xout clear;
