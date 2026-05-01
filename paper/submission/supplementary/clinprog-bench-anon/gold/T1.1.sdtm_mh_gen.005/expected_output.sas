/* ================================================================
   SDTM MH Domain Creation Program
   Study: CDISCPilot01
   Domain: MH (Medical History)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.mh_raw;
    set raw.mh;
run;

proc sort data=work.mh_raw; by USUBJID; run;

data sdtm.mh;
    length STUDYID $12 DOMAIN $2 USUBJID $11 MHSEQ 8;
    set work.mh_raw;

    retain MHSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "MH";

    if first.USUBJID then MHSEQ = 0;
    MHSEQ = MHSEQ + 1;

    /* Domain-specific variable mappings for Medical History */
    /* MHTERM, MHDECOD, MHBODSYS, MHSTDTC, MHENDTC, MHCAT */

    keep STUDYID DOMAIN USUBJID MHSEQ MHTERM  MHDECOD  MHBODSYS  MHSTDTC  MHENDTC  MHCAT;
run;

proc datasets library=sdtm nolist;
    modify mh;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              MHSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/mh.xpt);
filename xout "path/to/output/mh.xpt";
libname  xout xport;
data xout.mh;
    set sdtm.mh;
run;
libname xout clear;
filename xout clear;
