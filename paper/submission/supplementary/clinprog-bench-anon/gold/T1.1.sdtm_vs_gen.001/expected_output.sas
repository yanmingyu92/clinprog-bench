/* ================================================================
   SDTM VS Domain Creation Program
   Study: CDISCPilot01
   Domain: VS (Vital Signs)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw vital signs data (already in long/SDTM format) --- */
data work.vs_raw;
    set raw.vs;
run;

/* --- Derive SDTM VS variables --- */
proc sort data=work.vs_raw; by USUBJID VSTESTCD VISITNUM; run;

data sdtm.vs;
    length STUDYID $12 DOMAIN $2 USUBJID $11 VSSEQ 8
           VSTESTCD $8 VSTEST $40 VSORRES $20 VSORRESU $10
           VSSTRESC $20 VSSTRESN 8 VSSTRESU $10 VSBLFL $1
           VISIT $40 VISITNUM 8 VSDY 8;

    set work.vs_raw;
    retain VSSEQ;
    by USUBJID VSTESTCD VISITNUM;

    STUDYID = "&studyid";
    DOMAIN  = "VS";

    /* Sequence number per subject */
    if first.USUBJID then VSSEQ = 0;
    VSSEQ = VSSEQ + 1;

    /* Baseline flag */
    if VSBLFL = "" and VISITDY <= 0 then VSBLFL = "Y";

    /* Study day */
    VSDY = VISITDY;

    keep STUDYID DOMAIN USUBJID VSSEQ VSTESTCD VSTEST
         VSORRES VSORRESU VSSTRESC VSSTRESN VSSTRESU VSBLFL
         VISIT VISITNUM VSDY VISITDY VSDTC;
run;

/* --- Apply labels --- */
proc datasets library=sdtm nolist;
    modify vs;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              VSSEQ    = "Sequence Number"
              VSTESTCD = "Vital Signs Test Short Name"
              VSTEST   = "Vital Signs Test Name"
              VSORRES  = "Result in Original Units"
              VSORRESU = "Original Units"
              VSSTRESC = "Character Result in Standard Units"
              VSSTRESN = "Numeric Result in Standard Units"
              VSSTRESU = "Standard Units"
              VSBLFL   = "Baseline Flag"
              VISIT    = "Visit Name"
              VISITNUM = "Visit Number"
              VSDY     = "Study Day of Vital Signs";
run; quit;

/* --- Export to transport file --- */
%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/vs.xpt);
filename xout "path/to/output/vs.xpt";
libname  xout xport;
data xout.vs;
    set sdtm.vs;
run;
libname xout clear;
filename xout clear;
