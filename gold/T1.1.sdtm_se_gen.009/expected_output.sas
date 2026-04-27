/* ================================================================
   SDTM SE Domain Creation Program
   Study: CDISCPilot01
   Domain: SE (Subject Elements)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.se_raw;
    set raw.se;
run;

proc sort data=work.se_raw; by USUBJID; run;

data sdtm.se;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SESEQ 8;
    set work.se_raw;

    retain SESEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SE";

    if first.USUBJID then SESEQ = 0;
    SESEQ = SESEQ + 1;

    /* Domain-specific variable mappings for Subject Elements */
    /* ETCD, ELEMENT, SESTDTC, SEENDTC, TAETORD */

    keep STUDYID DOMAIN USUBJID SESEQ ETCD  ELEMENT  SESTDTC  SEENDTC  TAETORD;
run;

proc datasets library=sdtm nolist;
    modify se;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SESEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/se.xpt);
filename xout "path/to/output/se.xpt";
libname  xout xport;
data xout.se;
    set sdtm.se;
run;
libname xout clear;
filename xout clear;
