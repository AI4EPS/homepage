# Research

Earthquakes are among the most destructive natural hazards, and among the hardest to anticipate. Much of what we need to understand them already sits unread in decades of seismic archives. We develop machine-learning methods to recover that information, and use it to build catalogs, characterize earthquake sources, image faults at depth, and forecast future shaking and seismicity.

## Data Mining

Seeing a whole fault system at once requires measuring every event the same way. [STEAD](https://doi.org/10.1109/ACCESS.2019.2947848) assembled a global set of labeled seismic signals for machine learning, and [CEED](https://huggingface.co/datasets/AI4EPS/CEED) unifies California's northern and southern records into roughly 650,000 events and four million waveforms since 1987, labeled with phase arrivals, first-motion polarities, and ground motion. We build catalogs at this scale with [QuakeFlow](https://github.com/AI4EPS/QuakeFlow), and are extending the record beyond California.

Catalogs built this way span [tectonic](https://doi.org/10.1785/0320210001), [induced](https://doi.org/10.1029/2020GL087032), and [volcanic](https://doi.org/10.1126/science.ade5755) earthquakes, from shallow crustal sequences to [megathrust](https://doi.org/10.1126/science.adt6389) and [deep](https://doi.org/10.1093/gji/ggae200) earthquakes in subduction zones.

## Detection

A waveform records when and where an earthquake happened, how its fault ruptured, and what its waves crossed, but classical analysis reads only part of that, and mostly for the largest events. [PhaseNet](https://github.com/AI4EPS/PhaseNet) picks phase arrivals, [DeepDenoiser](https://github.com/AI4EPS/DeepDenoiser) separates signal from noise, newer models add first-motion polarity, and the [phase neural operator](https://doi.org/10.1029/2023GL106434) picks across a whole network at once.

Station coverage remains sparse offshore, so we also work with distributed acoustic sensing, which turns a telecommunication cable into thousands of sensors. Because hand-labeled fiber data are scarce, [PhaseNet-DAS](https://github.com/AI4EPS/EQNet) trains on labels transferred from seismometers, [DASFormer](https://doi.org/10.1007/s44267-025-00085-y) learns from unlabeled recordings, and [DASNet](https://arxiv.org/abs/2603.14844) detects, classifies, and picks signals on submarine fiber, where four years of one Monterey Bay cable recorded local earthquakes, distant T-waves, whale calls, and vessel traffic.

## Inversion

Precise locations resolve diffuse seismicity into the fine structure of faults, and seismic-wave speed indicates where fluids and fractured rock influence slip. Automatic differentiation supplies the gradients these inversions need directly from the forward model, so physical constraints and learned components fit in one framework. [GaMMA](https://github.com/AI4EPS/GaMMA) and [VORA](https://arxiv.org/abs/2607.10450) associate arrivals, [ADLoc](https://github.com/AI4EPS/ADLoc) locates them, and [ADTomo](https://github.com/AI4EPS/ADTomo) and [ADSeismic](https://github.com/AI4EPS/ADSeismic.jl) image subsurface structure.

## Forecasting

Forecasts of shaking and aftershocks drive early warning and post-event response, and have largely rested on empirical ground-motion relations and on statistical aftershock models that prescribe a fixed temporal decay and an isotropic spatial kernel. As catalogs become more complete and internally consistent, forecasts can be learned from them directly. [QuakeFormer](https://arxiv.org/abs/2412.00815) unifies ground-motion forecasting, early warning, and interpolation in one model, and [QuakeGen](https://arxiv.org/abs/2607.24109) generates evolving fields of aftershock rate and maximum magnitude, outperforming the operational USGS Reasenberg-Jones forecast. [Physical simulation of the earthquake cycle](https://doi.org/10.1038/s41467-020-18598-z) couples fluid flow, crack sealing, and fault slip, reproducing swarms, aseismic slip, and injection-driven pressure changes, and provides an independent physical constraint on the data-driven forecasts.

## Open science

We release our software under [AI4EPS](https://github.com/AI4EPS), and it is used in both research and operational catalogs. These models are converging toward a seismic foundation model, one shared representation of seismic waveforms learned across networks, borehole arrays, and fiber.
