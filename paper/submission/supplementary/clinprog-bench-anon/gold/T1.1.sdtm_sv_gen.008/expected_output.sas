/* ================================================================
   SDTM SV Domain Creation Program
   Study: CDISCPilot01
   Domain: SV (Subject Visits)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.sv_raw;
    set raw.sv;
run;

proc sort data=work.sv_raw; by USUBJID; run;

data sdtm.sv;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SVSEQ 8;
    set work.sv_raw;

    retain SVSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SV";

    if first.USUBJID then SVSEQ = 0;
    SVSEQ = SVSEQ + 1;

    /* Domain-specific variable mappings for Subject Visits */
    /* VISITNUM, VISIT, SVSTDTC, SVENDTC, SVDY */

    keep STUDYID DOMAIN USUBJID SVSEQ VISITNUM  VISIT  SVSTDTC  SVENDTC  SVDY;
run;

proc datasets library=sdtm nolist;
    modify sv;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SVSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/sv.xpt);
filename xout "path/to/output/sv.xpt";
libname  xout xport;
data xout.sv;
    set sdtm.sv;
run;
libname xout clear;
filename xout clear;
