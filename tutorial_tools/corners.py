"""Plot actual nessai draws for the same single/two-source search data."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import matplotlib
# Use the notebook backend.
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter,MaxNLocator

B=Path(__file__).resolve().parents[1]
BLUE,ORANGE='#185e92','#d78b25'
PLOT_CHECKS={}
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})


def _flags_per_dataset(flags,datasets):
    """A flags entry given as one array per dataset, or None for a shared array."""
    if not isinstance(flags,(list,tuple)) or len(flags)!=len(datasets):return None
    for entry,draws in zip(flags,datasets):
        try:
            if len(entry)!=len(draws):return None
        except TypeError:return None
    return list(flags)


def corner_plot(data,labels,path,truths,colors=None,legend=None,ranges=None,size=6.7,frequency_axes=(),local_ranges=None,truth_sets=None,branch_specs=None,periods=None,bounds=None,bandwidth=None,grid_size=None):
    from .posterior_density import density_1d,density_2d,STYLE
    datasets=data if isinstance(data,list) else [data]
    colors=colors or [BLUE]*len(datasets);d=len(labels)
    periods=periods or {};bounds=bounds or {}
    # Optional KDE overrides. Both default to None, which passes no keyword at
    # all, so every existing call produces byte-identical output.
    kw1={} if bandwidth is None else dict(bandwidth=bandwidth)
    kw2=kw1 if grid_size is None else dict(kw1,grid_size=grid_size)
    specs=[(flags,affected,_flags_per_dataset(flags,datasets)) for flags,affected in (branch_specs or [])]
    def groups_for(dims,index):
        if not branch_specs:return None
        per=datasets[index]
        groups=np.zeros(len(per),int)
        for flags,affected,split in specs:
            if set(dims)&set(affected):
                groups=2*groups+np.asarray(split[index] if split is not None else flags,int)
        return groups
    if ranges is None:
        ranges=[]
        for j in range(d):
            lo=min(x[:,j].min() for x in datasets);hi=max(x[:,j].max() for x in datasets)
            extra=.05*(hi-lo);lo-=extra;hi+=extra
            if j in bounds:
                a,b=bounds[j]
                if a is not None:lo=max(lo,a)
                if b is not None:hi=min(hi,b)
            if j in periods:lo=max(lo,0.);hi=min(hi,periods[j])
            ranges.append((lo,hi))
    fig,axes=plt.subplots(d,d,figsize=(size,size),squeeze=False)
    fig.subplots_adjust(left=.13,right=.98,bottom=.17 if d<=4 else .12,top=.98,hspace=.06,wspace=.06)
    audit=[]
    for row in range(d):
        for col in range(d):
            ax=axes[row,col]
            if col>row:ax.set_visible(False);continue
            ax.set_box_aspect(1)
            if row==col:
                for index,(draws,color) in enumerate(zip(datasets,colors)):
                    x,y=density_1d(draws[:,col],groups=groups_for([col],index),bounds=bounds.get(col),period=periods.get(col),**kw1)
                    ax.plot(x,y,color=color,lw=1.5)
                ax.set_ylim(bottom=0);ax.set_yticks([])
            else:
                for index,(draws,color) in enumerate(zip(datasets,colors)):
                    grids,levels,records=density_2d(draws[:,[col,row]],groups=groups_for([col,row],index),
                        bounds=[bounds.get(col),bounds.get(row)],periods=[periods.get(col),periods.get(row)],**kw2)
                    t68,t95=levels
                    for x,y,density,cell in grids:
                        valid=[(threshold,style) for threshold,style in [(t95,'--'),(t68,'-')]
                               if density.min()<threshold<density.max()]
                        if valid:
                            ax.contourf(x,y,density,levels=[t95,t68,max(float(density.max()),t68)*(1+1e-8)],
                                colors=[color,color],alpha=.17)
                            ax.contour(x,y,density,levels=[a for a,b in valid],colors=[color],
                                linestyles=[b for a,b in valid],linewidths=1.3)
                    audit.append(dict(row=row,column=col,components=records))
                ax.set_ylim(*ranges[row]);ax.yaxis.set_major_locator(MaxNLocator(3))
            ax.set_xlim(*ranges[col]);ax.xaxis.set_major_locator(MaxNLocator(3))
            ax.tick_params(labelsize=10 if d<=4 else 7)
            if col in frequency_axes:
                ax.xaxis.set_major_formatter(FormatStrFormatter('%.7f'));ax.xaxis.set_major_locator(MaxNLocator(2))
            if row in frequency_axes and col<row:
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.7f'));ax.yaxis.set_major_locator(MaxNLocator(2))
            if row<d-1:ax.tick_params(axis='x',labelbottom=False)
            else:
                ax.set_xlabel(labels[col],fontsize=14 if d<=4 else 9)
                ax.xaxis.set_label_coords(.5,-.60 if d<=4 or col in frequency_axes else -.42)
                ax.tick_params(axis='x',labelrotation=45)
            if col>0:ax.tick_params(axis='y',labelleft=False)
            elif row>0:
                ax.set_ylabel(labels[row],fontsize=14 if d<=4 else 9)
                ax.yaxis.set_label_coords(-.65 if row in frequency_axes else -.42,.5)
    marker_sets=truth_sets if truth_sets is not None else ([] if truths is None else [truths])
    marker_colors=colors if truth_sets is not None else ['#536370']
    for truth,color in zip(marker_sets,marker_colors):
        for row in range(d):
            for col in range(row+1):
                ax=axes[row,col];ax.axvline(truth[col],color=color,lw=.8,alpha=.55)
                if row>col:
                    ax.axhline(truth[row],color=color,lw=.8,alpha=.55)
                    ax.plot(truth[col],truth[row],'+',color=color,ms=5)
    if legend:
        fig.legend([Line2D([],[],color=c,lw=2) for c in colors],legend,
            loc='upper right',bbox_to_anchor=(.95,.95),frameon=False,fontsize=12 if d<=4 else 11)
    path=Path(path)
    audit_style=dict(STYLE)
    if bandwidth is not None:audit_style['bandwidth_factor']=bandwidth
    if grid_size is not None:audit_style['grid_2d']=grid_size
    fig.savefig(path,dpi=240,bbox_inches='tight',facecolor='white');plt.close(fig)
    PLOT_CHECKS[path.name]=dict(style=audit_style,panels=audit)


