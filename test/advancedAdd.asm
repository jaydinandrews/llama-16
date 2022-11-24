MAIN: mv OPP1, a
      mv OPP2, b
LOOP: inc b
      dec a
      cmp #0, a
      jnz LOOP    ;Inline comment
      hlt
   ;New line comment

OPP1: .data 3 ;Directive comment
OPP2: .data 5
