%reset -f
%run -i setup 3
figs.nosave = True
%run -i model_comparison
%run -i breadth_depth
%run -i pareto
%run -i expansion
figs.nosave = False

# # %% --------
# @figure(tight=False, reformat_legend=False)
# def exp3_main():
#     fig, axes = plt.subplots(2, 3, figsize=(11.9, 0.9 * 6), 
#         constrained_layout=True,
#         gridspec_kw=dict(height_ratios=[1, 1.2]))
#     for v, ax in zip(VARIANCES, axes[0, :]):
#         ax.set_title(f'{v.title()} Variance', fontdict=dict(fontsize=20), pad=20)

#     first_click_depth(axes[0])
#     # ax = axes[0,0]
#     # handles, labels = ax.get_legend_handles_labels()
#     # ax.legend(handles=handles, labels=['Human', , frameon=False, prop={'size': 12}, **legend_kws)

#     fig.set_constrained_layout_pads(h_pad=0.1)
#     plot_geometric_mean_likelihood(axes[1])


# %% --------

task_image('increasing3', 65)
task_image('decreasing3', 65)
task_image('constant3', 65)

@figure(tight=False)
def exp3_main():
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
    
    plot_pareto(axes[1, :], legend=True, fit_reg=False)
    handles, labels = axes[1, 0].get_legend_handles_labels()
    axes[1, 0].legend(handles=handles[0:-1], labels=["Optimal", "Forward-only Optimal", "Random"], 
                      frameon=False, prop={'size': 12})

    plot_geometric_mean_likelihood(axes[2, :])
    first_click_depth(axes[3, :])

    for i, ax in enumerate(axes[3, :]):
        # if i != 0:
        ax.set_yticks([0, 0.5, 1])
    fig.set_constrained_layout_pads(h_pad=0.1)
