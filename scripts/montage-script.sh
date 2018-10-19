#!/bin/bash
for i in {000..017}; do FOLDER=`printf "%03d\n" $i`; montage -mode Concatenate -tile x1 ${FOLDER}/roastimage* ${FOLDER}.png; done



#montage -mode Concatenate -tile x1 *.png outs/eadc-8.png
