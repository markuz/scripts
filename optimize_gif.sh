convert giphy-2.gif -geometry 200 -dither none -deconstruct -layers optimize -matte -depth 8 \( -clone 0--1 -background none +append -quantize transparent -colors 32 -unique-colors -write mpr:cmap +delete \) -map mpr:cmap unicorn.gif
