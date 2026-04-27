/* ================================================================
   SDTM VS Domain Creation Program
   Study: CDISCPilot01
   Domain: VS (Vital Signs)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/03_raw_data" access=readonly;
libname sdtm "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/04_sdtm/datasets";
%let studyid = CDISCPilot01;

/* --- Read raw vital signs data (wide format) --- */
data work.vs_raw;
    set raw.vs;
run;

/* --- Transpose to long format (one row per test per visit) --- */
proc transpose data=work.vs_raw out=vs_long prefix=V;
    by USUBJID VISIT VISITNUM VISITDY;
    var HEIGHT WEIGHT DIABP SYSBP PULSE TEMP;
run;

/* --- Map test codes and standardize --- */
data work.vs_mapped;
    set vs_long;
    length VSTESTCD $8 VSTEST $40 VSORRES $20 VSORRESU $10
           VSSTRESC $20 VSSTRESN 8 VSSTRESU $10 VSBLFL $1
           VSDY 8 VSDY_D 8;

    /* Determine test code from transposed variable name */
    VSTESTCD = scan(_NAME_, 1, "_");

    select (VSTESTCD);
        when ("HEIGHT")
            do; VSTEST = "Height"; VSORRESU = "cm"; VSSTRESU = "cm"; end;
        when ("WEIGHT")
            do; VSTEST = "Weight"; VSORRESU = "kg"; VSSTRESU = "kg"; end;
        when ("DIABP")
            do; VSTEST = "Diastolic Blood Pressure"; VSORRESU = "mmHg"; VSSTRESU = "mmHg"; end;
        when ("SYSBP")
            do; VSTEST = "Systolic Blood Pressure"; VSORRESU = "mmHg"; VSSTRESU = "mmHg"; end;
        when ("PULSE")
            do; VSTEST = "Pulse Rate"; VSORRESU = "BEATS/MIN"; VSSTRESU = "BEATS/MIN"; end;
        when ("TEMP")
            do; VSTEST = "Temperature"; VSORRESU = "C"; VSSTRESU = "C"; end;
        otherwise;
    end;

    /* Original and standardized results */
    VSORRES  = strip(put(COL1, best12.));
    VSSTRESC = strip(put(COL1, best12.));
    VSSTRESN = input(strip(put(COL1, best12.)), 8.);

    /* Baseline flag: last measurement before first dose */
    if VISITDY <= 0 then VSBLFL = "Y";
    else VSBLFL = "";

    keep USUBJID VISIT VISITNUM VISITDY VSTESTCD VSTEST
         VSORRES VSORRESU VSSTRESC VSSTRESN VSSTRESU VSBLFL;
run;

/* --- Create final SDTM VS dataset --- */
proc sort data=work.vs_mapped; by USUBJID VSTESTCD VISITNUM; run;

data sdtm.vs;
    length STUDYID $12 DOMAIN $2 USUBJID $11 VSSEQ 8;
    set work.vs_mapped;
    by USUBJID VSTESTCD VISITNUM;

    retain VSSEQ;
    if first.USUBJID then VSSEQ = 0;
    VSSEQ = VSSEQ + 1;

    STUDYID = "&studyid";
    DOMAIN  = "VS";

    /* Study day relative to first dose */
    VSDY = VISITDY;
run;

/* --- Apply labels and export --- */
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

proc export data=sdtm.vs
    outfile="C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/clinprog-bench/gold/_exec_output/vs.xpt"
    dbms=xport replace;
run;
