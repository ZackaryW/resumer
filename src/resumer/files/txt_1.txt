$info.firstname$ $info.lastname$
$info.address$
$info.phonenum$
$info.email$
$if(info.github)$
Github: $info.github$
$endif$
$if(info.linkedin)$
Linkedin: $info.linkedin$
$endif$

$if(info.summary)$
[Summary]
$info.summary$
$endif$

$if(core)$
[Core Competencies]
$for(core.items)$
* $core.items$
$endfor$
$endif$

$if(topqual)$
[Qualifications]
$for(topqual.items)$
* $topqual.items$
$endfor$
$endif$

$for(qual)$
$if(qual.items)$

[[$qual.title$]]
$for(qual.items)$
* $qual.items$
$endfor$
$endif$
$endfor$

$if(exp)$

[Experience]
$for(exp)$
$exp.position$
$exp.organization$, $exp.location$
$exp.datestart$ - $exp.dateend$
$for(exp.items)$
* $exp.items$
$endfor$
$endfor$

$endif$

$if(project)$

[Projects]
$for(project)$
$project.name$ - $project.type$ - $project.position$
$project.datestart$ - $project.dateend$
$for(project.items)$
* $project.items$
$endfor$
$endfor$
$endif$


$if(edu)$
[Education]

$for(edu)$

$edu.degree$
$edu.institution$, $edu.location$
$edu.datestart$ - $edu.dateend$
$for(edu.items)$
* $edu.items$
$endfor$
$endfor$
$endif$