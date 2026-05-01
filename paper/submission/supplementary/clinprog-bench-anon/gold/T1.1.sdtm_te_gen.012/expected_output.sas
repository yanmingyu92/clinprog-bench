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



data sdtm.te;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TESEQ 8;
    set work.te_raw;

    retain TESEQ;

    STUDYID = "&studyid";
    DOMAIN  = "TE";
    TESEQ = TESEQ + 1;

    /* Domain-specific variable mappings for Trial Elements */
    /* ETCD, ELEMENT, TESTRL, TEENRL, TEDUR */

    keep STUDYID DOMAIN USUBJID TESEQ ETCD  ELEMENT  TESTRL  TEENRL  TEDUR;
run;

proc datasets library=sdtm nolist;
    modify te;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TESEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/te.xpt);
filename xout "path/to/output/te.xpt";
libname  xout xport;
data xout.te;
    set sdtm.te;
run;
libname xout clear;
filename xout clear;
