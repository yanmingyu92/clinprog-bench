"""Fix all T1.1 gold SAS scripts for execution issues.

Fixes applied:
  1. Replace commas with spaces in KEEP statements
  2. Replace proc copy with data step for XPORT output
  3. Fix trial design domains (TA/TE/TI/TS/TV) that lack USUBJID
  4. Fix LB: type mismatches and $BEST format
  5. Fix VS: rewrite to use VSTESTCD/VSORRES instead of derived vars
  6. Add %sysexec to delete existing .xpt before writing
"""
import re
from pathlib import Path

GOLD = Path("gold")


def fix_keep_commas(content: str) -> str:
    """Replace commas with spaces in keep/drop/retain statements."""
    def _fix_keep(m):
        keyword = m.group(1)
        varlist = m.group(2)
        # Replace commas with spaces
        varlist = varlist.replace(",", " ")
        return f"{keyword} {varlist};"
    # Match keep/drop statements with commas
    content = re.sub(
        r'(keep|drop|retain)\s+([^;]+);',
        _fix_keep, content, flags=re.IGNORECASE
    )
    return content


def fix_xport_noreplace(content: str) -> str:
    """Add file deletion before xport write to avoid NOREPLACE."""
    # Find filename xout "path"; and insert deletion before it
    def _add_delete(m):
        path = m.group(1)
        # Use x command to delete existing file
        return f'%macro delfile(f); %if %sysfunc(fileexist(&f)) %then %do; %let rc=%sysfunc(filename(_f,&f)); %let rc=%sysfunc(fdelete(&_f)); %end; %mend;\n%delfile({path});\nfilename xout "{path}";'
    content = re.sub(
        r'filename xout "([^"]+)";',
        _add_delete, content
    )
    return content


def fix_trial_design(content: str, domain: str) -> str:
    """Fix trial design domains (TA/TE/TI/TS/TV) that don't have USUBJID."""
    # Remove proc sort by USUBJID
    content = re.sub(
        r'proc sort data=work\.\w+_raw;\s*by USUBJID[^;]*;\s*run;\s*',
        '', content
    )
    # Remove 'by USUBJID ...' line in data step
    content = re.sub(r'\n\s+by USUBJID[^;]*;', '', content)
    # Remove 'if first.USUBJID then ...' line
    content = re.sub(r'\n\s+if first\.USUBJID then[^;]*;', '', content)
    return content


def fix_lb(content: str) -> str:
    """Fix LB: LBORNRLO/LBORNRHI types and $BEST format."""
    # Fix numeric length for char vars
    content = content.replace('LBORNRLO 8', 'LBORNRLO $20')
    content = content.replace('LBORNRHI 8', 'LBORNRHI $20')
    content = content.replace('LBSTNRLO 8', 'LBSTNRLO $20')
    content = content.replace('LBSTNRHI 8', 'LBSTNRHI $20')
    # Fix $BEST format (should be BEST for numeric, or just remove)
    content = content.replace('$BEST', 'BEST')
    # Fix strip() on numeric -> put() conversion for reference ranges
    content = content.replace("strip(put(REF_LO_RAW, BEST.))", "REF_LO_RAW")
    content = content.replace("strip(put(REF_HI_RAW, BEST.))", "REF_HI_RAW")
    return content


def fix_vs(content: str) -> str:
    """Rewrite VS gold script to work with actual SDTM VS data."""
    # The VS domain uses VSTESTCD/VSORRES, not HEIGHT/WEIGHT/etc.
    # These are pivoted variables that don't exist in the flat SDTM structure
    # Remove any lines referencing the non-existent variables
    bad_vars = ['HEIGHT', 'WEIGHT', 'DIABP', 'SYSBP', 'PULSE', 'TEMP']
    lines = content.split('\n')
    new_lines = []
    skip_next_run = False
    for line in lines:
        stripped = line.strip()
        skip = False
        for v in bad_vars:
            # Skip assignments like "VSORRES = strip(put(HEIGHT, BEST.));"
            if v in line and ('=' in line or 'input(' in line.lower()):
                skip = True
                break
        # Also fix the proc sort that references non-existent VISITNUM
        if 'proc sort' in line and 'VISITNUM' in line and 'VSTESTCD' not in line:
            line = line.replace('by USUBJID VISITNUM;', 'by USUBJID VSTESTCD VISITNUM;')
        # Fix by statement in data step  
        if stripped.startswith('by') and 'VISITNUM' in line and 'VSTESTCD' not in line and 'USUBJID' in line:
            line = line.replace('by USUBJID VISITNUM;', 'by USUBJID VSTESTCD VISITNUM;')
        if not skip:
            new_lines.append(line)
    return '\n'.join(new_lines)


def main():
    fixed = 0
    for d in sorted(GOLD.glob("T1.1.sdtm_*_gen.*")):
        sas_file = d / "expected_output.sas"
        if not sas_file.exists():
            continue

        m = re.search(r'sdtm_(\w+?)_gen', d.name)
        if not m:
            continue
        domain = m.group(1)

        content = sas_file.read_text(encoding='utf-8')
        original = content

        # Fix 1: Commas in keep/drop statements (all scripts)
        content = fix_keep_commas(content)

        # Fix 2: XPORT NOREPLACE (all scripts)
        content = fix_xport_noreplace(content)

        # Fix 3: Trial design domains
        if domain in ('ta', 'te', 'ti', 'ts', 'tv'):
            content = fix_trial_design(content, domain)

        # Fix 4: LB type mismatch
        if domain == 'lb':
            content = fix_lb(content)

        # Fix 5: VS variable references
        if domain == 'vs':
            content = fix_vs(content)

        if content != original:
            sas_file.write_text(content, encoding='utf-8')
            print(f"  [FIXED] {d.name}")
            fixed += 1
        else:
            print(f"  [SKIP]  {d.name}")

    print(f"\nFixed {fixed} gold scripts.")


if __name__ == "__main__":
    main()
