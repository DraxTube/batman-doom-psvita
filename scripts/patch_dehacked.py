#!/usr/bin/env python3
"""Patch d_main.c to call DEH_LoadFromWADs() and DEH_LoadFromFile()
after WAD initialization."""

with open('d_main.c', 'r') as f:
    content = f.read()

# Add include for our DEH loader
if '#include "deh_loader.h"' not in content:
    content = '#include "deh_loader.h"\n' + content

# Add strings.h for strncasecmp
if '#include <strings.h>' not in content and '#include <string.h>' in content:
    content = content.replace('#include <string.h>', '#include <string.h>\n#include <strings.h>', 1)

# Inject DEH loading calls after W_GenerateHashTable()
target = 'W_GenerateHashTable();'
inject = target + '''

    // VITA: Load DEHACKED lumps from PWADs
    DEH_LoadFromWADs();

    // VITA: Load external .DEH file (Batman Doom uses BATMAN.DEH)
    DEH_LoadFromFile("ux0:/data/batmandoom/batman.deh");
    DEH_LoadFromFile("ux0:/data/batmandoom/BATMAN.DEH");
    DEH_LoadFromFile("ux0:/data/batmandoom/Batman.deh");'''

if 'DEH_LoadFromWADs' not in content:
    if target in content:
        content = content.replace(target, inject, 1)
        print('Injected DEH_LoadFromWADs() and DEH_LoadFromFile() after W_GenerateHashTable')
    else:
        print('WARNING: W_GenerateHashTable not found')
else:
    # Already has DEH_LoadFromWADs, add DEH_LoadFromFile if missing
    if 'DEH_LoadFromFile' not in content:
        old = 'DEH_LoadFromWADs();'
        new = old + '''

    // VITA: Load external .DEH file (Batman Doom uses BATMAN.DEH)
    DEH_LoadFromFile("ux0:/data/batmandoom/batman.deh");
    DEH_LoadFromFile("ux0:/data/batmandoom/BATMAN.DEH");
    DEH_LoadFromFile("ux0:/data/batmandoom/Batman.deh");'''
        content = content.replace(old, new, 1)
        print('Added DEH_LoadFromFile() calls')
    else:
        print('DEH loading already present')

with open('d_main.c', 'w') as f:
    f.write(content)
print('d_main.c patched successfully')
