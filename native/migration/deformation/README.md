# Maintained skin deformation kernels

Pinned GPL-3.0-or-later addon sources are recorded by original hashes in sources.json.
The original native.cpp ABI is replaced by owned AnthroForge adapters. Numerical LE,
FAST/BBW, embedding, material sampling and contact behavior are retained. Experimental
nonlinear branches remain private and are not exposed as supported modes.

Execution adaptation in model.hpp: check reads the existing job cancellation token,
not a filesystem sentinel. The old 600-second whole-job timeout is omitted under the
explicitly approved execution policy. The cancel string is retained only for the original
BBW cache path. Numerical stopping tolerances/iteration counts are unchanged. Contact's
advisory work limits are separate; contact integration is not yet qualified.

C++ adapters perform the original normalization and area-CDF sampling formerly done by
Python. Mutable factorization state is exclusively leased during calls; serialized project
references contain owned arrays, not handles. Source inspection/compilation alone does
not establish parity or release qualification.
