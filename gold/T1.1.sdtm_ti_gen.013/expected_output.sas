/* ================================================================
   SDTM TI Domain Creation Program
   Study: CDISCPilot01
   Domain: TI (Trial Inclusion/Exclusion)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.ti_raw;
    set raw.ti;
run;



data sdtm.ti;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TISEQ 8;
    set work.ti_raw;

    retain TISEQ;

    STUDYID = "&studyid";
    DOMAIN  = "TI";
    TISEQ = TISEQ + 1;

    /* Domain-specific variable mappings for Trial Inclusion/Exclusion */
    /* TSPARMCD, TSPARM, TSVAL */

    keep STUDYID DOMAIN USUBJID TISEQ TSPARMCD  TSPARM  TSVAL;
run;

proc datasets library=sdtm nolist;
    modify ti;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TISEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/ti.xpt);
filename xout "path/to/output/ti.xpt";
libname  xout xport;
data xout.ti;
    set sdtm.ti;
run;
libname xout clear;
filename xout clear;
