#!/bin/bash

# output diretory
OUTDIR=$1      # 1st argument
if [[ -d "$OUTDIR" ]]; then
    echo -e "\n [+] output directory ok:\n $OUTDIR\n"
else
    echo -e "\n [-] Directory doesn't exist:\n $OUTDIR\n"
    return 1
fi

# input directories:
# NOTE: the data in these directories was generated by other scripts (for 
# instance, `icmes/src/sea_splitted.py`), which take the spacecraft data and
# filter-in time intervals associated to ICMEs/MCs/sheaths passages.
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_

group=(lo mid hi)
lims=('100. 375.' '375. 450.' '450. 3000.')
EXE=$MEAN_PROFILES_ACE/mixed.icmes/src/splitted.py

#--- splitted profiles
for i in $(seq 0 1 2); do
    OUT=${OUTDIR}/${group[$i]} && mkdir -p $OUT
    # build mixed profile
    $EXE -- --left $LEFT  --right $RIGHT  --plot $OUT  --lim ${lims[$i]}
done

#--- global profiles
OUT=${OUTDIR}/all && mkdir $OUT
# build mixed profile
$EXE -- --left $LEFT  --right $RIGHT  --plot $OUT

#EOF
