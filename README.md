# resumer
 a resume generator for personal use

# install
install via git repo
``` 
pip install git+https://github.com/zackaryw/resumer.git
```
# usage
CLI
```bash
resumer [profile name]
```

# example data toml
default profiles
```toml

[info]
address =XXXXXXXXXXXXX
city =XXXXXXXXXXXXX
country =XXXXXXXXXXXXX
email =XXXXXXXXXXXXX
firstname =XXXXXXXXXXXXX
github =XXXXXXXXXXXXX
lastname =XXXXXXXXXXXXX
linkedin =XXXXXXXXXXXXX
middleinitial =XXXXXXXXXXXXX
middlename =XXXXXXXXXXXXX
phonenum =XXXXXXXXXXXXX
postalcode =XXXXXXXXXXXXX
province =XXXXXXXXXXXXX


[[exp]]
position =XXXXXXXXXXXXX
organization =XXXXXXXXXXXXX
location =XXXXXXXXXXXXX
datestart=XXXXXXXXXXXXX
dateend =XXXXXXXXXXXXX

# detail points
items=[
    XXXXXXXXXXXXXXXXXXX,
    XXXXXXXXXXXXXXXXXX 
]
    
[[exp]]
position =XXXXXXXXXXXXX
organization =XXXXXXXXXXXXX
location =XXXXXXXXXXXXX
datestart =XXXXXXXXXXXXX
dateend =XXXXXXXXXXXXX
items = []


[[qual]]
pinned =true # if it is pinned, it will display without a title and at the top
items =[]


[[qual]]
title ="Certifications"
items =[
    "First aid attendent",
    "Driver's License",
]

[[edu]]
degree =XXXXXXXXXXXXX
school =XXXXXXXXXXXXX
datestart =XXXXXXXXXXXXX
dateend =XXXXXXXXXXXXX
location =XXXXXXXXXXXXX
items =[]

```

# template syntaxes
```
<br> will act as a line break
```

# acknowledgements
- [awesome-cv](https://github.com/posquit0/Awesome-CV)
> this project made slight modifications to the cls file

