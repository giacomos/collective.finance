from setuptools import setup, find_packages
import os

version = '0.1'
long_description = open("README.rst").read() + "\n" + \
    open(os.path.join("docs", "HISTORY.txt")).read(),

setup(name='collective.finance',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Development Status :: 2 - Pre-Alpha",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
      ],
      keywords='Plone Python Finance Manager',
      author='Giacomo Spettoli',
      author_email='giacomo.spettoli@gmail.com',
      url='https://github.com/giacomos/collective.finance',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'python-money',
          'qifparse',
          'ofxparse',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing[robot]'
          ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
