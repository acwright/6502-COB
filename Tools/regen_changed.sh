#!/bin/zsh
# Regenerates every revision in this repository whose schematic or PCB has uncommitted changes, one after another.
# With --all, in all five repositories, which sit beside this one.
T=${0:A:h}; ROOT=${T:h}; K=${ROOT:h}; THIS=${${ROOT:t}#6502-}
repos=($THIS); [[ "$1" == --all ]] && repos=(ACE COB DEV KIM VCS)
for r in $repos; do
  git -C $K/6502-$r status --porcelain -- Hardware | sed -E 's/^.. "?//; s/"$//' | grep -E '\.kicad_(sch|pcb)$' | sed -E 's|/[^/]*$||' | sort -u | while read d; do
    b=${d:h:t}; v=${${d:t}#Rev }
    echo "== $r $b $v"; python3 $T/regen.py $r "$b" "$v" 2>&1 | tail -6
  done
done
echo all-done
