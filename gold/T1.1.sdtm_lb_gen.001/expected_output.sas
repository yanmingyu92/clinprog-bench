/* ================================================================
   SDTM LB Domain Creation Program
   Study: CDISCPilot01
   Domain: LB (Laboratory Test Results)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw lab data --- */
data work.lb_raw;
    set raw.lb;
run;

/* --- Map test codes and standardize units --- */
data work.lb_mapped;
    set work.lb_raw;

    length LBTESTCD $8 LBTEST $40 LBORRES $200 LBORRESU $40
           LBSTRESC $200 LBSTRESN 8 LBSTRESU $40
           LBORNRLO $200 LBORNRHI $200;

    /* CDISC controlled terminology mapping */
    select (LBTEST_RAW);
        when ("Sodium")       LBTESTCD = "SODIUM";
        when ("Potassium")    LBTESTCD = "K";
        when ("Chloride")     LBTESTCD = "CL";
        when ("Glucose")      LBTESTCD = "GLUC";
        when ("BUN")          LBTESTCD = "BUN";
        when ("Creatinine")   LBTESTCD = "CREAT";
        when ("Albumin")      LBTESTCD = "ALB";
        when ("Total Protein") LBTESTCD = "TP";
        when ("ALT")          LBTESTCD = "ALT";
        when ("AST")          LBTESTCD = "AST";
        when ("Alkaline Phos") LBTESTCD = "ALKPH";
        when ("Total Bilirubin") LBTESTCD = "BILI";
        when ("Hemoglobin")   LBTESTCD = "HGB";
        when ("WBC")          LBTESTCD = "WBC";
        when ("Platelet Count") LBTESTCD = "PLAT";
        otherwise LBTESTCD = "OTHER";
    end;

    LBTEST   = LBTEST_RAW;
    LBORRES  = strip(RESULT_RAW);
    LBORRESU = strip(UNIT_RAW);

    /* Standardize numeric results */
    LBSTRESC = strip(RESULT_RAW);
    LBSTRESN = input(RESULT_RAW, ?? best32.);
    LBSTRESU = strip(UNIT_RAW);

    /* Reference ranges */
    LBORNRLO = REF_LO_RAW;
    LBORNRHI = REF_HI_RAW;

    keep USUBJID VISIT VISITNUM LBTESTCD LBTEST LBORRES LBORRESU
         LBSTRESC LBSTRESN LBSTRESU LBORNRLO LBORNRHI
         LBDTC LBDY;
run;

/* --- Assign sequence numbers --- */
proc sort data=work.lb_mapped; by USUBJID LBTESTCD VISITNUM; run;

data sdtm.lb;
    length STUDYID $12 DOMAIN $2 USUBJID $11 LBSEQ 8;
    set work.lb_mapped;
    by USUBJID LBTESTCD VISITNUM;

    retain LBSEQ;
    if first.USUBJID then LBSEQ = 0;
    LBSEQ = LBSEQ + 1;

    STUDYID = "&studyid";
    DOMAIN  = "LB";
run;

/* --- Labels and export --- */
proc datasets library=sdtm nolist;
    modify lb;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              LBSEQ    = "Sequence Number"
              LBTESTCD = "Lab Test Short Name"
              LBTEST   = "Lab Test Name"
              LBORRES  = "Result in Original Units"
              LBORRESU = "Original Units"
              LBSTRESC = "Character Result in Standard Format"
              LBSTRESN = "Numeric Result in Standard Units"
              LBSTRESU = "Standard Units"
              LBORNRLO = "Reference Range Lower Limit (Original)"
              LBORNRHI = "Reference Range Upper Limit (Original)"
              LBNRNRLO = "Reference Range Lower Limit (Standard)"
              LBNRNRHI = "Reference Range Upper Limit (Standard)";
run; quit;

%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;
%delfile(path/to/output/lb.xpt);
filename xout "path/to/output/lb.xpt";
libname  xout xport;
data xout.lb;
    set sdtm.lb;
run;
libname xout clear;
filename xout clear;
