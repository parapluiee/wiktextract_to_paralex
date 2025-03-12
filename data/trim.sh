#!/bin/bash

cat $1 | jq -c 'if .pos == "noun" and .head_templates[0].name == "hi-noun" and has("forms") then {"word": .word, "pos": .pos, forms: .forms} else empty end' | sed '$!s/$/,/' | sed '1 i\{"nouns": [' > hindi_nouns.jsonl
echo ']}' >> hindi_nouns.jsonl


