from collections import deque
from nltk.corpus import wordnet as wn

from .pos_extract import Transformer as PosExtract

class Transformer (PosExtract):

    def __init__ (self):
        super().__init__(sempos = {'noun': 'n'})
        self.node_from_concept = dict()
        self.min_depth = 4
        self.sentences = []

    def pre_process (self, tree, graph):
        self.dropped = []

    def transform_node (self, msnode):
        sem = super().transform_node(msnode)
        concept = sem.get('concept')
        # Only one node for each concept
        if concept == None:
            return None
        if concept in self.node_from_concept:
            self.dropped.append(self.node_from_concept[concept])
            return None
        ss = wn.synsets(concept, 'n')
        if len(ss)<1:
            return None
        # WSD by MFS
        sem['synset'] = ss[0]
        return sem

    def post_insertion (self, sentence_nodes, graph):
        g = graph._g
        # Record the concept nodes
        for n in sentence_nodes:
            concept = g.node[n]['concept']
            self.node_from_concept[concept] = n
        # Record the sentence
        self.sentences.append(sentence_nodes + self.dropped)
        # Extend with hypernyms
        to_extend = deque(sentence_nodes)
        while len(to_extend)>0:
            n = to_extend.popleft()
            node = g.node[n]
            ss = node['gram']['synset']
            for cc in ss.hypernyms() + ss.instance_hypernyms():
                depth = ss.min_depth()
                if depth < self.min_depth:
                    continue
                concept = cc.lemmas()[0].name()
                if concept not in self.node_from_concept:
                    nid = graph.add_node(concept,gram={'synset':cc,'sempos':'n'})
                    to_extend.append(nid)
                    self.node_from_concept[concept] = nid
                else:
                    nid = self.node_from_concept[concept]
                graph.add_edge(n, nid, 'HYP', {'weight':depth/(depth+1)})
