
# %% ==================== Second click ====================

def breadth_depth_data(models, noclick='drop'):
    dfs = []
    d = tdf.reset_index().set_index('variance').copy()
    d['agent'] = 'Human'
    dfs.append(d)
    for k in models:
        d = model_trial_features(k)
        d['wid'] = k
        dfs.append(d)
    data = pd.concat(dfs, sort=False)
    data = data[['agent', 'wid', 'first_revealed', 'second_same']].copy()
    data = data.loc[~data.first_revealed.isna()]  # no first click

    data.first_revealed = data.first_revealed.astype(int)
    if noclick == 'drop':
        data = data.loc[~data.second_same.isna()]
    elif noclick == 'zero':
        data.second_same = data.second_same.fillna(0.)
    else:
        raise ValueError("noclick")
    return data

@figure(EXPERIMENT == 2)
def plot_second_click(axes=None, models=['OptimalPlus', 'Best', 'Breadth', 'Depth'], noclick='drop'):
    bdd = breadth_depth_data(models, noclick=noclick)
    if axes is None:
        fig, axes = setup_variance_plot(title=True)
    for i, v in enumerate(VARIANCES):
        plt.sca(axes.flat[i])
        agents = [*reversed(models), 'Human']
        data = bdd.loc[v].query('agent == @agents')

        grouped = data.groupby(['agent', 'wid', 'first_revealed']).mean().reset_index()
        print(grouped.query('agent == "Human"').first_revealed.value_counts())

        # for m in reversed(models):
        #     highlight = {'decreasing': 'Breadth', 'constant': 'Best', 'increasing': 'Depth'}[v]
        #     alpha = 1 if m in (highlight, 'OptimalPlus') else 0.3
        #     # x = data.loc[m].groupby('first_revealed').mean().sort_index().values
        #     # plt.plot(x, color=palette[m], lw=2.5, alpha=alpha)[0].set_zorder(-10)
        #     sns.pointplot('first_revealed', 'second_same', color=palette[m], data=data.loc[m], 
        #         ci=False)

        # sns.pointplot('first_revealed', 'second_same', color=palette['Human'],
        #     data=data.loc['Human'], legend=False)
        
        sns.pointplot('first_revealed', 'second_same', hue='agent', hue_order=agents,
            palette=palette, data=grouped, legend=None)
        plt.legend().remove()

        plt.xlabel('First Revealed Value')
        plt.ylim(-0.05, 1.05)
        plt.yticks([0, 0.5, 1])
        if i == 0:
            if noclick == 'zero':
                plt.ylabel('Probability of Second\nClick on Same Path')
            else:
                plt.ylabel('Proportion of Second\nClicks on Same Path')
            # plt.legend()
            # figs.reformat_legend()
        else:
            # plt.legend().remove()
            plt.ylabel('')

@figure(EXPERIMENT == 2)
def plot_second_click_alt():
    plot_second_click(models=COMPARISON_MODELS)

# # %% ==================== First click depth ====================

def load_depth_curve(k):
    d = pd.DataFrame(get_result(VERSION, f'depth_curve/{k}.json'))
    if k != 'Human':
        d.wid = d.wid.apply(lambda x: x.split('-')[1])
    d.set_index('wid', inplace=True)
    d['variance'] = pdf.variance
    d['agent'] = k
    return d.loc[list(pdf.index)]

@figure(EXPERIMENT >= 3)
def first_click_depth(axes=None):
    if axes is None:
        fig, axes = setup_variance_plot(title=True)

    agents = ['Human', 'OptimalPlus', 'OptimalPlusExpand']

    dd = pd.concat([load_depth_curve(h).query('click == 1')
        for h in agents]).set_index(['agent', 'variance']).depth

    def make_hist(m, var):
        x = dd.loc[m, var].value_counts(sort=False)
        x /= x.sum()
        return x

    for i, (ax, var) in enumerate(zip(axes.flat, VARIANCES)):
        d = pd.DataFrame({m: make_hist(m, var) for m in agents})
        d.plot.bar(color=[palette[m] for m in agents], 
            rot=0, ax=ax, legend=i==0)
        ax.set_ylim(0, 1)
        ax.set_xlabel('First Clicked Depth')
        ax.set_xticklabels([1,2,3])
        if i == 0:
            ax.set_ylabel('Proportion of Trials')
            print('hello')
            figs.reformat_legend(ax=ax, OptimalPlusExpand='Optimal +Forward')



# # %% ==================== Depth curve ====================
# @figure()
# def plot_depth_curve(axes=None):
#     # dcd = pd.concat(load_depth_curve(k) for k in ['Human', 'OptimalPlus', 'BestFirst']).set_index('variance')
#     dcd = load_depth_curve('Human')
#     if axes is None:
#         fig, axes = setup_variance_plot(title=True)
#     for i, v in enumerate(VARIANCES):
#         plt.sca(axes.flat[i])
#         sns.lineplot('click', 'cumdepth', hue='agent', 
#             palette=palette, data=dcd.loc[v])
#         plt.xlabel('Click Number')
#         # plt.ylim(-0.05, 1.05)
#         if i == 0:
#             plt.ylabel('Maximum Depth Clicked')
#             plt.legend()
#             figs.reformat_legend()
#         else:
#             plt.legend().remove()
#             plt.ylabel('')




# # %% ==================== HEATMAP ====================

# def plot_depth_heat(agent, axes):
#     # base = matplotlib.cm.get_cmap('Blues', 512)
#     # cmap = matplotlib.colors.ListedColormap(base(np.linspace(0.2, 1, 512 * 0.8)))
#     cmap = 'Blues'

#     dcd = load_depth_curve(agent)
#     D = dcd.set_index('variance')

#     for i, (ax, var) in enumerate(zip(axes.flat, VARIANCES)):
#         plt.sca(ax)
#         X = D.loc[var].groupby(['depth', 'click']).apply(len).unstack()
#         # n_trial = (tdf.variance == var).sum()
#         X /= X[1].sum()
#         g = sns.heatmap(X, cmap=cmap, vmin=0, vmax=1, linewidths=1, cbar=True)
#         g.invert_yaxis()
#         if i > 0:
#             plt.ylabel('')
#         figs.reformat_labels()
#     return g

# @figure()
# def depth_heat():
#     fig, axes = setup_variance_plot(2, title=True)
#     plot_depth_heat('Human', axes[0])
#     plot_depth_heat('OptimalPlus', axes[1])


