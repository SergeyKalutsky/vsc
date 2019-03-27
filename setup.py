from setuptools import setup

setup(name='video_censor',
      version='0.0.1',
      description='Real time video recording censor',
      url='https://github.com/SergeyKalutsky/video_censor',
      author='Sergey Kalutsky',
      author_email='skalutsky@gmail.com',
      license='MIT',
      entry_points={'console_scripts': [
        'vsc = video_censor.classifier:main',
      ]},
      install_requires=[
        'pyzmq',
        'mss',
        'numpy',
        'opencv-python',
        'prefetch-generator'
      ],
      packages=['video_censor'],
      zip_safe=True)
