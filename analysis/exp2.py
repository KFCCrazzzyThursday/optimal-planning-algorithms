%reset -f
%run -i setup 2
figs.nosave = True
%run -i termination
%run -i pareto
%run -i model_comparison
figs.nosave = False
%run -i breadth_depth
# %% --------
@figure(tight=False)
def exp2_main():
    label_offset = -0.3
    fig, axes = plt.subplots(4, 3, figsize=(12, 0.9 * (4.1+3+3+3)), 
        constrained_layout=True, 
        gridspec_kw=dict(height_ratios=[4.1,3,3,3]))

    if LABEL_PANELS:
        for char, ax in zip('ABCDEFG', axes[:, 0]):
            ax.annotate(char, (label_offset, 1.2), xycoords='axes fraction', size=24, va='bottom')
    
    # task image
    for v, ax in zip(VARIANCES, axes[0, :]):
        ax.set_title(f'{v.title()} Variance', fontdict=dict(fontsize=20))
        # ax.imshow(task_image(v))
        ax.axis('off')
    plot_pareto(axes[1, :], legend=False, fit_reg=False)
    # for i, ax in enumerate(axes[1, :]):
    #     ax.set_ylim(-1, 25)
    #     if i != 0:
    
    #         ax.set_yticks([])
    plot_geometric_mean_likelihood(axes[2, :])
    plot_second_click(axes[3, :])
    axes[3,0].legend().remove()
    for i, ax in enumerate(axes[3, :]):
        # if i != 0:
        ax.set_yticks([0, 0.5, 1])
    fig.set_constrained_layout_pads(h_pad=0.1)

