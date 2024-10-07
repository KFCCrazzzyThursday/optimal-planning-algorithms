all: generate sync

generate:
	ipython -c "`cat exp1.py`"
	ipython -c "`cat exp2.py`"
	ipython -c "`cat exp3.py`"
	ipython -c "`cat exp4.py`"
	ipython -c "`cat exp5.py`"
	Rscript glmer.r

sync:
# 	rsync -av figs/main/ ~/Papers/planning-as-information/figs
	rsync --exclude main -av figs/ ~/Papers/planning-as-information/figs/supp
	rsync -av stats/ ~/Papers/planning-as-information/stats/
