@do_if(True)
def this():
    cf_hum = load_cf('Human').query('n_revealed < 16')
    cf_opt = load_cf('OptimalPlusPure').query('n_revealed < 16')

    for df in [cf_opt, cf_hum]:  # order matters!
        for k in ['term_reward', 'best_next']:
            df[k] = (df[k] - cf_hum[k].mean()) / cf_hum[k].std()
            df.is_term = df.is_term.astype(int)

    cf_opt[['term_reward', 'best_next', 'is_term']].to_csv(f'tmp4r/{EXPERIMENT}/opt_term.csv')
    cf_hum[['term_reward', 'best_next', 'is_term']].to_csv(f'tmp4r/{EXPERIMENT}/hum_term.csv')

    

# %% ==================== heatmaps ====================

def robust_mean(x):
    return np.mean(x)
    if len(x) < 5:
        return np.nan
    return np.mean(x)

def plot_term(df, x, y, **kws):
    base = matplotlib.cm.get_cmap('Blues', 512)
    cmap = matplotlib.colors.ListedColormap(base(np.linspace(0.2, 1, round(512 * 0.8))))

    # df = df.query('term_reward >= -10')
    assert EXPERIMENT == 1
    max_clicks = 16
    df = df.query('n_revealed < @max_clicks')
    X = df.groupby([y, x]).is_term.apply(robust_mean).unstack()

    ax = sns.heatmap(X, cmap=cmap, vmin=0, vmax=1, linewidths=1, **kws)

    xlab = [int(float(t.get_text())) for t in ax.get_xticklabels()]
    ax.set_xticks(ax.get_xticks()[::2])
    ax.set_xticklabels(xlab[::2])
    plt.xticks(rotation=0)
    
    ylab = [int(float(t.get_text())) for t in ax.get_yticklabels()]
    ax.set_yticks(ax.get_yticks()[::2])
    ax.set_yticklabels(ylab[::2])

    ax.invert_yaxis()
    plt.xlim(-0.5, X.shape[1] + 0.5)
    plt.ylim(-0.5, X.shape[0] + 0.5)
    figs.reformat_labels()
    return ax

def termination(x, y, height=3):
    agents = ['Human', 'OptimalPlusPure']
    # agents = ['Human', 'OptimalPlus']
    nc = len(agents)
    fig, axes = plt.subplots(1, nc+1, figsize=(4*nc, height),
                             gridspec_kw={'width_ratios': [*([16] * nc), 1]})

    cfs = {k: load_cf(k) for k in agents}
    multi_cf = pd.concat([load_cf(k) for k in agents])
    # multi_cf['prob_maximal'] = pd.cut(multi_cf.prob_maximal, bins=np.arange(0, 1.01, 0.1)).apply(lambda x: 100*x.right)

    for k in (x, y):
        multi_cf[k] = pd.Categorical(multi_cf[k])

    for i, (name, cf) in enumerate(multi_cf.groupby('agent')):
        plt.sca(axes[i])
        if i == 0:
            plot_term(cf, x, y, cbar_ax=axes[-1])
        else:
            plot_term(cf, x, y, cbar=False)
            # plt.yticks(())
            plt.ylabel("")
        plt.title(figs.nice_name(name))
    axes[-1].set_ylabel('Stopping Probability', labelpad=10)


if EXPERIMENT == 1:
    @figure(despine=True, tight=False)
    def plot_termination():
        # with sns.axes_style('white'):
        termination('best_next', 'term_reward', height=4)
        # sns.despine(offset=10, trim=True)

    # %% --------
    @figure()
    def plot_nextbest():
        X = pd.concat(load_cf(v) for v in ['Human', 'OptimalPlusPure'])
        sns.pointplot('best_next', 'is_term', data=X, hue='agent', palette=palette)
        plt.ylabel('Probability of Stopping')
        figs.reformat_legend()
        figs.reformat_labels()

    # %% --------
    @figure()
    def plot_satisfice():
        X = pd.concat(load_cf(v) for v in ['Human', 'OptimalPlusPure'])
        sns.pointplot('term_reward', 'is_term', data=X, hue='agent', palette=palette)
        plt.ylabel('Probability of Stopping')
        figs.reformat_legend()
        figs.reformat_labels()

    # %% --------
    @figure()
    def plot_probmax():
        X = pd.concat(load_cf(v) for v in ['Human', 'OptimalPlusPure'])
        X['prob_maximal'] = pd.cut(X.prob_maximal, bins=np.arange(0, 1.01, 0.1)).apply(lambda x: x.mid)
        sns.lineplot('prob_maximal', 'is_term', data=X, hue='agent', palette=palette)
        plt.ylabel('Probability of Stopping')
        plt.xlim(0, 1)
        figs.reformat_legend()
        figs.reformat_labels()
