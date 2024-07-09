# resumer
a resume generator for personal use, but can be easily extended

The resume template is derived from the awesome-cv project and incorporates features from templates valued at over $1000.

some advanced features are supported but not documented, create an issue if you need them

# required
xelatex, pandoc and python>=3.8

# install
I highly recommend install all pre-requisites using [scoop](https://scoop.sh/)
standard scoop install commands
```
scoop install git
scoop bucket add extras
scoop install pandoc
scoop install xelatex
```

then install via git repo
``` 
pip install git+https://github.com/zackaryw/resumer.git
```

# Cli
to simply generate based on the two profiles available in examples, use
```
resumer profgen [txt_1/tex_1] {path of your data.toml}
```