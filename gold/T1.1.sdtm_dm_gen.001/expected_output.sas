/* ================================================================
   SDTM DM Domain Creation Program
   Study: CDISCPilot01
   Domain: DM (Demographics)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw demographics data --- */
data work.dm_raw;
    set raw.dm;
run;

/* --- Derive SDTM DM variables --- */
data sdtm.dm;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUBJID $4 SITEID $2
           RFICDTC $20 RFXSTDTC $20 ARMCD $8 ARM $40
           ACTARMCD $8 ACTARM $40 AGE 8 AGEU $10
           SEX $2 RACE $40 ETHNIC $22 COUNTRY $3;

    /* Core identifiers */
    STUDYID = "&studyid";
    DOMAIN  = "DM";

    /* Derive USUBJID: concatenation of STUDYID-SITEID-SUBJID */
    USUBJID = cats(STUDYID, "-", SITEID, "-", SUBJID);

    /* Treatment arm mapping from randomization */
    select (ARMCD_RAW);
        when ("Pbo")    do; ARMCD = "Pbo";    ARM = "Placebo"; end;
        when ("Xan_Lo") do; ARMCD = "Xan_Lo"; ARM = "Xanomeline Low Dose"; end;
        when ("Xan_Hi") do; ARMCD = "Xan_Hi"; ARM = "Xanomeline High Dose"; end;
        when ("Scrnfail") do; ARMCD = "Scrnfail"; ARM = "Screen Failure"; end;
        otherwise do; ARMCD = ""; ARM = ""; end;
    end;

    /* Actual arm = planned arm unless early discontinuation */
    ACTARMCD = ARMCD;
    ACTARM   = ARM;

    /* Age from birth date and reference date */
    AGE = int(yrdif(BRTHDTC, RFICDTC, 'ACTUAL'));

    AGEU = "YEARS";

    /* Demographics from CRF */
    SEX    = SEX_RAW;
    RACE   = RACE_RAW;
    ETHNIC = ETHNIC_RAW;

    /* Country derived from site */
    COUNTRY = "US";

    /* Dates */
    RFICDTC  = put(consent_dt, is8601da.);
    RFXSTDTC = put(first_dose_dt, is8601da.);

    /* Keep only required variables */
    keep STUDYID DOMAIN USUBJID SUBJID SITEID
         RFICDTC RFXSTDTC ARMCD ARM ACTARMCD ACTARM
         AGE AGEU SEX RACE ETHNIC COUNTRY RFICDEC;
run;

/* --- Apply variable labels --- */
proc datasets library=sdtm nolist;
    modify dm;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUBJID   = "Subject Identifier for the Study"
              SITEID   = "Study Site Identifier"
              RFICDTC  = "Date/Time of Informed Consent"
              RFXSTDTC = "Date/Time of First Study Treatment"
              ARMCD    = "Planned Arm Code"
              ARM      = "Description of Planned Arm"
              ACTARMCD = "Actual Arm Code"
              ACTARM   = "Description of Actual Arm"
              AGE      = "Age"
              AGEU     = "Age Units"
              SEX      = "Sex"
              RACE     = "Race"
              ETHNIC   = "Ethnicity"
              COUNTRY  = "Country";
run; quit;

/* --- Export to transport file --- */
filename xout "path/to/output/dm.xpt";
libname  xout xport;
proc copy in=sdtm out=xout;
    select dm;
run;
libname xout clear;
filename xout clear;
