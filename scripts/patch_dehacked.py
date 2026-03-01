#!/usr/bin/env python3
"""Patch d_main.c to call DEH_LoadFromWADs() after WAD initialization."""

with open('d_main.c', 'r') as f:
    content = f.read()

# Add include for our DEH loader
if '#include "deh_loader.h"' not in content:
    content = '#include "deh_loader.h"\n' + content

# Add strings.h for strncasecmp
if '#include <strings.h>' not in content and '#include <string.h>' in content:
    content = content.replace('#include <string.h>', '#include <string.h>\n#include <strings.h>', 1)

# Inject DEH_LoadFromWADs() call after W_GenerateHashTable()
target = 'W_GenerateHashTable();'
inject = target + '\n\n    // VITA: Load DEHACKED lumps from PWADs\n    DEH_LoadFromWADs();'

if 'DEH_LoadFromWADs' not in content:
    if target in content:
        content = content.replace(target, inject, 1)
        print('Injected DEH_LoadFromWADs() after W_GenerateHashTable')
    else:
        print('WARNING: W_GenerateHashTable not found')
else:
    print('DEH_LoadFromWADs already present')

with open('d_main.c', 'w') as f:
    f.write(content)
print('d_main.c patched successfully')
