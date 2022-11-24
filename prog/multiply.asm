START: io PROMPT, OUT
       io a, IN
       mv a, [6000]
       io PROMPT, OUT
       io c, IN
       mv c, [6001]
       dec c
LOOP:  add [6000], a
       dec c
       jnz LOOP
       mv [6000], b
       io b, OUT
       io TIMES, OUT
       mv [6001], c
       io c, OUT
       io IS, OUT
       io a, OUT
       io NL, OUT
       hlt

PROMPT: .string "Enter a number: "
TIMES:  .string " times "
IS:     .string " is "
NL:     .data 10
