#!/usr/bin/env python3
"""Patch r_things.c to allow PWAD sprites to override IWAD sprites.

Instead of trying to match exact whitespace (tabs vs spaces), we use
line-by-line scanning to find and neutralize the I_Error calls related
to duplicate sprite lumps.
"""
import re

with open('r_things.c', 'r') as f:
    lines = f.readlines()

count = 0

# We need to find all I_Error calls related to sprite duplicates and
# replace them with empty blocks.
# The patterns are:
#   1) "multip rot=0 lump"
#   2) "has rotations" + "and a rot=0 lump"  (two occurrences)
#   3) "has two lumps mapped to it"

i = 0
while i < len(lines):
    line = lines[i]

    # Match lines containing these specific I_Error messages
    if 'I_Error' in line and (
        'multip rot=0 lump' in line or
        'and a rot=0 lump' in line or
        'has two lumps mapped to it' in line or
        'has rotations' in line
    ):
        # This is a single-line I_Error with the message
        # Replace: I_Error(...); with { /* VITA: allow override */ }
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = indent + '{ /* VITA: allow PWAD override */ }\n'
        # Remove continuation lines (lines that are just string literals or args)
        j = i + 1
        while j < len(lines):
            stripped = lines[j].strip()
            if stripped.startswith('"') or stripped.startswith('spritename') or stripped == '':
                # This is a continuation of the I_Error call
                if stripped.endswith(');'):
                    lines[j] = ''
                    j += 1
                    break
                lines[j] = ''
                j += 1
            else:
                break
        count += 1
        i = j
        continue

    # Also match the case where I_Error starts on one line and the message is on the next
    if 'I_Error' in line and 'R_InitSprites' in line:
        # Check if next lines contain our target messages
        combined = line
        for k in range(1, 4):
            if i + k < len(lines):
                combined += lines[i + k]
        if ('multip rot=0 lump' in combined or
            'and a rot=0 lump' in combined or
            'has two lumps mapped to it' in combined):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = indent + '{ /* VITA: allow PWAD override */ }\n'
            # Remove continuation lines
            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if (stripped.startswith('"') or
                    stripped.startswith('spritename') or
                    stripped.startswith("'") or
                    stripped == ''):
                    should_stop = stripped.endswith(');')
                    lines[j] = ''
                    j += 1
                    if should_stop:
                        break
                else:
                    break
            count += 1
            i = j
            continue

    i += 1

if count > 0:
    with open('r_things.c', 'w') as f:
        f.writelines(lines)
    print(f'Patched {count} I_Error calls in R_InstallSpriteLump')
    print('r_things.c patched successfully')
else:
    print('WARNING: No sprite duplicate I_Error calls found - may already be patched')
