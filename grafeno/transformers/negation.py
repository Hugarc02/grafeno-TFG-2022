from grafeno.transformers.base import Transformer as Base

class Transformer (Base):

    def transform_node (self, ms):
        sem = super().transform_node(ms)
        if ms.get('lemma') == 'not':
            sem['_negation'] = True
            if 'concept' in sem:
                del sem['concept']
        return sem

    def transform_dep (self, dep, pid, cid):
        edge = super().transform_dep(dep, pid, cid)
        parent = self.nodes[edge['parent']]
        child = self.nodes[edge['child']]
        do_del = False
        if '_negation' in child:
            if parent.get('sempos') == 'v' and 'concept' in parent:
                parent['negative'] = True
            else:
                parent['_negation'] = True
        if dep == 'aux' and 'negative' in child:
            parent['negative'] = True
            do_del = True
        return edge


