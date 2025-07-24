from setuptools import setup, Extension

setup(
    name='TrieModule',
    ext_modules=[
        Extension(
            'TrieModule',
            sources=['TrieModule.cpp'],
            extra_compile_args=['-std=c++11']
        )
    ]
)

