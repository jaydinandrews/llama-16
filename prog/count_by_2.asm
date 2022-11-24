      mv #0, a        ; reg a will store the values in our sequence
      mv #20, b       ; reg b will store a counter
      io a, OUT       ; print first value 0
      io SPACE, OUT   ; print a space after number
LOOP: add #2, a       ; add two to previous number
      io a, OUT       ; print the value
      io SPACE, OUT   ; print a space for readablity
      dec b           ; decrease the counter
      jnz LOOP        ; check the counter, if zero then continue, if not jump to LOOP
      io NEWLINE, OUT ; print a newline character
      io END, OUT     ; print the ending prompt
      hlt             ; halt the machine

END: .string "END OF SEQUENCE!" ; a text prompt to be printed at the end of counting
SPACE: .string " "              ; helper string to increase readablity
NEWLINE: .data 10               ; decimal value of ASCII newline character
