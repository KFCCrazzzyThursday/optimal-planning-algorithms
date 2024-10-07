%reset -f
%run -i setup 4
figs.nosave = True
%run -i model_comparison
%run -i breadth_depth
%run -i expansion
figs.nosave = False

@figure(tight=False)
def exp4_main():
    fig = plt.figure(constrained_layout=True, figsize=(12, 0.9 * 6),)
    gs = fig.add_gridspec(2, 6)
    
    plt.sca(fig.add_subplot(gs[:, 0:4]))
    # img = Image.open(f'imgs/roadtrip.png')
    # plt.imshow(img)
    plt.axis('off')
    if LABEL_PANELS:
        plt.annotate('A', (-0.4, 1), xycoords='axes fraction', size=32, va='bottom')
    
    ax = fig.add_subplot(gs[0, 4:6])
    plot_geometric_mean_likelihood(np.array(ax))
    if LABEL_PANELS:
        ax.annotate('B', (-0.5, 1), xycoords='axes fraction', size=32, va='bottom')
    
    ax = fig.add_subplot(gs[1, 4:6])
    plt.sca(ax)
    expansion_value()

    if LABEL_PANELS:
        ax.annotate('C', (-0.5, 1), xycoords='axes fraction', size=32, va='bottom')

    fig.set_constrained_layout_pads(h_pad=0.1)
