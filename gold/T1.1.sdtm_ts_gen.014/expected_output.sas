/* ================================================================
   SDTM TS Domain Creation Program
   Study: CDISCPilot01
   Domain: TS (Trial Summary)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.ts_raw;
    set raw.ts;
run;

proc sort data=work.ts_raw; by USUBJID; run;

data sdtm.ts;
    length STUDYID $12 DOMAIN $2 USUBJID $11 TSSEQ 8;

    retain TSSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "TS";

    if first.USUBJID then TSSEQ = 0;
    TSSEQ = TSSEQ + 1;

    /* Domain-specific variable mappings for Trial Summary */
    /* TSPARMCD, TSPARM, TSVAL */

    keep STUDYID DOMAIN USUBJID TSSEQ TSPARMCD, TSPARM, TSVAL;
run;

proc datasets library=sdtm nolist;
    modify ts;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              TSSEQ = "Sequence Number";
run; quit;

proc export data=sdtm.ts
    outfile="path/to/output/ts.xpt"
    dbms=xport replace;
run;
