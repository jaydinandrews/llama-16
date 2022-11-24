MAIN: mv OPP1, a
      mv OPP2, b
LOOP: inc b
      dec a
      cmp #0, a
      jnz LOOP    ;this is a comment
      hlt
   ;This is also comment

OPP1: .data 3
OPP2: .data 5
