from distutils.core import setup

setup(
    name='MapXml',
    version='0.2',
    packages=['mapxml'],
    url='http://www.gecoder.net/mapxml',
    license='',
    author='gecoder',
    author_email='gogzor@gmail.com',
    description='Map any XML/HTML to dictionary using flexible object-oriented schemas.',
    install_requires=['lxml']
)