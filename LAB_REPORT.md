# Project Phase 1
## Milestone 0

**Engineering checkpoint 1.**
Because of randomness

## Milestone 1

**Engineering checkpoint 2.**
Setting random_state=42 does not guarantee bit-for-bit identical results across every CPU, GPU, or software stack.
It only ensures reproducibility of the random number generation under the same conditions.

Results may still differ because of:

* Hardware differences: CPUs and GPUs may perform floating-point operations differently.
* Software versions: Different library, compiler, or driver versions may change algorithms or implementations.
* Parallel processing: Different execution orders can produce slightly different floating-point results.
* Non-deterministic operations: Some GPU operations are inherently non-deterministic.

## Milestone 2

**Engineering checkpoint 3.**
The Git remote stores source code and DVC tracking files, the DVC remote stores the actual raw images, and git push does not transfer DVC-managed images (use dvc push instead).

## Milestone 3

