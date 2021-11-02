try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def descriptions():
    with open('README.md') as fh:
        ret = fh.read()
        return ret.split('\n', 1)[0], ret


description, long_description = descriptions()


def version():
    with open('django_thread/__init__.py') as fh:
        for line in fh:
            if line.startswith('__VERSION__'):
                return line.split("'")[1]


setup(
    author='Ross McFaland',
    author_email='rwmcfa1@gmail.com',
    description=description,
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='django_thread',
    packages=('django_thread',),
    python_requires='>=3.6',
    install_requires=('django>=1.6.0',),
    url='https://github.com/ross/django-thread',
    version=version(),
    tests_require=['mock>=4.0.3'],
)
