/* ================================================================
   SDTM SUPPLB Domain Creation Program
   Study: CDISCPilot01
   Domain: SUPPLB (Supplemental LB)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.supplb_raw;
    set raw.supplb;
run;

proc sort data=work.supplb_raw; by USUBJID; run;

data sdtm.supplb;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUPPLBSEQ 8;

    retain SUPPLBSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SUPPLB";

    if first.USUBJID then SUPPLBSEQ = 0;
    SUPPLBSEQ = SUPPLBSEQ + 1;

    /* Domain-specific variable mappings for Supplemental LB */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL */

    keep STUDYID DOMAIN USUBJID SUPPLBSEQ RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL;
run;

proc datasets library=sdtm nolist;
    modify supplb;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUPPLBSEQ = "Sequence Number";
run; quit;

proc export data=sdtm.supplb
    outfile="path/to/output/supplb.xpt"
    dbms=xport replace;
run;
