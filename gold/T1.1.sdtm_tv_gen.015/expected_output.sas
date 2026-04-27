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

proc sort data=work.tv_raw; by USUBJID; run;

data sdtm.tv;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TVSEQ 8;
    set work.tv_raw;

    retain TVSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "TV";

    if first.USUBJID then TVSEQ = 0;
    TVSEQ = TVSEQ + 1;

    /* Domain-specific variable mappings for Trial Visits */
    /* VISITNUM, VISIT, VISTPT, VISTPTREF */

    keep STUDYID DOMAIN USUBJID TVSEQ VISITNUM, VISIT, VISTPT, VISTPTREF;
run;

proc datasets library=sdtm nolist;
    modify tv;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TVSEQ = "Sequence Number";
run; quit;

filename xout "path/to/output/tv.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select tv;
run;
libname xout clear;
filename xout clear;
