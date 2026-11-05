"""Shared Gaussian KDE for lecture posteriors, without modifying sample weights.

Linear binning on fine principal-axis grids followed by Gaussian convolution
approximates scipy's empirical Gaussian KDE. A common factor multiplies each
component's weighted covariance. Known modes retain their measured masses;
periodic coordinates wrap and physical bounds reflect kernel leakage.
"""
import itertools
import numpy as np
from scipy.ndimage import gaussian_filter,gaussian_filter1d
from scipy.interpolate import RegularGridInterpolator

BANDWIDTH=.30
GRID_2D=256
GRID_1D=2048
PROBABILITIES=(.68,.95)
STYLE=dict(kernel='Gaussian',bandwidth_factor=BANDWIDTH,
    bandwidth_units='within-component weighted standard deviation/covariance',
    grid_2d=GRID_2D,grid_1d=GRID_1D,contour_probabilities=list(PROBABILITIES),
    periodic_grid='Adaptive: at least 12 cells per kernel SD, up to 262144 cells per period.',
    mode_weights='Actual posterior component probabilities; no equal-mode reweighting.',
    periodic='Circular unwrapping and summed periodic kernel images.',
    physical_bounds='Reflect kernel leakage at declared physical bounds.')


def weights_for(x,weights=None):
    w=np.ones(len(x)) if weights is None else np.asarray(weights,float).copy()
    assert np.isfinite(x).all() and np.isfinite(w).all() and np.all(w>=0)
    w/=w.sum();return w


def unwrap(x,w,period):
    if period is None:return x.copy()
    centre=np.angle(np.sum(w*np.exp(2j*np.pi*x/period)))*period/(2*np.pi)
    return centre+(x-centre+period/2)%period-period/2


def components(groups,n):
    groups=np.zeros(n,int) if groups is None else np.asarray(groups)
    return [groups==g for g in np.unique(groups)]


def deposit_1d(x,w,grid):
    u=(x-grid[0])/(grid[1]-grid[0]);i=np.floor(u).astype(int);f=u-i
    h=np.zeros(len(grid));valid=(i>=0)&(i<len(grid)-1)
    np.add.at(h,i[valid],w[valid]*(1-f[valid]))
    np.add.at(h,i[valid]+1,w[valid]*f[valid]);return h


def density_1d(x,weights=None,groups=None,bounds=None,period=None,bandwidth=BANDWIDTH):
    x=np.asarray(x,float);w=weights_for(x,weights);pieces=[]
    if period is not None:
        specs=[]
        for keep in components(groups,len(x)):
            p=w[keep].sum();v=w[keep]/p;z=unwrap(x[keep],v,period)
            sd=float(np.sqrt(np.cov(z,aweights=v)));specs.append((keep,p,v,sd))
        ngrid=min(262144,max(GRID_1D,int(np.ceil(period/(bandwidth*min(a[3] for a in specs)/12)))))
        dx=period/ngrid;grid=np.arange(ngrid)*dx
        for keep,p,v,sd in specs:
            h=np.zeros(ngrid)
            u=(x[keep]%period)/dx;i=np.floor(u).astype(int);f=u-i
            np.add.at(h,i%ngrid,v*(1-f));np.add.at(h,(i+1)%ngrid,v*f)
            d=gaussian_filter1d(h,max(bandwidth*sd/dx,.5),mode='wrap')/dx
            pieces.append((grid,p*d))
        return np.r_[grid,period],np.r_[sum(d for _,d in pieces),sum(d[0] for _,d in pieces)]
    for keep in components(groups,len(x)):
        p=w[keep].sum();v=w[keep]/p;z=x[keep]
        sd=float(np.sqrt(np.cov(z,aweights=v)));sd=max(sd,np.ptp(z)*1e-10,1e-30)
        low=z.min()-4.5*bandwidth*sd;high=z.max()+4.5*bandwidth*sd
        grid=np.linspace(low,high,GRID_1D);dx=grid[1]-grid[0]
        d=gaussian_filter1d(deposit_1d(z,v,grid),bandwidth*sd/dx,mode='constant',truncate=4.5)/dx
        if bounds is not None:
            lo,hi=bounds
            if lo is not None:d+=np.interp(2*lo-grid,grid,d,left=0,right=0)
            if hi is not None:d+=np.interp(2*hi-grid,grid,d,left=0,right=0)
            d=np.where((grid>=(lo if lo is not None else -np.inf))&(grid<=(hi if hi is not None else np.inf)),d,0)
        d/=np.trapz(d,grid);pieces.append((grid,p*d))
    low=min(g[0] for g,d in pieces);high=max(g[-1] for g,d in pieces)
    grid=np.linspace(low,high,GRID_1D)
    d=sum(np.interp(grid,g,v,left=0,right=0) for g,v in pieces)
    return grid,d


def evaluate_component(spec,points):
    q=np.asarray(points,float).copy();valid=np.ones(q.shape[:-1],bool)
    for j,period in enumerate(spec['periods']):
        if period is not None:q[...,j]=spec['mean'][j]+(q[...,j]-spec['mean'][j]+period/2)%period-period/2
        elif spec['bounds'][j] is not None:
            lo,hi=spec['bounds'][j]
            if lo is not None:valid&=q[...,j]>=lo
            if hi is not None:valid&=q[...,j]<=hi
    out=np.zeros(q.shape[:-1])
    for transforms in itertools.product(*spec['options']):
        a=q.copy()
        for j,(kind,value) in enumerate(transforms):a[...,j]=a[...,j]+value if kind=='shift' else value-a[...,j]
        a=(a-spec['mean'])@spec['rotation']
        out+=spec['interpolator'](np.stack([a[...,1],a[...,0]],axis=-1))
    return np.where(valid,out*spec['probability']/spec['normalisation'],0.)


def density_2d(x,weights=None,groups=None,bounds=None,periods=None,bandwidth=BANDWIDTH,grid_size=GRID_2D):
    x=np.asarray(x,float);w=weights_for(x,weights)
    periods=periods or [None,None];bounds=bounds or [None,None]
    pieces=[];records=[];specs=[];owners=[]
    for keep in components(groups,len(x)):
        p=float(w[keep].sum());v=w[keep]/p;z=x[keep].copy()
        for j,period in enumerate(periods):z[:,j]=unwrap(z[:,j],v,period)
        mean=(z*v[:,None]).sum(axis=0);cov=np.cov(z.T,aweights=v)
        eigen,rotation=np.linalg.eigh(cov)
        eigen=np.maximum(eigen,np.max(eigen)*1e-14)
        sd=np.sqrt(eigen);r=(z-mean)@rotation
        low=r.min(axis=0)-4.5*bandwidth*sd;high=r.max(axis=0)+4.5*bandwidth*sd
        axes=[np.linspace(low[j],high[j],grid_size) for j in range(2)]
        step=np.array([a[1]-a[0] for a in axes]);u=(r-low)/step;i=np.floor(u).astype(int);frac=u-i
        mass=np.zeros((grid_size,grid_size))
        valid=(i[:,0]>=0)&(i[:,0]<grid_size-1)&(i[:,1]>=0)&(i[:,1]<grid_size-1)
        for a,b in itertools.product([0,1],repeat=2):
            f=(frac[:,0] if a else 1-frac[:,0])*(frac[:,1] if b else 1-frac[:,1])
            np.add.at(mass,(i[valid,1]+b,i[valid,0]+a),v[valid]*f[valid])
        cell=float(np.prod(step));base=gaussian_filter(mass,bandwidth*sd[::-1]/step[::-1],
            mode='constant',truncate=4.5)/cell
        U,V=np.meshgrid(*axes);xy=np.stack([U,V],axis=-1)@rotation.T+mean
        interp=RegularGridInterpolator((axes[1],axes[0]),base,bounds_error=False,fill_value=0.)
        options=[];central=np.ones(U.shape,bool)
        for j in range(2):
            if periods[j] is not None:
                period=periods[j];central&=(xy[...,j]>=mean[j]-period/2)&(xy[...,j]<mean[j]+period/2)
                options.append([('shift',k*period) for k in [-1,0,1]])
            else:
                limits=bounds[j];o=[('shift',0.)]
                if limits is not None:
                    lo,hi=limits
                    if lo is not None:central&=xy[...,j]>=lo;o.append(('reflect',2*lo))
                    if hi is not None:central&=xy[...,j]<=hi;o.append(('reflect',2*hi))
                options.append(o)
        d=np.zeros(U.shape)
        for transforms in itertools.product(*options):
            q=xy.copy()
            for j,(kind,value) in enumerate(transforms):q[...,j]=q[...,j]+value if kind=='shift' else value-q[...,j]
            q=(q-mean)@rotation
            d+=interp(np.stack([q[...,1],q[...,0]],axis=-1))
        d=np.where(central,d,0.);normalisation=float(d.sum()*cell)
        assert normalisation>0
        d*=p/normalisation
        records.append(dict(probability=p,grid_mass=float(d.sum()*cell),kernel_support_mass=normalisation))
        specs.append(dict(mean=mean,rotation=rotation,interpolator=interp,periods=periods,
            bounds=bounds,options=options,probability=p,normalisation=normalisation))
        # Periodic cuts become masked pieces on the original physical axes.
        shifts=[range(int(np.floor(xy[...,j].min()/periods[j])),int(np.floor(xy[...,j].max()/periods[j]))+1)
                if periods[j] is not None else [0] for j in range(2)]
        for a,b in itertools.product(*shifts):
            q=xy.copy();mask=~central
            for j,k in enumerate([a,b]):
                if periods[j] is not None:
                    q[...,j]-=k*periods[j];mask|=(q[...,j]<0)|(q[...,j]>=periods[j])
            if np.any(~mask):pieces.append((q[...,0],q[...,1],np.ma.array(d,mask=mask),cell));owners.append(len(specs)-1)
    # HDRs use the summed mixture density, even if projected branches overlap.
    # Integrating each component against the *total*-density threshold counts
    # mixture probability once without a coarse grid spanning separated modes.
    all_values=[];all_mass=[];render=[]
    for (X,Y,own,cell),owner in zip(pieces,owners):
        if len(specs)==1:total=own.filled(0.);best=np.zeros(X.shape,int)
        else:
            parts=np.stack([evaluate_component(spec,np.stack([X,Y],axis=-1)) for spec in specs])
            total=parts.sum(axis=0);best=np.argmax(parts,axis=0)
        total=np.ma.array(total,mask=np.ma.getmaskarray(own))
        all_values.append(total.compressed());all_mass.append(own.compressed()*cell)
        render.append((X,Y,np.ma.array(total,mask=np.ma.getmaskarray(own)|(best!=owner)),cell))
    values=np.concatenate(all_values);mass=np.concatenate(all_mass)
    order=np.argsort(values)[::-1];c=np.cumsum(mass[order]);c/=c[-1]
    levels=[float(values[order][min(np.searchsorted(c,q),len(order)-1)]) for q in PROBABILITIES]
    return render,levels,records
