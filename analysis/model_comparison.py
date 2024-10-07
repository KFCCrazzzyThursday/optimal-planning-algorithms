# %% ==================== Load predictions ====================

def get_fits():
    models = get_result(VERSION, "param_counts.json").keys()
    fits = load_fits(VERSION, models).set_index('wid')
    fits['variance'] = pdf.variance
    # fits['n_act'] = load_cf('Human').index.value_counts()
    # fits['geometric_like'] = np.exp(fits.cv_nll / fits.n_act)
    assert set(fits.index) == set(pdf.index)
    return fits.reset_index().set_index(['variance', 'wid'])

fits = get_fits()
n_act = load_cf('Human').variance.value_counts()
totals = fits.groupby(['variance', 'model']).cv_nll.sum().reset_index('model')
assert np.isfinite(totals.cv_nll).all()

if len(n_act) == 1:
    # Pandas can't figure this out for some reason...
    avg_nll = totals.cv_nll / float(n_act)
else:
    avg_nll = totals.cv_nll / n_act

totals['geometric_like'] = list(np.exp(-avg_nll))
geometric_like = totals.reset_index().set_index(['variance', 'model']).geometric_like

totals.query('model != "OptimalPlus"').reset_index().set_index('model').groupby('variance').geometric_like.idxmax()
# %% ==================== Choose models to plot ====================

BASIC = ['Random', 'MetaGreedy', 'OptimalPlus']
HEURISTICS = ['Breadth', 'Depth', 'Best']
MECHANISMS = ['Satisfice', 'BestNext']

if EXPERIMENT >= 3:
    MECHANISMS.append('Expand')
else:
    MECHANISMS.extend(['DepthLimit', 'Prune'])

COMPARISON_MODELS = list(BASIC)


avg_across_variance = geometric_like.groupby(['model']).mean()
best_heuristic = [
    avg_across_variance.filter(regex=f'^{model_class}(_Satisfice)?(_BestNext)?(_DepthLimit)?(_Prune)?(_Expand)?$').idxmax()
    for model_class in HEURISTICS
]
best_heuristic_no_expand = [
    avg_across_variance.filter(regex=f'^{model_class}(_Satisfice)?(_BestNext)?(_DepthLimit)?(_Prune)?$').idxmax()
    for model_class in HEURISTICS
]
best_heuristic_no_depthlimit = [
    avg_across_variance.filter(regex=f'^{model_class}(_Satisfice)?(_BestNext)?(_Prune)?$').idxmax()
    for model_class in ['Breadth', 'Depth', 'Best']
]
best_heuristic_no_depthlimit_noprune = [
    avg_across_variance.filter(regex=f'^{model_class}(_Satisfice)?(_BestNext)?$').idxmax()
    for model_class in ['Breadth', 'Depth', 'Best']
]

if EXPERIMENT == 1:
    COMPARISON_MODELS.extend(best_heuristic)
    COMPARISON_MODELS.extend([
        # 'Best_BestNext_DepthLimit',
        'Best_Satisfice_BestNext_DepthLimit_Prune',
        'Best_BestNext',
        'Best_Satisfice',
        'Best_DepthLimit',
        'Best_Prune',
        'Best'
    ])
elif EXPERIMENT == 2:
    COMPARISON_MODELS.extend(best_heuristic_no_depthlimit)
else: # 3 and 4
    COMPARISON_MODELS.extend(['Expand', 'MetaGreedyExpand', 'OptimalPlusExpand'])
    COMPARISON_MODELS.extend(best_heuristic)
    COMPARISON_MODELS.extend(best_heuristic_no_expand)
    # no_expand = [m.replace('_Expand', '') for m in best_heuristic]
    # COMPARISON_MODELS.extend(no_expand)
    # COMPARISON_MODELS.extend(m + '_Expand' for m in no_expand)

# %% ==================== Plots ====================
label = 'Geometric Mean\nLikelihood'

def plot_like_horizontal(axes=None):
    if axes is None:
        fig, axes = setup_variance_plot()
    for i, v in enumerate(VARIANCES):
        plt.sca(axes.flat[i])
        pal = [palette[m] for m in COMPARISON_MODELS]
        geometric_like.loc[v].loc[COMPARISON_MODELS].plot.barh(color=pal)

        plt.xlabel(label.replace('\n', ' '))
        plt.ylabel('')
        if i != 0:
            plt.yticks(())
    figs.reformat_ticks(yaxis=True, ax=axes.flat[0])

def plot_like_vertical(ax=None):
    if ax is None:
        plt.figure(figsize=(8,4))
        ax = plt.gca()
    else:
        plt.sca(ax)
    pal = [palette[m] for m in COMPARISON_MODELS]
    for i in range(6, len(pal)):
        pal[i] = lg

    geometric_like.loc['constant'].loc[COMPARISON_MODELS].plot.bar(color=pal)

    plt.xticks(rotation=35, ha="right")
    figs.reformat_ticks()
    plt.ylabel(label)
    plt.xlabel('')

def plot_like_expansion(axes=None):
    # L = L.groupby('variance').mean()
    if axes is None:
        if EXPERIMENT == 4:
            fig, axes = plt.subplots(1, 1, figsize=(6,4), squeeze=False)
        else:
            fig, axes = setup_variance_plot()
    
    top_models = [m for m in COMPARISON_MODELS if not m.endswith('Expand')]
    bottom_models = [m for m in COMPARISON_MODELS if m.endswith('Expand')]
    # del top_models[0]

    for i, v in enumerate(VARIANCES):
        plt.sca(axes.flat[i])

        for models in [bottom_models, top_models]:
            pal = [palette[m] for m in models]
            ax = geometric_like.loc[v].loc[models].plot.barh(color=pal)

        plt.ylabel('')
        plt.xlabel(label.replace('\n', ' '))
        if i == 0:
            figs.reformat_ticks(yaxis=True)
        else:
            plt.yticks(())

@figure()
def plot_geometric_mean_likelihood(axes=None):
    if EXPERIMENT == 1:
        return plot_like_vertical(axes)
    elif EXPERIMENT == 2:
        return plot_like_horizontal(axes)
    if EXPERIMENT >= 3:
        return plot_like_expansion(axes)


# %% ==================== Stats ====================

def get_best_with_delta(lp):
    top2 = lp.sort_values(ascending=False).iloc[:2]
    return top2.index[0], top2.iloc[0] - top2.iloc[1]

def fmt_min_delta(x):
    assert x > 0
    return rf'all $\dnll > {np.floor(x):.0f}$'

# This is like "if EXPERIMENT == 1:" except it doesn't pollute the global namespace
@do_if(EXPERIMENT == 1)
def this():
    ll = -totals.set_index('model').cv_nll # total log likelihood for each model
    opt = ll.OptimalPlus
    no_opt = ll.drop('OptimalPlus')
    no_fancy = no_opt.loc[~no_opt.index.str.contains('Prob')]

    no_best = no_fancy.loc[~no_fancy.index.str.startswith('Best')]
    write_tex('dnll_no_best', fmt_min_delta(opt - no_best.max()))

    no_best_next = no_fancy.loc[~no_fancy.index.str.contains('BestNext')]
    write_tex('dnll_no_bestnext', fmt_min_delta(opt - no_best_next.max()))

    write_tex('dnll_no_fancy', fmt_min_delta(opt - no_fancy.max()))

    write_tex('dnll_full', rf'$\dnll = {opt - no_opt.max():.0f}$')

    write_tex('dnll_fancy', rf'$\dnll = {no_opt.max() - no_fancy.max():.0f}$')

    no_probbest = no_opt.loc[~no_opt.index.str.contains('ProbBest')]
    
    assert no_fancy.idxmax() == 'Best_Satisfice_BestNext_DepthLimit'
    delta = ll.Best_Satisfice_BestNext_DepthLimit_Prune - ll.Best_Satisfice_BestNext_DepthLimit
    write_tex('dnll_prune', rf'$\dnll = {delta:.0f}$')

    THRESHOLD = np.log(100)
    def_better = ll - ll.OptimalPlus > THRESHOLD
    def_worse = ll - ll.OptimalPlus < -THRESHOLD

    # write_tex('min_dnll_plot', f'{ll[COMPARISON_MODELS].sort_values().diff().min():.0f}')
    if ll[COMPARISON_MODELS].sort_values().diff().min() < THRESHOLD:
        print("ERROR: warn_small_dnll")
        write_tex('warn_small_dnll', r'\red{WARNING: SMALL DIFFERENCE IN LIKELIHOOD}')
    else:
        write_tex('warn_small_dnll', '')

    all_fits = {
        'no_fancy': fits.loc[~fits.model.str.contains('Prob')],
        'no_probbest': fits.loc[~fits.model.str.contains('ProbBest')],
        'full': fits
    }
    for key, the_fits in all_fits.items():
        best_fit = the_fits.reset_index().pivot('model', 'wid', 'cv_nll').idxmin()
        pdf['best_fit'] = best_fit
        pdf['best_fit_class'] = best_fit.apply(lambda x: x.split('_')[0])
        pdf.groupby('variance').best_fit_class.value_counts()
        nbf = best_fit.apply(lambda x: x.split('_')[0]).value_counts()

        write_tex(f'nfit_best_{key}', nbf.Best)
        write_tex(f'nfit_optimal_{key}', nbf.OptimalPlus)
        write_tex(f'nfit_other_{key}', nbf.drop(['Best', 'OptimalPlus']).sum())

    all_models = all_fits['full'].model.unique()
    x = the_fits.reset_index().set_index(['model', 'wid']).cv_nll
    better = (x.loc['OptimalPlus'] - x) > 0
    better.groupby('model').sum().sort_values()
    n_better = int(better.groupby('model').sum().max())
    write_tex(f'nfit_beat_opt', f'{n_better} vs. {len(pdf) - n_better}')


@do_if(EXPERIMENT == 2)
def this():
    # ll = totals.reset_index().set_index(['model', 'variance']).sort_index().cv_nll
    # L = fits.reset_index().groupby(['variance', 'model']).cv_nll.sum()
    L = -fits.pivot_table('cv_nll', 'variance', 'model', 'sum')
    deltas = []
    for v in VARIANCES:
        predicted = {'decreasing': 'Breadth', 'constant': 'Best', 'increasing': 'Depth'}[v]

        top = L[best_heuristic].loc[v].sort_values(ascending=False)
        assert top.index[0].startswith(predicted)
        deltas.append(top.iloc[0] - top.iloc[1])

    write_tex('heuristic_min_dnll', fmt_min_delta(min(deltas)))

    all_fits = {
        'no_fancy': fits.loc[~fits.model.str.contains('Prob')],
        'full': fits
    }
    reported_best = {
        'no_fancy': dict(zip(VARIANCES, ['OptimalPlus', 'Best_BestNext_DepthLimit', 'OptimalPlus'])),
        'full': dict(zip(VARIANCES, ['OptimalPlus', 'Best_Satisfice_ProbBetter_ProbBest_DepthLimit', 'OptimalPlus']))
    }
    for key, the_fits in all_fits.items():
        L = -the_fits.pivot_table('cv_nll', 'variance', 'model', 'sum')

        for v in VARIANCES:
            lp = L.loc[v]
            best_model, delta = get_best_with_delta(lp)

            assert best_model == reported_best[key][v]
            if best_model != 'OptimalPlus':
                delta = lp[best_model] - lp['OptimalPlus']
            write_tex(f'dnll_{v}_{key}', rf'$\dnll = {delta:.0f}$')

        x = L.loc['constant'].sort_values()
        # delta = x.iloc[-1] - x.iloc[-2]
        # write_tex(f'top2_{key}', rf'$\dnll = {delta:.0f}$')
        x.loc[~x.index.str.startswith('Best')]
        delta = x.iloc[-1] - x.loc[~x.index.str.startswith('Best')][-1]

        write_tex(f'top2_class_{key}', rf'$\dnll = {delta:.0f}$')

@do_if(EXPERIMENT == 3)
def this():
    deltas = []
    x = totals.loc[~totals.model.str.contains('Prob')]  # exclude fancy
    ll = -x.groupby(['variance', 'model']).cv_nll.sum()
    for v in VARIANCES:
        model, delta = get_best_with_delta(ll.loc[v])
        assert model == 'OptimalPlusExpand'
        deltas.append(delta)

    write_tex('min_dnll', fmt_min_delta(min(deltas)))

@do_if(EXPERIMENT == 4)
def this():
    x = totals.loc[~totals.model.str.contains('Prob')]  # exclude fancy
    ll = -x.groupby(['model']).cv_nll.sum()
    model, delta = get_best_with_delta(ll)
    assert model == 'OptimalPlusExpand'
    write_tex('dnll', rf'$\dnll = {delta:.0f}$')


# %% ==================== Stopping rules across experiments ====================

os.makedirs('tmp', exist_ok=True)
for v in VARIANCES:
    T = totals.loc[v].set_index('model')
    rows = []

    def add_row(name, exclude):
        X = T.filter(regex='^(Breadth|Depth|Best)', axis='index')
        if exclude:
            X = X.loc[~X.index.str.contains(exclude)]
        i = X.cv_nll.idxmin()
        x = dict(X.loc[i])
        x['name'] = name
        rows.append(x)

    for m in MECHANISMS:
        add_row(f'Basic -{m}', f'ProbBetter|ProbBest|{m}')

    add_row(f'Basic', f'ProbBetter|ProbBest')
    add_row(f'Basic +ProbBetter', f'ProbBest')
    add_row(f'Basic +ProbBest', f'ProbBetter')
    add_row(f'Basic +Both', None)
    rows.append({'name': 'Optimal', **T.loc['OptimalPlus']})
    if 'Expand' in MECHANISMS:
        rows.append({'name': 'Optimal +Forward', **T.loc['OptimalPlusExpand']})

    pd.DataFrame(rows).set_index('name').to_pickle(f'tmp/table-{EXPERIMENT}{v}')
# %% --------

@do_if(EXPERIMENT == 4)
def this():
    keys = {
        '1constant' : '1 Constant',
        '2decreasing' : '2 Decreasing',
        '2constant' : '2 Constant',
        '2increasing' : '2 Increasing',
        '3decreasing' : '3 Decreasing',
        '3constant' : '3 Constant',
        '3increasing' : '3 Increasing',
        '4constant' : '4 Constant',
        # '1constant' : '1 Const',
        # '2constant' : '2 Const',
        # '2decreasing' : '2 Dec',
        # '2increasing' : '2 Inc',
        # '3constant' : '3 Const',
        # '3decreasing' : '3 Dec',
        # '3increasing' : '3 Inc',
        # '4constant' : '4 Const',
    }

    cols = {}
    for k, name in keys.items():
        cols[name] = pd.read_pickle(f'tmp/table-{k}').cv_nll
    tbl = pd.DataFrame(cols).round()
    tbl = tbl.reindex(pd.read_pickle(f'tmp/table-{k}').index)  # unsort (thanks Pandas)
    tbl.index.name = 'Model Class'
    tbl.index = tbl.index.str.replace('-Expand', '-Forward')
    write_tex(f'mechanism_table', tbl.to_latex(na_rep='', float_format="%d"))
    
    # cols = {}
    # for k, name in keys.items():
    #     cols[name] = pd.read_pickle(f'tmp/table-{k}').geometric_like
    # tbl = pd.DataFrame(cols).round(3)
    # tbl = tbl.reindex(pd.read_pickle(f'tmp/table-{k}').index)  # unsort (thanks Pandas)
    # tbl.index.name = 'Model Class'
    # tbl.index = tbl.index.str.replace('-Expand', '-Forward')
    # write_tex(f'mechanism_table_geometric', tbl.to_latex(na_rep='', float_format="%.3f"))

# %% ==================== Search order table ====================

if EXPERIMENT < 3:
    basic = list(BASIC)
else:
    basic = ['Expand', 'MetaGreedyExpand', 'OptimalPlusExpand']

x = totals.reset_index().pivot('model', 'variance', 'cv_nll').loc[basic + best_heuristic]
x.columns = [f'{EXPERIMENT} {c.title()}' for c in x.columns]
x.index = x.index.map(lambda x: figs.nice_name(x).split()[0])
x.index = x.index.str.replace('MetaGreedyExpand', 'Myopic').str.replace('Expand', 'Random')
x.to_pickle(f'tmp/order_table-{EXPERIMENT}')

# %% --------
@do_if(EXPERIMENT == 4)
def this():
    tbl = pd.concat((pd.read_pickle(f'tmp/order_table-{exp}') for exp in [1,2,3,4]), axis=1)
    tbl = tbl.round()
    tbl.index.name = 'Model Class'
    tbl = tbl.loc[::-1]
    write_tex(f'order_table', tbl.to_latex(na_rep='', float_format="%d"))



# %% ==================== Build table ====================

# param_counts = get_result(VERSION, 'param_counts.json')
# param_counts['Random_Expand'] = param_counts.get('Expand', None)
# param_counts['MetaGreedy_Expand'] = param_counts.get('MetaGreedyExpand', None)
# param_counts['OptimalPlus_Expand'] = param_counts.get('OptimalPlusExpand', None)

# def write_table(logp, postfix=''):
    
#     logp = logp.rename(columns={
#         'Expand': 'Random_Expand',
#         'MetaGreedyExpand': 'MetaGreedy_Expand',
#         'OptimalPlusExpand': 'OptimalPlus_Expand',
#         }) 

#     total = logp.sum()
#     best_fit = logp.groupby('wid').sum().T.idxmax()
#     nbf = best_fit.value_counts()

#     def make_row(model):
#         row = {'Class': model.split('_')[0].replace('Plus', '')}
#         for mech in MECHANISMS:
#             row[mech] = mech in model
#         row['# Param'] = param_counts[model]
#         row['# Subj'] = nbf.get(model, 0)
#         row['Total NLL'] = -int(round(total[model]))
#         return row

#     models = total.index.unique()
#     t = pd.DataFrame(make_row(model) for model in models)
#     t.Class.replace('MetaGreedy', 'Myopic', inplace=True)

#     t.Class = pd.Categorical(t.Class, ['Random', 'Myopic', 'Optimal', *HEURISTICS])
#     t = t.sort_values(['Class'] + MECHANISMS)
#     rename = {
#         'Satisfice': 'S',
#         'BestNext': 'BN',
#         'DepthLimit': 'DL',
#         'Prune': 'P',
#         'Expand': 'F'

#         }
#     t.rename(columns=rename, inplace=True)

#     write_tex(f'modelcomp_table_{postfix}', t.to_latex(index=False, 
#         formatters={
#             rename[mech]: lambda x: {False: '', True: 'X'}[x]
#         for mech in MECHANISMS}))

# @do_if(True)
# def this():
#     for v, d in logp.groupby('variance'):
#         write_table(d, v)

# %% ==================== Old figures ====================



# @figure()
# def bbd_individual_likelihood():
#     def plot_participants(val, fits, COMPARISON_MODELS):
#         sns.swarmplot(y='model', x=val, data=fits, order=COMPARISON_MODELS,
#                       palette=palette)
#         for w, d in fits.groupby('wid'):
#             # c = palette[pdf.click_delay[w]]
#             c = 'k'
#             plt.plot(d.set_index('model').loc[COMPARISON_MODELS][val], COMPARISON_MODELS, color=c, lw=2, alpha=0.5)
#         plt.ylabel('')
#         plt.xlabel('Log Likelihood')

#     X = fits.set_index('variance')

#     fig, axes = plt.subplots(len(VARIANCES), 1, figsize=(8,4*len(VARIANCES)))
#     for i, v in enumerate(VARIANCES):
#         if i != 0:
#             plt.legend().remove()
#         try:
#             plt.sca(axes.flat[i])
#         except:
#             pass
#         plot_participants('cv_nll', X.loc[v], COMPARISON_MODELS)
#         plt.title(f'{v.title()} Variance')
#         if i != len(VARIANCES) - 1:
#             plt.xlabel('')

# # %% --------


# @figure()
# def geometric_mean_likelihood(axes=None):
#     plot_model_performance(
#         np.exp(logp.groupby('variance').mean()),
#         "Geometric Mean Likelihood",
#         axes
#     )

# # %% --------


# # %% --------
# @figure()
# def plot_full_likelihood(axes=None):
#     plot_model_performance(
#         -logp.groupby('variance').sum(),
#         'Cross Validated\nNegative Log-Likelihood',
#         axes
#     )

# # %% --------

# @figure()
# def plot_average_predictive_accuracy(axes=None):
#     plot_model_performance(np.exp(logp.groupby(['variance', 'wid']).mean()),
#         'Predictive Accuracy', axes)
# # %% --------

# @figure()
# def individual_predictive_accuracy():
#     models = COMPARISON_MODELS
#     fig = plt.figure(figsize=(8,4))
#     L = np.exp(logp.groupby('wid').mean())
#     L = L.loc[pdf.index]

#     lm = L.mean().loc[models]
#     plt.scatter(lm, lm.index, s=100, color=[palette[m] for m in models]).set_zorder(20)

#     sns.stripplot(y='Model', x='value',
#         data=pd.melt(L, var_name='Model'),
#         order=models,  jitter=False, 
#         palette=palette,
#         alpha=0.1)

#     for wid, row in L.iterrows():
#         # c = palette[pdf.click_delay[w]]
#         c = 'k'
#         plt.plot(row.loc[models], models, color=c, lw=1, alpha=0.1)
#     plt.xlabel('Predictive Accuracy')
#     plt.ylabel('')
#     figs.reformat_ticks(yaxis=True)