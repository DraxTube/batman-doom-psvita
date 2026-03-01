#!/usr/bin/env python3
"""Patch r_things.c to allow PWAD sprites to override IWAD sprites
instead of calling I_Error on duplicates."""

with open('r_things.c', 'r') as f:
    content = f.read()

patched = False

# 1. Fix rotation=0 duplicate: "multip rot=0 lump"
#    Change I_Error to just silently override
old1 = '''    if (sprtemp[frame].rotate == false)
\t    I_Error ("R_InitSprites: Sprite %s frame %c has "
\t\t     "multip rot=0 lump", spritename, 'A'+frame);'''
new1 = '''    if (sprtemp[frame].rotate == false)
\t    { /* VITA: allow PWAD override instead of error */ }'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    patched = True
    print('Patched: rot=0 multip override')

# 2. Fix rotation=0 vs rotations conflict
old2_a = '''    if (sprtemp[frame].rotate == true)
\t    I_Error ("R_InitSprites: Sprite %s frame %c has rotations "
\t\t     "and a rot=0 lump", spritename, 'A'+frame);

\tsprtemp[frame].rotate = false;'''
new2_a = '''    if (sprtemp[frame].rotate == true)
\t    { /* VITA: allow PWAD rot=0 to override rotations */ }

\tsprtemp[frame].rotate = false;'''

if old2_a in content:
    content = content.replace(old2_a, new2_a, 1)
    patched = True
    print('Patched: rot=0 vs rotations override')

# 3. Fix the reverse: rotations vs rot=0 conflict
old2_b = '''    // the lump is only used for one rotation
    if (sprtemp[frame].rotate == false)
\tI_Error ("R_InitSprites: Sprite %s frame %c has rotations "
\t\t "and a rot=0 lump", spritename, 'A'+frame);'''
new2_b = '''    // the lump is only used for one rotation
    if (sprtemp[frame].rotate == false)
\t{ /* VITA: allow PWAD rotations to override rot=0 */ }'''

if old2_b in content:
    content = content.replace(old2_b, new2_b, 1)
    patched = True
    print('Patched: rotations vs rot=0 override')

# 4. Fix the main duplicate error: "has two lumps mapped to it"
old3 = '''    if (sprtemp[frame].lump[rotation] != -1)
\tI_Error ("R_InitSprites: Sprite %s : %c : %c "
\t\t "has two lumps mapped to it",
\t\t spritename, 'A'+frame, '1'+rotation);'''
new3 = '''    if (sprtemp[frame].lump[rotation] != -1)
\t{ /* VITA: allow PWAD to override existing sprite lump */ }'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    patched = True
    print('Patched: duplicate lump override (main fix)')

if patched:
    with open('r_things.c', 'w') as f:
        f.write(content)
    print('r_things.c patched successfully')
else:
    print('WARNING: No patterns matched in r_things.c - may already be patched')
