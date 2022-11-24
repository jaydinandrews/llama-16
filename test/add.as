MAIN: mv #3, r0
      mv #5, r1
LOOP: inc r1
      dec r0
      cmp #0, r0
      jnz LOOP    ;this is a comment
      hlt
   ;This is also comment
