/*
 * Minimal DEHACKED lump parser for doomgeneric.
 * Self-contained: uses ONLY doomgeneric's native types.
 * Handles Thing, Frame, Pointer, Weapon, Text blocks.
 */
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "d_items.h"
#include "d_think.h"
#include "deh_loader.h"
#include "doomtype.h"
#include "info.h"
#include "sounds.h"
#include "w_wad.h"
#include "z_zone.h"


/* ---- parser state ---- */
static const char *dp;   /* current read position */
static const char *dend; /* end of data */

static int deh_readline(char *buf, int sz) {
  if (dp >= dend)
    return 0;
  int i = 0;
  while (dp < dend && i < sz - 1) {
    char c = *dp++;
    if (c == '\n')
      break;
    if (c != '\r')
      buf[i++] = c;
  }
  buf[i] = '\0';
  return 1;
}

static int deh_readchars(char *buf, int n) {
  int i = 0;
  while (i < n && dp < dend)
    buf[i++] = *dp++;
  buf[i] = '\0';
  return i;
}

static char *skipws(char *s) {
  while (*s == ' ' || *s == '\t')
    s++;
  return s;
}

static int getval(const char *l) {
  const char *eq = strchr(l, '=');
  return eq ? atoi(eq + 1) : 0;
}

static int pfx(const char *s, const char *p) {
  return strncasecmp(s, p, strlen(p)) == 0;
}

static int blank(const char *l) {
  while (*l == ' ' || *l == '\t')
    l++;
  return (*l == '\0' || *l == '#');
}

/* ---- save original action pointers ---- */
static actionf_t orig_act[NUMSTATES];
static int act_saved = 0;
static void save_act(void) {
  int i;
  if (act_saved)
    return;
  for (i = 0; i < NUMSTATES; i++)
    orig_act[i] = states[i].action;
  act_saved = 1;
}

/* ---- Thing ---- */
static void p_thing(int num) {
  char line[256];
  if (num < 1 || num > NUMMOBJTYPES)
    return;
  mobjinfo_t *m = &mobjinfo[num - 1];
  while (deh_readline(line, sizeof(line))) {
    char *l = skipws(line);
    if (blank(l))
      return;
    int v = getval(l);
    if (pfx(l, "ID #"))
      m->doomednum = v;
    else if (pfx(l, "Initial frame"))
      m->spawnstate = v;
    else if (pfx(l, "Hit points"))
      m->spawnhealth = v;
    else if (pfx(l, "First moving frame"))
      m->seestate = v;
    else if (pfx(l, "Alert sound"))
      m->seesound = v;
    else if (pfx(l, "Reaction time"))
      m->reactiontime = v;
    else if (pfx(l, "Attack sound"))
      m->attacksound = v;
    else if (pfx(l, "Injury frame"))
      m->painstate = v;
    else if (pfx(l, "Pain chance"))
      m->painchance = v;
    else if (pfx(l, "Pain sound"))
      m->painsound = v;
    else if (pfx(l, "Close attack frame"))
      m->meleestate = v;
    else if (pfx(l, "Far attack frame"))
      m->missilestate = v;
    else if (pfx(l, "Death frame"))
      m->deathstate = v;
    else if (pfx(l, "Exploding frame"))
      m->xdeathstate = v;
    else if (pfx(l, "Death sound"))
      m->deathsound = v;
    else if (pfx(l, "Speed"))
      m->speed = v;
    else if (pfx(l, "Width"))
      m->radius = v;
    else if (pfx(l, "Height"))
      m->height = v;
    else if (pfx(l, "Mass"))
      m->mass = v;
    else if (pfx(l, "Missile damage"))
      m->damage = v;
    else if (pfx(l, "Action sound"))
      m->activesound = v;
    else if (pfx(l, "Bits"))
      m->flags = v;
    else if (pfx(l, "Respawn frame"))
      m->raisestate = v;
  }
}

/* ---- Frame ---- */
static void p_frame(int num) {
  char line[256];
  if (num < 0 || num >= NUMSTATES)
    return;
  state_t *s = &states[num];
  while (deh_readline(line, sizeof(line))) {
    char *l = skipws(line);
    if (blank(l))
      return;
    int v = getval(l);
    if (pfx(l, "Sprite number"))
      s->sprite = (spritenum_t)v;
    else if (pfx(l, "Sprite subnumber"))
      s->frame = v;
    else if (pfx(l, "Duration"))
      s->tics = v;
    else if (pfx(l, "Next frame"))
      s->nextstate = (statenum_t)v;
    else if (pfx(l, "Unknown 1"))
      s->misc1 = v;
    else if (pfx(l, "Unknown 2"))
      s->misc2 = v;
  }
}

/* ---- Pointer ---- */
static void p_pointer(const char *hdr) {
  char line[256];
  const char *p = strchr(hdr, '(');
  int fr = 0;
  if (!p || sscanf(p, "(Frame %d)", &fr) != 1)
    return;
  if (fr < 0 || fr >= NUMSTATES)
    return;
  while (deh_readline(line, sizeof(line))) {
    char *l = skipws(line);
    if (blank(l))
      return;
    if (pfx(l, "Codep Frame")) {
      int c = getval(l);
      if (c >= 0 && c < NUMSTATES)
        states[fr].action = orig_act[c];
    }
  }
}

/* ---- Weapon ---- */
static void p_weapon(int num) {
  char line[256];
  if (num < 0 || num >= NUMWEAPONS)
    return;
  weaponinfo_t *w = &weaponinfo[num];
  while (deh_readline(line, sizeof(line))) {
    char *l = skipws(line);
    if (blank(l))
      return;
    int v = getval(l);
    if (pfx(l, "Ammo type"))
      w->ammo = (ammotype_t)v;
    else if (pfx(l, "Deselect frame"))
      w->upstate = v;
    else if (pfx(l, "Select frame"))
      w->downstate = v;
    else if (pfx(l, "Bobbing frame"))
      w->readystate = v;
    else if (pfx(l, "Shooting frame"))
      w->atkstate = v;
    else if (pfx(l, "Firing frame"))
      w->flashstate = v;
  }
}

/* ---- Text (sprite name replacement) ---- */
#define MAX_REN 256
static char ren_buf[MAX_REN][5];
static int n_ren = 0;

static void p_text(int old_len, int new_len) {
  char otxt[512], ntxt[512];
  if (old_len > 500 || new_len > 500) {
    deh_readchars(otxt, old_len > 500 ? 500 : old_len);
    deh_readchars(ntxt, new_len > 500 ? 500 : new_len);
    return;
  }
  deh_readchars(otxt, old_len);
  otxt[old_len] = '\0';
  deh_readchars(ntxt, new_len);
  ntxt[new_len] = '\0';

  /* Sprite name replacement (4 chars) */
  if (old_len == 4 && new_len == 4 && n_ren < MAX_REN) {
    int i;
    for (i = 0; i < NUMSPRITES; i++) {
      if (strncmp(sprnames[i], otxt, 4) == 0) {
        memcpy(ren_buf[n_ren], ntxt, 4);
        ren_buf[n_ren][4] = '\0';
        sprnames[i] = ren_buf[n_ren];
        n_ren++;
        printf("  DEH: sprite %s -> %s\n", otxt, ntxt);
        break;
      }
    }
  }
}

/* ---- skip block (Misc, Cheat, Ammo, Sound, etc.) ---- */
static void p_skip(void) {
  char line[256];
  while (deh_readline(line, sizeof(line))) {
    if (blank(skipws(line)))
      return;
  }
}

/* ---- Public API ---- */
void DEH_LoadFromWADs(void) {
  unsigned int i;
  int loaded = 0;
  char line[256];

  save_act();

  for (i = 0; i < numlumps; i++) {
    if (strncasecmp(lumpinfo[i].name, "DEHACKED", 8) != 0)
      continue;
    int len = W_LumpLength(i);
    if (len <= 0)
      continue;

    char *data = (char *)malloc(len + 1);
    if (!data)
      continue;
    memcpy(data, W_CacheLumpNum(i, PU_CACHE), len);
    data[len] = '\0';

    dp = data;
    dend = data + len;

    while (deh_readline(line, sizeof(line))) {
      char *l = skipws(line);
      if (blank(l))
        continue;

      if (pfx(l, "Thing "))
        p_thing(atoi(l + 6));
      else if (pfx(l, "Frame "))
        p_frame(atoi(l + 6));
      else if (pfx(l, "Pointer "))
        p_pointer(l);
      else if (pfx(l, "Weapon "))
        p_weapon(atoi(l + 7));
      else if (pfx(l, "Text ")) {
        int ol = 0, nl = 0;
        sscanf(l + 5, "%d %d", &ol, &nl);
        p_text(ol, nl);
      } else if (pfx(l, "Ammo ") || pfx(l, "Misc ") || pfx(l, "Sound ") ||
                 pfx(l, "Cheat "))
        p_skip();
      /* else: header lines, comments, etc. - skip */
    }

    free(data);
    loaded++;
    printf("  DEH: processed lump %u (%d bytes)\n", i, len);
  }
  if (loaded > 0)
    printf("  DEH: %d DEHACKED lump(s) loaded\n", loaded);
}
