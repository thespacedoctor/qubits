from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='qubits',
      version='0.2',
      description='',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
      ],
      keywords='utilities dryx',
      url='https://github.com/thespacedoctor/qubits',
      author='thespacedoctor',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=['qubits'],
      install_requires=[
         'dryxPython',
         'pysynphot',
         'docopt',
         'nose',
         'numpy'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': ['qubits=qubits.command_line:qubits'],
      },
      zip_safe=False)
