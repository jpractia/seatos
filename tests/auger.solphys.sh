#!/bin/bash
#++++++++++++++++++++++++++++++++++++++++++++
#
# Build mixed time profiles using the output files
# generated by the previous script (auger.splitted.sh).
#
#++++++++++++++++++++++++++++++++++++++++++++

me=`basename "$0"` # name of this script

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
[[ -v LEFT && -v RIGHT ]] \
    && ok=true \
    || ok=false
if [[ ! $ok ]]; then
    # if any of them is not set, set them all:
    echo -e "\n [-] $me: At least one env variable is not present, so"
    echo -e "     we'll set them...\n"
    export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
    export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_
else
    echo -e "\n [+] $me: all needed env variables were parsed to this script!\n"
fi

group=(lo mid hi)
lims=('100. 450.' '450. 550.' '550. 3000.')

#--- splitted profiles
EXE=$MEAN_PROFILES_ACE/mixed.icmes/src/splitted.py
for i in $(seq 0 1 2); do
    OUT=${OUTDIR}/${group[$i]} && mkdir -p $OUT
    # build mixed profile
    $EXE --pdb -- --left $LEFT  --right $RIGHT  --plot $OUT  --lim ${lims[$i]}
done

#--- global profiles
OUT=${OUTDIR}/all && mkdir $OUT
# build mixed profile
$EXE --pdb -- --left $LEFT  --right $RIGHT  --plot $OUT

#EOF
