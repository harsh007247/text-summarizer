import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

REPO_NAME = "text-summarizer"
AUTHOR_USER_NAME = "harsh007247"
SRC_REPO = "testsummarizer"
AUTHOR_EMAIL = "harshpaliwa104@gmail.com"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A small package for nlp app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)