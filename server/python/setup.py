from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "TrieModule",
        ["bindings/TrieModule.cpp"],
        cxx_std=17
    ),
    Pybind11Extension(
        "MinDist",
        ["bindings/MinDist.cpp"],
        cxx_std=17
    ),
]

setup(
    name="fastwordprocessor",
    version="0.1.0",
    author="Atharva Kerkar",
    description="Fast Trie and MinDist Python bindings using pybind11",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)

