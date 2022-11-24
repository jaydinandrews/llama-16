MAIN: mv #3, a
      call SUB
      mv #2, b
      hlt

SUB:  inc a
      inc a
      inc a
      ret
