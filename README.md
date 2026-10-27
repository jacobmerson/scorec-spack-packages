# scorec-spack-packages (Spack repo)

This Spack repository (namespace `scorec`) provides recipes for SCOREC software and related dependencies, including:

- **PCMS**: [SCOREC/pcms](https://github.com/SCOREC/pcms)
- **MeshFields**: [SCOREC/meshFields](https://github.com/SCOREC/meshFields)
- **EnGPar**: [SCOREC/EnGPar](https://github.com/SCOREC/EnGPar)
- **PUMI-PiC**: [SCOREC/pumi-pic](https://github.com/SCOREC/pumi-pic)
- **OpenMC with PUMI‑Tally** (OpenMC fork integrating PUMI‑Tally):
  - **OpenMC fork**: [Fuad-HH/openmc](https://github.com/Fuad-HH/openmc) (upstream: [openmc-dev/openmc](https://github.com/openmc-dev/openmc))
  - **PUMI‑Tally**: [Fuad-HH/PumiUMTally](https://github.com/Fuad-HH/PumiUMTally)

## Installation

### 1. Install Spack
It is recommended to use the system-provided Spack if available. If not, follow the instructions below to install
Spack from source. Check the [Spack documentation](https://spack.readthedocs.io/en/latest/getting_started.html) 
for more details.

```bash
git clone --depth=2 https://github.com/spack/spack.git
. /your/path/to/spack/share/spack/setup-env.sh
```

### 2. Create a new environment and activate it
```bash
spack env create pumi-env
spack env activate pumi-env
```

### 3. Add this repository to Spack and update the `builtin` repository

```bash
spack repo add https://github.com/SCOREC/scorec-spack-packages.git --name scorec
spack repo update builtin
spack repo update builtin --branch releases/v2026.10
```
Now, if you do `spack config get repos` you should see the repositories added to the list.
And doing `spack info pumi-pic` should show the package.


### 4. Install Packages

```bash
spack add pumi-pic
```
or for OpenMC with PUMI-Tally:

```bash
spack add openmc-pumi +pumitally +dagmc ^kokkos+openmp+serial
```
and run `spack concretize` and `spack install` to install the packages.

> [!NOTE]
> PUMI-PiC also supports other Kokkos backends. Check available backends with `spack info kokkos`.

## Using OpenMC with PUMI-Tally
The case setup and run instructions are available here: [OpenMC with PUMI-Tally](https://github.com/Fuad-HH/openmc-pumi-tally-casehttps://gist.github.com/Fuad-HH/bf16253e70ae0122800f2128b9fd4a8f#create-mesh-and-run-case)

## Build cache and container images

CI builds the environments under `environments/` and pushes the results to a
public Spack build cache. Add it as a mirror to install prebuilt binaries
instead of building from source:

```bash
spack mirror add --unsigned scorec oci://ghcr.io/scorec/scorec-spack-buildcache
```

### PCMS container image

The `pcms+python+petsc` spec of `environments/pcms` is also published as a
runnable, multi-architecture container image. See the
[PCMS README](https://github.com/SCOREC/pcms#run-pcms-in-a-container) for how
to use it.

| Tag | Contents |
|---|---|
| `ghcr.io/scorec/pcms:develop` | Latest build, for `linux/amd64` and `linux/arm64` |
| `ghcr.io/scorec/pcms:develop-YYYY-MM-DD` | The build from that date |

The same images are also tagged in the build cache repository as
`pcms-develop`, `pcms-develop-YYYY-MM-DD`, and per architecture as
`pcms-develop-amd64` and `pcms-develop-arm64`.

How it is built, in `.github/workflows/pcms.yml`:

- `build` (x86_64, `target=x86_64_v3`) and `build-arm` (aarch64,
  `target=armv8.2a`, which runs on Neoverse and Apple silicon) build and test
  the environment. On `main`, each pushes its image as a per-architecture tag
  with `spack buildcache push --base-image ubuntu:24.04 --tag`, which layers
  the spec and its runtime dependencies on the base image.
- `publish-image` combines the per-architecture images into the
  multi-architecture tags. The dated tag holds only the images built in that
  run. The rolling tag takes the latest image of each architecture, so a
  failing build for one architecture doesn't hold back the other.
- `test-container` pulls the dated image on an x86_64 and an aarch64 runner and
  imports `pcms`, including under `mpirun`.

Images are published only from `main`: on pushes that change the PCMS recipes,
environments, or workflows, and by the weekly scheduled run, which picks up new
commits on the branches PCMS and its dependencies track. Pull requests build
and test but don't push.

To publish an image for another environment, pass `image-spec` (a root spec of
the environment that matches exactly one root) and `image-tag` to
`build-spack-env.yml`. New packages on GHCR are private; make them public under
the package's settings. The container tests pull without credentials, the way
users do, so they fail until the package is public.
