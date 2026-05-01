/* ================================================================
   SDTM SUPPDM Domain Creation Program
   Study: CDISCPilot01
   Domain: SUPPDM (Supplemental DM)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.suppdm_raw;
    set raw.suppdm;
run;

proc sort data=work.suppdm_raw; by USUBJID; run;

data sdtm.suppdm;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUPPDMSEQ 8;
    set work.suppdm_raw;

    retain SUPPDMSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SUPPDM";

    if first.USUBJID then SUPPDMSEQ = 0;
    SUPPDMSEQ = SUPPDMSEQ + 1;

    /* Domain-specific variable mappings for Supplemental DM */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL */

    keep STUDYID DOMAIN USUBJID SUPPDMSEQ RDOMAIN  USUBJID  IDVAR  IDVARVAL  QNAM  QVAL  QLABEL;
run;

proc datasets library=sdtm nolist;
    modify suppdm;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUPPDMSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/suppdm.xpt);
filename xout "path/to/output/suppdm.xpt";
libname  xout xport;
data xout.suppdm;
    set sdtm.suppdm;
    drop SUPPDMSEQ;
run;
libname xout clear;
filename xout clear;
