MAIN: mv #3, a
      mv #5, b
LOOP: inc b
      dec a
      cmp #0, a
      jnz LOOP    ;this is a comment
      hlt
   ;This is also comment
