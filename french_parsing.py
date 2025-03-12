#super chill, necessary
replacement_pairs={
    "first-person": ["first person"],
    "second-person": ["second person"],
    "third-person": ["third person"],
    'gerund': ['present', 'participle'],
    'imperative': ['imperative', 'present'],
    'conditional': ['conditional', 'present']
}

#probably chill, save for table-tags and inflection template
#just need to study the json structure
disallowed_tags = [
    "table-tags",
    "inflection-template",
    "multiword-construction",
    "anterior"
]

#based
irrelevant_tags = [
    "historic"
]


#this should be apart of the standard
feature_order = [
 "Mode", "Tense", "Gender", "Person", "Number"
]