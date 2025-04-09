# from statsmodels.stats.proportion import proportion_confint
# from statsmodels.stats.proportion import proportions_ztest
from statsmodels.formula.api import logit 
import scipy

expansion = pd.DataFrame(get_result(VERSION, 'expansion.json')).set_index('wid')
expansion['gain'] = (expansion.q_jump - expansion.q_expand) * 10  # undo previous rescaling
expansion['gain_z'] = (expansion.gain - expansion.gain.mean()) / expansion.gain.std()
expansion['jump'] = ~expansion['expand']

@do_if(True)
def expansion_stats():
    human = load_cf('Human').query('variance == "constant" and not is_term').expand
    model = load_cf('OptimalPlusPure').query('variance == "constant" and not is_term').expand

    write_tex('expansion_human', f'{100*human.mean():.1f}\\%')
    # write_tex(f'expansion_human', mean_std(100*human.groupby('wid').mean(), fmt='pct', digits=0))

    write_tex('expansion_optimal', f'{100*model.mean():.1f}\\%')


    h = human.groupby('wid').mean()
    m = model.mean()

    lo, hi = bootstrap_confint(100*h)
    write_tex(f'expansion_ci', f'95\\% CI [{lo:.1f}, {hi:.1f}]')
    
    p = wilcoxon(h - m).pvalue
    z = abs(scipy.stats.norm.ppf(p/2))
    write_tex(f'expansion_wilcoxon', f'$z = {z:.2f}, {pval(p)}$')

    write_tex("jump", f'{expansion.jump.mean()*100:.1f}\%')
    # write_tex("jump", mean_std(expansion.groupby('wid').jump.mean()*100, fmt='pct'))

    m = logit(f'jump.astype(int) ~ gain_z', data=expansion).fit()

    lo, hi = m.conf_int().loc['gain_z']

    write_tex(f'expansion_logistic', 
        f'$z = {m.tvalues.gain_z:.1f}$, ${pval(m.pvalues.gain_z)}$, '
        f'$\\beta = {m.params.gain_z:.3f}$, 95\\% CI [{lo:.3f}, {hi:.3f}]'
    )

    expansion.jump = expansion.jump.astype(int)
    expansion[['gain_z', 'jump']].to_csv(f'tmp4r/{EXPERIMENT}/expansion.csv')
    # write_tex(f'expansion_logistic', rf'$\beta = {m.params.gain_z:.3f}$, 95\% CI [{lo:.3f} {hi:.3f}], ${pval(m.pvalues.gain_z)}$')

# @do_if(True)
# def expansion_stats_increasing():
#     human = load_cf('Human').query('variance == "increasing" and not is_term').expand
#     model = load_cf('OptimalPlusPure').query('variance == "increasing" and not is_term').expand

#     write_tex('expansion_human_increasing', f'{100*human.mean():.1f}\\%')
#     # write_tex(f'expansion_human', mean_std(100*human.groupby('wid').mean(), fmt='pct', digits=0))

#     write_tex('expansion_optimal_increasing', f'{100*model.mean():.1f}\\%')

#     constant = load_cf('Human').query('variance == "constant" and not is_term').expand

#     z, p = proportions_ztest([human.sum(), constant.sum()], [len(human), len(constant)])
#     human.sum() / len(human)
#     constant.sum() / len(constant)
#     write_tex("expansion_test_increasing_vs_constant", rf"$z={z:.1f},\ {pval(p)}$")


@figure()
def expansion_value():
    sns.regplot('gain', 'jump', data=expansion, logistic=True, x_bins=np.linspace(-7.5, 7.5, 7), color='black')
    plt.xlabel('Value of Violating Forward Search')
    plt.ylabel('Probability of Violating\nForward Search')



# %% ==================== expansion rate by participant ====================

@figure(False)
def expansion_rate():
    opt_exp = load_cf('OptimalPlus').groupby('wid').expand.mean()
    opt_pure_exp = load_cf('OptimalPlusPure').groupby('wid').expand.mean()
    cf = load_cf('Human')

    fig, axes = setup_variance_plot()
    for ax, (_, d) in zip(axes.flat, cf.groupby(['variance'])):
        plt.sca(ax)
        g = d.expand.groupby('wid')
        est = g.mean()
        lo, hi = proportion_confint(g.apply(sum), g.apply(len))
        err = np.vstack([(est - lo).values, (hi - est).values])
        idx = np.argsort(est)
        plt.errorbar(np.arange(len(est)), est[idx], yerr=err[:, idx], color='k', label='Humans')
        
        plt.plot(np.arange(len(est)), opt_exp[est.index][idx], color=palette['Optimal'], label='Optimal')
        plt.plot(np.arange(len(est)), opt_pure_exp[est.index][idx], color=lb, label='Pure Optimal')

        plt.xticks([])
        plt.xlabel("Participant")
        plt.ylim(-0.05, 1.05)
        plt.ylabel('Expansion Rate')
        plt.axhline(1, label='Forward Search', color=palette['Breadth'])
    axes.flat[0].legend()

