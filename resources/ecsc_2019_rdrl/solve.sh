#!/bin/sh

while read p; do
  echo "$p"
  ./cipher.py "flag.png.enc" "$p" > out
  if ! pngcheck out | grep 'ERROR'; then
     echo "MATCH"
     exit
  fi
done <solutions_list.txt
