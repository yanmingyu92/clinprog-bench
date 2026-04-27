/* ================================================================
   SDTM SUPPAE Domain Creation Program
   Study: CDISCPilot01
   Domain: SUPPAE (Supplemental AE)
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.suppae_raw;
    set raw.suppae;
run;

proc sort data=work.suppae_raw; by USUBJID; run;

data sdtm.suppae;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUPPAESEQ 8;
    set work.suppae_raw;

    retain SUPPAESEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "SUPPAE";

    if first.USUBJID then SUPPAESEQ = 0;
    SUPPAESEQ = SUPPAESEQ + 1;

    /* Domain-specific variable mappings for Supplemental AE */
    /* RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL */

    keep STUDYID DOMAIN USUBJID SUPPAESEQ RDOMAIN  USUBJID  IDVAR  IDVARVAL  QNAM  QVAL  QLABEL;
run;

proc datasets library=sdtm nolist;
    modify suppae;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUPPAESEQ = "Sequence Number";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/suppae.xpt);
filename xout "path/to/output/suppae.xpt";
libname  xout xport;
data xout.suppae;
    set sdtm.suppae;
    drop SUPPAESEQ;
run;
libname xout clear;
filename xout clear;
