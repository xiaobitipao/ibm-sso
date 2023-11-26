from setuptools import find_packages, setup


def read_files(files):
    data = []
    for file in files:
        with open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)


long_description = read_files(['README.md', 'CHANGELOG.md'])

meta = {}
with open('./src/ibm_sso/version.py', encoding='utf-8') as f:
    exec(f.read(), meta)

setup(
    name='ibm_sso',
    description='IBM SSO Self-Service Provisioner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=meta['__version__'],
    author='xiaobitipao',
    author_email='xiaobitipao@gmail.com',
    url='https://github.com/xiaobitipao/ibm-sso',
    keywords=['sso', 'fastapi', 'oidc'],
    packages=find_packages('src'),    # include all packages under src
    package_dir={'': 'src'},          # tell distutils packages are under src
    python_requires='>=3.10',
    license='BSD-3-Clause',
    classifiers=[
        # https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ]
)
