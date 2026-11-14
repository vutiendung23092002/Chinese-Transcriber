"""Pin the dependency closure actually installed for runtime, tests and packaging."""
from importlib.metadata import distribution
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
import tomllib

project=tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))['project']
pending=project['dependencies']+project['optional-dependencies']['dev']
versions={}
while pending:
    requirement=Requirement(pending.pop())
    if requirement.marker and not requirement.marker.evaluate({'extra':''}): continue
    name=canonicalize_name(requirement.name)
    if name in versions: continue
    package=distribution(requirement.name); versions[name]=package.version
    pending.extend(package.requires or [])
Path('requirements-lock.txt').write_text('# Windows x64 / Python 3.11: runtime + development tools\n'+'\n'.join(f'{name}=={version}' for name,version in sorted(versions.items()))+'\n',encoding='utf-8')
print(f'Pinned {len(versions)} installed packages')
