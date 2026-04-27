/* ================================================================
   SDTM SC Domain Creation Program
   Study: CDISCPilot01
   Domain: SC (Subject Characteristics)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.sc_raw;
    set raw.sc;
run;

proc sort data=work.sc_raw; by USUBJID; run;

data sdtm.sc;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SCSEQ 8;

    retain SCSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SC";

    if first.USUBJID then SCSEQ = 0;
    SCSEQ = SCSEQ + 1;

    /* Domain-specific variable mappings for Subject Characteristics */
    /* SCTESTCD, SCTEST, SCORRES, SCSTRESC, SCSTRESN */

    keep STUDYID DOMAIN USUBJID SCSEQ SCTESTCD, SCTEST, SCORRES, SCSTRESC, SCSTRESN;
run;

proc datasets library=sdtm nolist;
    modify sc;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SCSEQ = "Sequence Number";
run; quit;

proc export data=sdtm.sc
    outfile="path/to/output/sc.xpt"
    dbms=xport replace;
run;
