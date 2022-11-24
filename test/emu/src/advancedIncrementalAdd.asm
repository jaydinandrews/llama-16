MAIN: mv OPP1, b
      mv OPP2, c
LOOP: inc c
      dec b
      cmp #0, b
      jnz LOOP    ;Inline comment
      hlt
   ;New line comment

OPP1: .data 3 ;Directive comment
OPP2: .data 5
