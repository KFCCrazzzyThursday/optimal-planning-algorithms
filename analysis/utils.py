import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from glob import glob
import json

from scipy.stats import wilcoxon

matplotlib.use('Agg')
sns.set_context('notebook', font_scale=1.3)
sns.set_style('white')

def bootstrap_confint(x, f=np.mean, ci=.95, N=10000):
    lo = (1-ci)/2
    hi = 1 - lo
    vals = [f(x.sample(frac=1, replace=True)) for i in range(N)]
    return np.quantile(vals, [0.025, 0.975])

def str_join(args, sep=' '):
    return sep.join(map(str, args))

def load_json(path):
    with open(path) as f:
        return json.load(f)

def get_result(version, name):
    return load_json(f'../model/results/{version}/{name}')

def mean_std(x, digits=1, fmt=None):
    mean = x.mean()
    std = x.std()
    if fmt == 'pct':
        x = x * 100
        return fr'{mean:.{digits}f}\% $\pm$ {std:.{digits}f}\%'
    elif fmt == '$':
        return fr'\${mean:.2f} $\pm$ \${std:.2f}'
    else:
        return fr'{mean:.{digits}f} $\pm$ {std:.{digits}f}'

def load_data(exp):
    tdf = pd.read_pickle(f'../data/{exp}/trials.pkl').query('block == "test"')
    pdf = pd.read_pickle(f'../data/{exp}/participants.pkl')
    pdf.rename(columns={'clickDelay': 'click_delay'}, inplace=True)
    tdf['click_delay'] = pdf['click_delay'] = pdf.click_delay.apply(lambda x: str(x/1000)+'s')
    if 'variance' not in pdf:
        pdf['variance'] = 'constant'
    if 'trial_id' in tdf:
        tdf['mdp'], tdf['trial_id'] = tdf.trial_id.str.split('-', expand=True).values.T
    tdf['variance'] = pdf.variance
    tdf['n_click'] = tdf.clicks.apply(len)

    for k in ['n_click', 'score']:
        pdf[k] = tdf[k].groupby('wid').mean()
    
    return pdf, tdf

def load_fits(exp, models, path='mle'):
    cv_fits = pd.concat([pd.read_csv(f'../model/results/{exp}/{path}/{model}-cv.csv') 
                         for model in models], sort=False)
    fits = pd.concat([pd.read_csv(f'../model/results/{exp}/{path}/{model}.csv')
                      for model in models], sort=False)
    fits.set_index(['model', 'wid'], inplace=True)
    fits['cv_nll'] = cv_fits.groupby(['model', 'wid']).test_nll.sum()
    fits['overfitting'] = fits.cv_nll - fits.nll
    return fits.reset_index()


# keeps the global namespace clean
def do_if(cond):
    def wrapper(f):
        if cond:
            f()
    return wrapper


from datetime import datetime
class Figures(object):
    """Plots and saves figures."""
    def __init__(self, path='figs', hist_path='fighist', pdf=True, dpi=200):
        self.path = path
        self.hist_path = hist_path
        self.dpi = dpi
        self.pdf = pdf
        self.names = {}
        self._last = None
        self.nosave = False

        os.makedirs(path, exist_ok=True)
        os.makedirs(hist_path, exist_ok=True)

    def add_names(self, names):
        self.names.update(names)

    def nice_name(self, name):
        return self.names.get(name, name.title())

    def open(self):
        latest = max(glob(f'fighist/*'), key=os.path.getctime)
        os.system(f'open {latest}')

    def reformat_labels(self, ax=None):
        if ax is None:
            ax = plt.gca()
        ax.set_ylabel(self.nice_name(ax.get_ylabel()))
        ax.set_xlabel(self.nice_name(ax.get_xlabel()))

    def reformat_ticks(self, yaxis=False, ax=None):
        if ax is None:
            ax = plt.gca()
        if yaxis:
            labels = [t.get_text() for t in ax.get_yticklabels()]
            new_labels = [self.nice_name(lab) for lab in labels]
            ax.set_yticklabels(new_labels)
        else:
            labels = [t.get_text() for t in ax.get_xticklabels()]
            new_labels = [self.nice_name(lab) for lab in labels]
            ax.set_xticklabels(new_labels)
        
    def reformat_legend(self, ax=None, legend_kws={}, **kws):
        if ax is None:
            ax = plt.gca()
        if ax.legend_:
            handles, labels = ax.get_legend_handles_labels()
            print(labels)
            names = {**self.names, **kws}
            new_labels = [names.get(l, l.title()).replace('\n', ' ') for l in labels]
            ax.legend(handles=handles, labels=new_labels, frameon=False, prop={'size': 12}, **legend_kws)

    def watch(self):
        from watcher import Watcher
        if hasattr(self, 'watcher'):
            self.watcher.start()
        self.watcher = Watcher(self.hist_path)

    def show(self, name='tmp', pdf=None, tight=True, reformat_labels=False, reformat_legend=False, despine=True):
      if pdf is None:
        pdf = self.pdf
        try:
            if tight:
                plt.tight_layout()
            if reformat_labels:
                self.reformat_labels()
            if reformat_legend:
                self.reformat_legend()
            if despine:
                sns.despine()

            dt = datetime.now().strftime('%m-%d-%H-%M-%S')
            p = f'{dt}-{name}.png'
            tmp = f'{self.hist_path}/{p}'
            if self.nosave:
                return

            plt.savefig(tmp, dpi=self.dpi, bbox_inches='tight')

            if name != 'tmp':
                name = name.lower()
                if pdf:
                    plt.savefig(f'{self.path}/{name}.pdf', bbox_inches='tight')
                else:
                    os.system(f'cp {tmp} {self.path}/{name}.png')
        finally:
            plt.close('all')

    def figure(self, run=True, **kwargs):
        """Decorator that calls a plotting function and saves the result."""
        def decorator(func):
            name = func.__name__
            if run:
                if name.startswith('plot_'):
                    name = name[len('plot_'):].lower()
                try:
                    plt.figure()
                    func()
                    self.show(name, **kwargs)
                finally:
                    plt.close('all')
            return func
        return decorator

def plot_params(fits):
    d = fits.query('model == "BestFirst"')
    betas = ['β_depth', 'β_sat', 'β_lead', 'β_click']
    thetas = ['θ_depth', 'θ_sat', 'θ_lead']
    params = [*betas, *thetas, 'ε']
    upper = [3, 3, 3, 3, 4, 30, 30, 1]
    X = d[params] / upper
    X = X[betas]
    X.T.plot(legend=False, color='k', alpha=0.4)


def pval(x):
    if x < 0.001:
        return r"p < .001"
    else:
        assert x < 1
        p = f'{x:.3f}'[1:]
        return f"p = {p}"

class TeX(object):
    """Saves tex files."""
    def __init__(self, path='stats', clear=False):
        self.path = path
        if clear:
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)


    def write(self, name, tex):
        file = f"{self.path}/{name}.tex"
        with open(file, "w+") as f:
            f.write(str(tex) + r"\unskip")
        print(f'wrote "{tex}" to "{file}"')

from scipy.stats import ttest_rel
def paired_ttest(x, y):
    t, p = ttest_rel(x, y)
    df = len(x) - 1
    return f"$t({df}) = {t:.3f}, {pval(p)}$"


# def load_data_multi(codes):
#     pdfs, tdfs = zip(*map(load_data, codes))
#     return pd.concat(pdfs, sort=False), pd.concat(tdfs, sort=False)

# mx = 'DepthFirst'; my = 'BestFirst'
# d = fits.query('variance == "increasing"')
# x = d.groupby(['wid', 'model']).nll.mean().reset_index().set_index('model').nll
# plt.scatter(x.loc[mx], x.loc[my])
# plt.plot([0, 400], [0, 400])
# plt.xlabel(f'{mx} NLL')
# plt.ylabel(f'{my} NLL')