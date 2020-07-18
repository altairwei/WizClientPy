from setuptools import setup, find_packages

setup(
    name="WizCli",
    version="0.0.1",
    python_requires='>3.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "click_repl",
        "prompt_toolkit",
        "requests",
        "colorama",
        "pygments"
    ],
    entry_points='''
        [console_scripts]
        wizcli=wizclientpy.wizcli:wizcli
    ''',
)
