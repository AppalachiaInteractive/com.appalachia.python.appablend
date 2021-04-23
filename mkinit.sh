#!/bin/bash

mapfile -t array < <(find ./appablend -type d -not -name __pycache__)

indexes=( $(
    for i in "${!array[@]}" ; do
        printf '%s %s %s\n' $i "${#array[i]}" "${array[i]}"
    done | sort -nrk2,2 -rk3 | cut -f1 -d' '
))

for i in "${indexes[@]}" ; do
    sorted+=("${array[i]}")
done

for dir in "${sorted[@]}"; do
    echo "${dir}"
    mkinit -relative -i "$dir"
done

