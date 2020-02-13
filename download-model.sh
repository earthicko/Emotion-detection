#!/bin/sh

echo "Downloading model "
export fileid=1FUn0XNOzf-nQV7QjbBPA6-8GLoHNNgv-
export filename=model.h5

curl -L -o $filename --progress-bar 'https://docs.google.com/uc?export=download&id='$fileid

echo "Done"
