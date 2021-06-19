import setuptools


setuptools.setup(name='barely',
                 packages=['barely'],
                 version='0.9.0',
                 description='barely is a lightweight, but highly extensible static site generator written in pure python.',
                 keyword=['static site generator', 'jinja2', 'markdown', 'web development'],
                 url='https://github.com/charludo/barely',
                 download_url='https://github.com/charludo/barely/archive/v_090.tar.gz',
                 author='Charlotte Hartmann Paludo',
                 author_email='contact@charlotteharludo.com',
                 license='GPL-3.0',
                 packages=setuptools.find_packages(),
                 zip_safe=False,
                 entry_points={"console_scripts": ["barely = barely.cli:run"]},
                 install_requires=[
                    "click>=8.0.0",
                    "mock>=4.0.0",
                    "pyyaml>=5.3.0",
                    "watchdog>=2.0.0",
                    "pillow>=8.0.0",
                    "GitPython>=3.0.0",
                    "pygments>=2.5.0",
                    "libsass>=0.21.0",
                    "pysftp>=0.2.5",
                    "livereload>=2.5.0",
                    "binaryornot>=0.4.0",
                    "jinja2>=3.0.0",
                    "mistune==2.0.0rc1",
                    "calmjs>=3.3.0"
                 ],
                 classifiers=[
                    'Development Status :: 4 - Beta',
                    'Intended Audience :: Developers',
                    'Topic :: Text Processing :: Markup :: HTML',
                    'Topic :: Text Processing :: General',
                    'Topic :: Software Development :: Build Tools',
                    'Topic :: Software Development',
                    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                    'Natural Language :: English',
                    'Programming Language :: Python :: 3.9',
                    'Environment :: Console',
                    'Operating System :: OS Independent'
                  ],
                 )
