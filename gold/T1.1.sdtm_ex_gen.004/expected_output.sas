/* ================================================================
   SDTM EX Domain Creation Program
   Study: CDISCPilot01
   Domain: EX (Exposure)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.ex_raw;
    set raw.ex;
run;

proc sort data=work.ex_raw; by USUBJID; run;

data sdtm.ex;
    length STUDYID $12 DOMAIN $2 USUBJID $11 EXSEQ 8;

    retain EXSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "EX";

    if first.USUBJID then EXSEQ = 0;
    EXSEQ = EXSEQ + 1;

    /* Domain-specific variable mappings for Exposure */
    /* EXTRT, EXDOSE, EXDOSU, EXROUTE, EXSTDTC, EXENDTC */

    keep STUDYID DOMAIN USUBJID EXSEQ EXTRT, EXDOSE, EXDOSU, EXROUTE, EXSTDTC, EXENDTC;
run;

proc datasets library=sdtm nolist;
    modify ex;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              EXSEQ = "Sequence Number";
run; quit;

proc export data=sdtm.ex
    outfile="path/to/output/ex.xpt"
    dbms=xport replace;
run;
