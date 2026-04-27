/* ================================================================
   SDTM AE Domain Creation Program
   Study: CDISCPilot01
   Domain: AE (Adverse Events)
   Standard: SDTM IG v3.1.2, MedDRA v8.0
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw adverse event data --- */
data work.ae_raw;
    set raw.ae;
run;

/* --- Derive SDTM AE variables --- */
proc sort data=work.ae_raw; by USUBJID AESTDTC; run;

data sdtm.ae;
    length STUDYID $12 DOMAIN $2 USUBJID $11 AESEQ 8
           AETERM $100 AELLT $100 AEDECOD $100
           AEHLT $100 AEHLGT $100 AEBODSYS $100
           AESEV $20 AESER $1 AEACN $30 AEREL $20
           AEOUT $30 AESTDTC $20 AEENDTC $20;

    retain AESEQ;
    by USUBJID AESTDTC;

    /* Core identifiers */
    STUDYID = "&studyid";
    DOMAIN  = "AE";

    /* Sequence number per subject */
    if first.USUBJID then AESEQ = 0;
    AESEQ = AESEQ + 1;

    /* Reported term from CRF */
    AETERM = strip(AETERM_RAW);

    /* MedDRA coding hierarchy (v8.0) */
    AELLT   = strip(LLT_RAW);
    AEDECOD = strip(PT_RAW);
    AEHLT   = strip(HLT_RAW);
    AEHLGT  = strip(HLGT_RAW);
    AEBODSYS = strip(SOC_RAW);

    /* Severity from CRF */
    AESEV = strip(AESEV_RAW);

    /* Seriousness flag: derived from seriousness criteria */
    if AESCAN_RAW = "Y" or AESCONG_RAW = "Y" or AESDEATH_RAW = "Y"
       or AESHOSP_RAW = "Y" or AESLIFE_RAW = "Y" or AESOD_RAW = "Y"
    then AESER = "Y";
    else AESER = "N";

    /* Action taken, causality, outcome from CRF */
    AEACN = strip(AEACN_RAW);
    AEREL = strip(AEREL_RAW);
    AEOUT = strip(AEOUT_RAW);

    /* Dates in ISO 8601 format */
    AESTDTC = strip(put(AESTDT, is8601da.));
    AEENDTC = strip(put(AEENDT, is8601da.));

    keep STUDYID DOMAIN USUBJID AESEQ AETERM AELLT AEDECOD
         AEHLT AEHLGT AEBODSYS AESEV AESER AEACN AEREL
         AEOUT AESTDTC AEENDTC AESCAN AESCONG AESDEATH
         AESHOSP AESLIFE AESOD;
run;

/* --- Apply variable labels --- */
proc datasets library=sdtm nolist;
    modify ae;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              AESEQ    = "Sequence Number"
              AETERM   = "Reported Term for the Adverse Event"
              AELLT    = "Lowest Level Term"
              AEDECOD  = "Dictionary-Derived Term"
              AEHLT    = "High Level Term"
              AEHLGT   = "High Level Group Term"
              AEBODSYS = "Body System or Organ Class"
              AESEV    = "Severity/Intensity"
              AESER    = "Serious Event"
              AEACN    = "Action Taken with Study Treatment"
              AEREL    = "Causality"
              AEOUT    = "Outcome of Adverse Event"
              AESTDTC  = "Start Date/Time of Adverse Event"
              AEENDTC  = "End Date/Time of Adverse Event";
run; quit;

/* --- Export to transport file --- */
proc export data=sdtm.ae
    outfile="path/to/output/ae.xpt"
    dbms=xport replace;
run;
