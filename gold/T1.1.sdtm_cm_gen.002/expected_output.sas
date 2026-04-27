/* ================================================================
   SDTM CM Domain Creation Program
   Study: CDISCPilot01
   Domain: CM (Concomitant Medications)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.cm_raw;
    set raw.cm;
run;

proc sort data=work.cm_raw; by USUBJID; run;

data sdtm.cm;
    length STUDYID $12 DOMAIN $2 USUBJID $11 CMSEQ 8;
    set work.cm_raw;

    retain CMSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "CM";

    if first.USUBJID then CMSEQ = 0;
    CMSEQ = CMSEQ + 1;

    /* Domain-specific variable mappings for Concomitant Medications */
    /* CMTRT, CMDECOD, CMINDC, CMCLAS, CMROUTE, CMSTDTC, CMENDTC, CMDOSU, CMDOSFRQ */

    keep STUDYID DOMAIN USUBJID CMSEQ CMTRT  CMDECOD  CMINDC  CMCLAS  CMROUTE  CMSTDTC  CMENDTC  CMDOSU  CMDOSFRQ;
run;

proc datasets library=sdtm nolist;
    modify cm;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              CMSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/cm.xpt);
filename xout "path/to/output/cm.xpt";
libname  xout xport;
data xout.cm;
    set sdtm.cm;
run;
libname xout clear;
filename xout clear;
