/* ================================================================
   SDTM SUPPDS Domain Creation Program
   Study: CDISCPilot01
   Domain: SUPPDS (Supplemental DS)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.suppds_raw;
    set raw.suppds;
run;

proc sort data=work.suppds_raw; by USUBJID; run;

data sdtm.suppds;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUPPDSSEQ 8;
    set work.suppds_raw;

    retain SUPPDSSEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SUPPDS";

    if first.USUBJID then SUPPDSSEQ = 0;
    SUPPDSSEQ = SUPPDSSEQ + 1;

    /* Domain-specific variable mappings for Supplemental DS */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL */

    keep STUDYID DOMAIN USUBJID SUPPDSSEQ RDOMAIN  USUBJID  IDVAR  IDVARVAL  QNAM  QVAL  QLABEL;
run;

proc datasets library=sdtm nolist;
    modify suppds;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUPPDSSEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/suppds.xpt);
filename xout "path/to/output/suppds.xpt";
libname  xout xport;
data xout.suppds;
    set sdtm.suppds;
    drop SUPPDSSEQ;
run;
libname xout clear;
filename xout clear;
