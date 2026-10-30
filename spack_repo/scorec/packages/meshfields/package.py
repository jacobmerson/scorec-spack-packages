# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install meshfields
#
# You can edit this file again by typing:
#
#     spack edit meshfields
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage
from spack.package import *


class Meshfields(CMakePackage, CudaPackage, ROCmPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/SCOREC/meshFields"
    git = "https://github.com/SCOREC/meshFields"

    maintainers("jacobmerson")

    license("BSD-3", checked_by="jacobmerson")

    version('main', branch='main')
    # The default version. meshFields PR #75 (main at f7c97cf) compiles
    # evaluate(), whose Kokkos::View<Real *[numComponents]> nvcc's host
    # compilation rejects, so this is the main commit before it.
    version('1.0.0.20261022', commit='604f42f56bf671a2781fb779fa833c52cfd42f62')

    variant('shared', default=False, description='enable shared library builds')
    variant('tests', default=False, description='enable build of tests')

    depends_on('cxx')
    depends_on('c') # requires c compiler when building with cabana
    depends_on('cabana@0.8.1:', type=('build', 'link', 'run'))
    depends_on('kokkos@4.7.0:4', type=('build','link','run'))
    depends_on('kokkos-kernels@4.7.0:4', type=('build', 'link', 'run'))
    # Only SCOREC omega-h versions; an open-ended range would also match omega-h@main
    depends_on('omega-h@11.0.0-scorec:11,master-scorec+kokkos+mpi~trilinos',type=('build','link','run'))
    depends_on('kokkos+cuda', when='+cuda')
    depends_on('cabana+cuda', when='+cuda')

    # Propagate cuda_arch to dependencies, see https://github.com/spack/spack/issues/28714
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = '+cuda cuda_arch={0}'.format(arch)
        depends_on('kokkos {0}'.format(cuda_dep), when=cuda_dep)
        depends_on('cabana {0}'.format(cuda_dep), when=cuda_dep)

    # Propagate amdgpu_target to dependencies
    for arch in ROCmPackage.amdgpu_targets:
        rocm_dep = '+rocm amdgpu_target={0}'.format(arch)
        depends_on('kokkos {0}'.format(rocm_dep), when=rocm_dep)
        depends_on('cabana {0}'.format(rocm_dep), when=rocm_dep)

    conflicts('cuda_arch=none', when='+cuda', msg='CUDA architecture is required')
    # Builds through kokkos's nvcc_wrapper, so +cuda must match Kokkos's backend
    conflicts('~cuda', when='^kokkos+cuda', msg='MeshFields requires +cuda when Kokkos has +cuda')
    conflicts('+cuda', when='^kokkos~cuda', msg='MeshFields requires Kokkos+cuda when CUDA is enabled')
    # Builds with hipcc, so +rocm must match Kokkos's backend
    conflicts('~rocm', when='^kokkos+rocm', msg='MeshFields requires +rocm when Kokkos has +rocm')
    conflicts('+rocm', when='^kokkos~rocm', msg='MeshFields requires Kokkos+rocm when ROCm is enabled')
    conflicts('+cuda', when='+rocm', msg='CUDA and ROCm are not compatible')

    def cmake_args(self):
        # FIXME: Add arguments other than
        # FIXME: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE
        # FIXME: If not needed delete this function
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", 'shared'),
            self.define_from_variant("MeshFields_IS_TESTING", 'tests'),
            self.define("MeshFields_USE_Cabana", True),
        ]
        return args + self.kokkos_cxx_args()

    def kokkos_cxx_args(self):
        # Kokkos's HIP backend needs its users compiled with hipcc unless Kokkos
        # itself was built with an AMD-capable Clang. Following approach from:
        # builtin kokkos-kernels, cmake_args.
        spec = self.spec
        if spec.satisfies("^kokkos+rocm") and not (
            spec.satisfies("^kokkos %cxx=clang") or spec.satisfies("^kokkos %cxx=rocmcc")
        ):
            return [self.define("CMAKE_CXX_COMPILER", spec["hip"].hipcc)]
        return []
