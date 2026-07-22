from setuptools import setup, find_packages

setup(
    name="yadisk-downloader",
    version="1.0.0",
    description="Yandex Disk Downloader with CLI and GUI",
    author="yadisk-downloader contributors",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "playwright>=1.40.0",
        "requests>=2.31.0",
        "imageio-ffmpeg>=0.4.9",
        "customtkinter>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "yadisk-downloader=yadisk_downloader.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Archiving",
    ],
)
