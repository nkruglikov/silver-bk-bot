from distutils.core import setup
import py2exe

setup(
    console=['interpreter.py'],
    data_files=[('', ['config.ini', 'README.txt']),
                ('routes', ['routes/Разворот.txt',
                            'routes/Двойной разворот.txt'])]
    )
