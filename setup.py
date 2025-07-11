from setuptools import setup, find_packages
setup(
    name='collaboration_v8',
    version='1.0.0',
    packages=find_packages(include=['collaboration','collaboration.*']),
    install_requires=[
        'pandas','numpy','requests',
        'scikit-learn','streamlit','plotly','scipy'
    ],
    entry_points={'console_scripts': ['run-collab=main:run_backtest']},
    author='Your Name',
    description='v8: Continuous α, doubles, in-play & what-if GUI'
)
