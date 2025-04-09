bestfirst_optimal = pd.DataFrame(get_result(VERSION, 'bestfirst_optimal.json')).sort_values('n_click')
bestfirst_random = pd.DataFrame(get_result(VERSION, 'bestfirst_random.json')).sort_values('n_click')
pdf['best_first'] = load_cf('Human').query('~is_term').groupby('wid').is_best.mean()
bestfirst_optimal.sort_values('cost')

fit_best_opt = load_cf('OptimalPlusPure').query('~is_term').groupby('wid').is_best.mean()
rand_best = load_cf('Random').query('~is_term').groupby('wid').is_best.mean()
# fit_best_opt = load_cf('Best_Satisfice_BestNext').query('~is_term').groupby('wid').is_best.mean()
# %% ==================== plots ====================

@figure()
def plot_best_first_only():    
    plt.figure(figsize=(4,4))
    pdf.best_first.plot.hist(bins=np.linspace(0,1,11), color=palette['Human'])
    plt.xlabel('Proportion of Clicks on Best Path')

# %% --------
@figure()
def plot_best_first():    
    plt.figure(figsize=(4,4))
    pdf.best_first.plot.hist(bins=np.linspace(0,1,11), color=palette['Human'])
    plt.axvline(fit_best_opt.mean(), color=palette['Optimal'], linestyle='--')
    plt.axvline(rand_best.mean(), color=palette['Random'], linestyle='--')
    plt.xlabel('Proportion of Clicks on Best Path')

# %% --------
@figure()
def plot_best_first():    
    plt.figure(figsize=(4,4))
    x = np.arange(1,len(pdf)+1)
    plt.scatter(x, pdf.best_first.sort_values().values, color=palette['Human'], s=10)
    plt.axhline(fit_best_opt.mean(), color=palette['Optimal'], lw=3)
    plt.axhline(rand_best.mean(), color=palette['Random'], lw=3)
    plt.axhline(1, color=palette['Best'], lw=3)
    plt.ylabel('Proportion of Clicks on Best Path')
    plt.xlabel('Participant')
    plt.xticks((1, len(pdf)+1))

# %% --------
@figure()
def plot_best_first():    
    plt.figure(figsize=(4,4))
    # bestfirst_optimal.best_first.plot()
    plt.axhline(rand_best.mean(), color=palette['Random'], lw=3, zorder=-1)
    plt.axhline([1], label='BestFirst', color=palette['Best'], lw=3, zorder=-1)
    x = bestfirst_optimal.query('0 < cost < 50')
    plt.scatter(x.cost, x.best_first, label="Optimal", color=palette["Optimal"], s=10, alpha=1)


    plt.scatter(np.ones(len(pdf)), pdf.best_first.sort_values().values, color=palette['Human'], s=10, alpha=0)
    
    plt.ylabel('Proportion of Clicks on Best Path')
    plt.xlabel('Node Expansion Cost')
    # plt.xlabel('Participant')
    

# %% --------

@figure()
def best_first_by_clicks(ax=None):
    if ax is None:
        plt.figure(figsize=(4,4))
    else:
        plt.sca(ax)

    plt.axhline([1], label='BestFirst', color=palette['Best'], lw=3)
    x = bestfirst_optimal.query('0 < cost < 50')
    plt.plot(x.n_click, x.best_first, label="Optimal", color=palette["Optimal"], lw=3, alpha=0.8)
    plt.plot(bestfirst_random.n_click, bestfirst_random.best_first, label="Random", color=palette["Random"], lw=3, alpha=0.8)
    
    plt.scatter('n_click', 'best_first', data=pdf, color=palette["Human"], label='Human', s=10)


    plt.ylabel('Proportion of Clicks on Best Path')
    plt.xlabel('Number of Clicks per Trial')
    plt.xlim(-0.5,15.5)
    plt.ylim(0.48, 1.02)


# %% ==================== stats ====================
from scipy.stats import spearmanr
from statsmodels.stats.proportion import proportion_confint


@do_if(EXPERIMENT == 1)
def this():
    x = load_cf('Human').query('~is_term')
    bf_rate = x.groupby('wid').is_best.mean()
    bf_rand_rate = x.groupby('wid').p_best_rand.mean()

    write_tex("best_first", f'{100*bf_rate.mean():.1f}\\%')
    write_tex("best_first_random", rf"{bf_rand_rate.mean() * 100:.1f}\%" )

    # from statsmodels.stats.proportion import proportions_ztest
    # r = load_cf('Random').query('not is_term').is_best
    # h = x.is_best

    lo, hi = bootstrap_confint(100*bf_rate)
    write_tex(f'best_first_ci', f'95\\% CI [{lo:.1f}, {hi:.1f}]')
    
    p = wilcoxon(bf_rate - bf_rand_rate).pvalue
    z = abs(scipy.stats.norm.ppf(p/2))
    write_tex(f'best_first_wilcoxon', f'$z = {z:.2f}, {pval(p)}$')

    # z, p = proportions_ztest([h.sum(), r.sum()], [len(h), len(r)], alternative='larger')
    # write_tex("best_first_test", rf"$z={z:.1f},\ {pval(p)}$")

    def get_cor(wids):
        r, p = spearmanr(bf_rate[wids], pdf.n_click[wids])
        return r

    r, p = spearmanr(bf_rate[pdf.index], pdf.n_click)
    lo, hi = bootstrap_confint(pdf.reset_index().wid, get_cor)
    write_tex('best_first_click', fr'$\rho={r:.3f}$, 95\% CI [{lo:.2f}, {hi:.2f}], ${pval(p)}$')


    corrected_bf_rate = bf_rate - bf_rand_rate
    def get_cor_corrected(wids):
        r, p = spearmanr(corrected_bf_rate[wids], pdf.n_click[wids])
        return r

    r, p = spearmanr(corrected_bf_rate[pdf.index], pdf.n_click)    
    lo, hi = bootstrap_confint(pdf.reset_index().wid, get_cor_corrected)
    # write_tex('best_first_click_corrected', fr'$\rho={r:.3f}$, 95\% CI [{lo:.2f}, {hi:.2f}], ${pval(p)}$')

# # %% ==================== correct for random ====================

def linear_interpolate(x1, x2, y1, y2, x):
    assert x1 < x < x2
    d = (x - x1) / (x2 - x1)
    return y1 + d * (y2 - y1)

def get_closest(row, comp, xvar, yvar):
    comp = comp.sort_values(xvar)
    x_diff = (comp[xvar] - row[xvar]).values
    cross_point = (x_diff > 0).argmax()
    
    if cross_point == 0:
        o = comp.iloc[0]
        assert row[xvar] > o[xvar]
        return o[yvar]
    else:
        assert x_diff[cross_point - 1] < 0
        o = comp.iloc[cross_point-1:cross_point+1]
        return linear_interpolate(*o[xvar], *o[yvar], row.n_click)

@do_if(EXPERIMENT == 1)
def this():
    rand_best = pdf.apply(get_closest, axis=1, comp=bestfirst_random, xvar='n_click', yvar='best_first')
    corrected = pdf.best_first - rand_best

    def get_cor(wids):
        r, p = spearmanr(corrected[wids], pdf.n_click[wids])
        return r

    r, p = spearmanr(corrected, pdf.n_click)
    lo, hi = bootstrap_confint(pdf.reset_index().wid, get_cor)
    write_tex('best_first_click_corrected', fr'$\rho={r:.3f}$, 95\% CI [{lo:.2f}, {hi:.2f}], ${pval(p)}$')

