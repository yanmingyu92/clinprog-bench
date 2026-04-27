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

proc sort data=work.ti_raw; by USUBJID; run;

data sdtm.ti;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TISEQ 8;

    retain TISEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "TI";

    if first.USUBJID then TISEQ = 0;
    TISEQ = TISEQ + 1;

    /* Domain-specific variable mappings for Trial Inclusion/Exclusion */
    /* TSPARMCD, TSPARM, TSVAL */

    keep STUDYID DOMAIN USUBJID TISEQ TSPARMCD, TSPARM, TSVAL;
run;

proc datasets library=sdtm nolist;
    modify ti;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TISEQ = "Sequence Number";
run; quit;

proc export data=sdtm.ti
    outfile="path/to/output/ti.xpt"
    dbms=xport replace;
run;
