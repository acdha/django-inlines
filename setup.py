try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


def README():
    with open('README', 'r') as readme:
        return readme.read()


setup(
    name='inlines',
    version='0.0.5',
    description='Embed just about anything.',
    author='Mike Urbanski',
    author_email='michael.c.urbanski@gmail.com',
    url='http://github.com/mikeurbanski/django-inlines/',
    long_description=README(),
    packages=['django_inlines', 'django_inlines.inlines'],
    package_data={},
    zip_safe=False,
    requires=['Django(>=1.6)'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'],)
