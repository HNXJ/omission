# Biophysical Stability & Synchrony (Advanced Guidelines)

A collection of operational lessons for building and optimizing stable, asynchronous cortical circuits in JAX/Jaxley.

## 1. Instability: Causes and Solutions
- **Problem**: Voltage "nan-explosions" or unrealistic hyperpolarization (e.g., -500mV).
- **Cause**: High synaptic conductances (especially GABAb) or large `dt` combined with float32 precision.
- **Solution**: 
    - **Stability Barrier**: Use `jnp.where(jnp.isnan(v) | jnp.isinf(v), old_v, v)` in state updates.
    - **Graded Synapses**: Avoid delta-pulses; use `GradedSynapse` logic to smooth conductance changes over time.

## 2. Adjusting Synchrony (Kappa Control)
- **Problem**: Population activity is too periodic (Kappa > 0.5).
- **Adjustment**:
    - **Noise Variance**: Increase `IPnoise.pulse_amp` or reduce `poisson_l` to drive asynchronous state transitions.
    - **Inhibitory Balance**: Strengthen local PV $\to$ Pyr feedback. PV-mediated shunting is the primary desynchronizer.
    - **Conductance Delays**: Introduce heterogeneity in synaptic weights or spatial positions to break global phase-locking.

## 3. Parameter Training (make_trainable)
- **Lesson**: `net.make_trainable("gAMPA")` only makes the *group* trainable (often 1-2 parameters).
- **Action**: To optimize individual synaptic weights, you must call it on the edges: `net.GradedAMPA.edge('all').make_trainable("gAMPA")`. This expands the PyTree to include every scalar conductance.

## 4. Optimization: The Alpha Jolt protocol
- **Protocol**: When loading a last optimal state or hitting a new one, perform **one trial with Alpha=0**.
- **Benefit**: This "Jolt" uses pure supervised gradients to orient the network in the new manifold before resuming adaptive stochastic exploration.

## 5. What to Avoid
- **Constant Seeds**: Never use a fixed integer seed for production trials; it hides the variance inherent in biophysical systems.
- **Purely Local Optima**: Avoid staying at the stochastic floor ($\alpha_{min}=0.1$) for too long. If the optimizer is stuck, increase `lambda_d` or trigger a manual exploration jolt.
