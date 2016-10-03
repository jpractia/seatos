# Build mean-profiles in icme-sheath

Run:
```bash
# path to input files
export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
# Jan/2006-Dec/2013 version of scalers (hdf5 file)
export SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5
# Jan/2006-Dec/2015 version of scalers (very different hdf5 structure inside!)
export SCLS=$AUGER_REPO/scl.build_final/test.h5
# now execute
./sea_splitted.py -- --ace $ACE --mcmurdo $MURDO --avr $AVR --rich_csv $RICH_CSV --auger_hsts $HSTS --auger_scls $SCLS --dir_plot ../plots3 --dir_data ../ascii3 --suffix _auger_ --icme_flag 0.1.2.2H --struct sh.i
# to reproduce A&A paper
./sea_splitted.py -- --ace $ACE  --mcmurdo 0  --avr $AVR  --rich_csv $RICH_CSV --auger_hsts 0  --auger_scls 0  --dir_plot ./test  --dir_data ./test  --suffix _test_  --icme_flag 2  --struct mc  --wang 1 90.  --Vsplit 450. 550.
```
Note that, you can use `0` for `--ace` and `--mcmurdo`, to avoid processing them.