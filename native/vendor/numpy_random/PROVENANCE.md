# Deterministic routing randomness

`pcg64.h` is copied unchanged from NumPy v1.26.4:
https://raw.githubusercontent.com/numpy/numpy/v1.26.4/numpy/random/src/pcg64/pcg64.h

The bounded 32-bit Lemire distribution in `routing_random.cpp` adapts
`buffered_bounded_lemire_uint32` and the singleton-range behavior from:
https://raw.githubusercontent.com/numpy/numpy/v1.26.4/numpy/random/src/distributions/distributions.c

Both use the upstream MIT terms retained in the header and `LICENSE.txt`.
The adapter uses the exact PCG64 states produced by NumPy 1.26.4 for the production
planner's fixed seeds 914 and 915. No Python callback or runtime random dependency is
introduced. The pinned addon tree fixture checks every generated node, parent index
and final path; ordinary floating-point tolerance accounts for native math-library
rounding rather than claiming cross-platform bit identity.
