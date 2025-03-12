#order
#ind.prs.1.pl
#mood.tense.person.num
import json
from itertools import chain
from epitran import Epitran



class Json_Processor():
    def __init__(self, lexemes_list, feat_csv_path, example_tags, feature_order, cells_path=None):
        self.cell_transformer = CellTransformer(feat_csv_path, example_tags, feature_order)
        self.full_list = lexemes_list
        self.lexemes_list = [lex["word"] for lex in lexemes_list]
        self.real_tags = self.__get_real_tags__()
        self.calculated_cells = set()
        self.csv_cells = set()
        if cells_path != None:
            self.csv_cells = self.__get_cell_ids__(cells_path)
        self.paradigms = self.__get_all_paradigms__()


    def __get_real_tags__(self):
        out = set()
        for lexeme in self.full_list:
            for form in lexeme["forms"]:
                out = out.union(set(form["tags"]))
            
        return out
    
    def __get_cell_ids__(self, cells_path):
        cells = list()
        firstline = False
        with open(cells_path) as f:
            for line in f:
                if (firstline):
                    line = line.split(',')
                    cells.append(line[0].replace("\n", ""))
                else:
                    firstline = True
        return set(cells)

    def compare_real_to_features(self):
        intersection = set(self.cell_transformer.label_to_id.keys()) - self.real_tags
        if (len(intersection) == 0):
            return False
        else:
            return intersection

    def __get_all_paradigms__(self):
        verb_paradigm = dict()
        for lexeme in self.full_list:
            lexeme_word = lexeme["word"]
            verb_paradigm[lexeme_word] = list()
            if not lexeme["forms"]:
                print(lexeme_word)
            for form in lexeme["forms"]:
                paradigm_cell = self.cell_transformer.make_entry_form(form, lexeme_word)

                self.calculated_cells.add(paradigm_cell[1])
                verb_paradigm[lexeme_word].append(paradigm_cell)

        return verb_paradigm

    def get_unfilled_lexemes(self):
        return [lexeme for lexeme in self.lexemes_list if not self.check_completeness(self.paradigms[lexeme])]

    def remove_unfilled(self):
        lexemes = set(self.get_unfilled_lexemes())
        
        for lexeme in lexemes:
            del self.paradigms[lexeme]
        
    def check_completeness(self, single_paradigm):
        filled_cells = [form[1] for form in single_paradigm]
        
        cells = [csv_cell for csv_cell in self.csv_cells if csv_cell not in filled_cells]
        return not cells
    
    def get_paradigms(self):
        return self.paradigms

class CellTransformer():
    def __init__(self, feat_csv_path, example_tags, feature_order, id_ind=0, label_ind=1, feat_ind=2, pos_ind=3, canorder_ind=4):
        #necessary, as wikilabels do not 1 to 1 correspond with id labels
        self.label_to_id = dict()
        self.features = dict()
        #all verbs here, should add this functionality
        self.pos = dict()
        #still dont know what this is for
        self.label_canon_order = dict()
        #not defined in paralex, should be
        self.feature_order = feature_order
        with open(feat_csv_path) as f:
            firstline = False
            for line in f:
                if (firstline):
                    line = line.split(',')
                    #pull all features from csv
                    feature = line[feat_ind]
                    label = line[label_ind]
                    #one to one
                    self.label_to_id[label] = line[id_ind]
                    #all labels of this feature type
                    #necessary to correctly order
                    if (feature not in self.features.keys()):
                        self.features[feature] = set([label])
                    else:
                        self.features[feature].add(label)
                    #haven't used, no ida what canon order is for
                    self.label_canon_order[label] = line[canorder_ind]
                else:
                    firstline = True
        
    def make_entry_form(self, form, lexeme):
        new_cell = self.form_tags_to_cellid(form["tags"])
        ipa = "NOIPA"
        if ("ipa" in form.keys()):
            ipa = " ".join(form["ipa"].replace(".", "").replace("/", ""))
        else:
            ipa = ipa_translator.transliterate(form["form"])

        ortho = form["form"]
        form_id = lexeme + "_" + new_cell.replace(".", "")
        return ([form_id, new_cell, ortho, ipa])
    
    def form_tags_to_cellid(self, tags):
        #REALLY scuffed, need to enforce by having a reverse label_feature dict, or perhaps a set length list of either empty or filled strings
        #main idea: label_to_feature_id: label -> feature_id
        #output = list : len = len(features)
            #["", "",......,""]
        #output[feature_id] = label
        out = ""
        for feature in self.feature_order:
            for label in tags:
                if label in self.features[feature]:
                    out += self.label_to_id[label] + "."
        #"also scuffed, this removes final .
        return out[0:len(out)-1]
        
#just gets cells from cells.csv





#creates final entry, form_id is the incorrect structure


#damn, iterative cleaning sucks

#super chill, necessary
replacement_pairs={
    "direct" : ["nominative"]
}

#probably chill, save for table-tags and inflection template
#just need to study the json structure
disallowed_tags = [
    "table-tags",
    "romanization",
    "class",
    "Urdu",
    "feminine", #gender may be important
    "masculine",
    "inflection-template",
    "canonical"
]

#based
irrelevant_tags = [
    
]

extract_tags = {
    "tag-marked": ("field to extract", "new_name")
}

#this should be apart of the standard
feature_order = [
 "Case", "Number"
]


json_path = "data/hindi_nouns.jsonl"
word_type = "nouns"
features_csv = "data/paralex_files/hindi_nouns_features.csv"
cells_csv = "data/paralex_files/hindi_nouns_cells.csv"
f = open(json_path)
noun_list = json.loads(f.read())[word_type]


example_tags = set()
#necessary in final product, should add somewhere else in the pipeline, or go over every option
for form in noun_list[0]["forms"]:
    example_tags = example_tags.union(set(form["tags"]))


#long signature, I think necessary
#cell_transform = CellTransformer("vlexique/vlexique_features.csv", example_tags, feature_order)


noun_list = clean_data(noun_list, replacement_pairs, disallowed_tags, irrelevant_tags)

ipa_translator = Epitran('hin-Deva')

processor = Json_Processor(noun_list, features_csv, example_tags, feature_order, cells_path=cells_csv)
paradigms = processor.get_paradigms()
unfilled_lexemes = processor.get_unfilled_lexemes()

print(paradigms)
print(len(unfilled_lexemes))
print(len(set(unfilled_lexemes)))
#processor.remove_unfilled()
#print(len(processor.get_unfilled_lexemes()))


#certain lexemes have no plural
#
