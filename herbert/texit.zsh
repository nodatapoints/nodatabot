#!/bin/zsh

# ja das geht auch mit bash.

working_dir=$(mktemp -d)
cd $working_dir

cat - > main.tex
if ! latexmk main.tex &>/dev/null; then
  echo "FAILED."
  exit 3
fi
dvipng -D 600 main.dvi &>/dev/null
convert	main*.png -bordercolor white -border x20% main.png
echo $working_dir/main.png
