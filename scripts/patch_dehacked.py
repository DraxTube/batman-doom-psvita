#!/usr/bin/env python3
"""Patch d_main.c to auto-load DEHACKED lumps from PWADs."""
import sys

with open('d_main.c', 'r') as f:
    content = f.read()

# Ensure strings.h is included for strncasecmp
if '#include <strings.h>' not in content and '#include <string.h>' in content:
    content = content.replace('#include <string.h>', '#include <string.h>\n#include <strings.h>', 1)

# Find W_GenerateHashTable(); and inject DEHACKED loading right after it
inject_after = 'W_GenerateHashTable();'
inject_code = """W_GenerateHashTable();

    // VITA: Auto-load DEHACKED lumps from PWADs for total conversion support
    {
        int i, loaded = 0;
        for (i = numiwadlumps; i < numlumps; ++i)
        {
            if (!strncasecmp(lumpinfo[i].name, "DEHACKED", 8))
            {
                DEH_LoadLump(i, false, false);
                loaded++;
            }
        }
        if (loaded > 0)
            printf("  loaded %d DEHACKED lumps from PWAD files.\\n", loaded);
    }"""

if inject_after in content:
    content = content.replace(inject_after, inject_code, 1)
    print('Injected DEHACKED loading after W_GenerateHashTable')
else:
    print('WARNING: W_GenerateHashTable not found in d_main.c')
    sys.exit(1)

with open('d_main.c', 'w') as f:
    f.write(content)

print('d_main.c patched successfully')
