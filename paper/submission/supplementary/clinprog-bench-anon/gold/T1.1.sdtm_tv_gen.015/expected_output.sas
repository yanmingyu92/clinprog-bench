/* ================================================================
   SDTM TV Domain Creation Program
   Study: CDISCPilot01
   Domain: TV (Trial Visits)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.tv_raw;
    set raw.tv;
run;



data sdtm.tv;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TVSEQ 8;
    set work.tv_raw;

    retain TVSEQ;

    STUDYID = "&studyid";
    DOMAIN  = "TV";
    TVSEQ = TVSEQ + 1;

    /* Domain-specific variable mappings for Trial Visits */
    /* VISITNUM, VISIT, VISTPT, VISTPTREF */

    keep STUDYID DOMAIN USUBJID TVSEQ VISITNUM  VISIT  VISTPT  VISTPTREF;
run;

proc datasets library=sdtm nolist;
    modify tv;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TVSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/tv.xpt);
filename xout "path/to/output/tv.xpt";
libname  xout xport;
data xout.tv;
    set sdtm.tv;
run;
libname xout clear;
filename xout clear;
