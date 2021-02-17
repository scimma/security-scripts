"""
L2 to L3 data products

This module turns L2 data product (all interconnections graph)
into L2 data products (graph with subgraphs/clusters describing service dependencies)
"""

from security_scripts.information.lib import measurements
import networkx as nx
from networkx_query import search_direct_relationships
from networkx_query import search_nodes
import json
import pyjq
import random
import pydot
import csv
import os


class Acquire(measurements.Dataset):
    """
    Process "universe" graph, elevating it from L2 to L3

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)

        # dir enforcement
        self.l2_path = args.report_path + '/L2/'
        self.l3_path = args.report_path + '/L3/'
        if not os.path.exists(self.l3_path):
            os.makedirs(self.l3_path)

        # init the graph stuff
        # load in the graph and node tags
        print('Loading universe.dot...')
        self.G = nx.drawing.nx_pydot.read_dot(self.l2_path + 'universe.dot')
        self.G_labels = nx.get_node_attributes(self.G, 'label')  # reference this to get label

        self.make_data()
        self.clean_data()

    def get_self_formula(self, service, function, definitions_self):
        pass

    def type_collector(self, labels):
        typ = []
        for label in labels:
            typ.append(labels[label].replace(label,"").replace("\n","")[1:-1])
        return list(set(typ))

    def invertHex(self, hexNumber):
        # invert a hex number
        inverse = hex(abs(int(hexNumber, 16) - 255))[2:]
        # if the number is a single digit add a preceding zero
        if len(inverse) == 1:
            inverse = '0' + inverse
        return inverse

    def invertHexFull(self, hexNumber):
        R = self.invertHex(hexNumber[0:2])
        G = self.invertHex(hexNumber[2:4])
        B = self.invertHex(hexNumber[4:])
        return R + G + B

    def nx_to_pywiz(self, type_colors, subgraphs):
        # build pydot from scratch
        P = pydot.Dot(graph_type='graph', strict=True)
        P = self.nx_port(self.G, P)
        # build subgraphs
        for type in subgraphs:
            sub = pydot.Subgraph('cluster_' + type.replace(" ", "_"),
                                 strict=True,
                                 graph_type='digraph',
                                 label=type + ' cluster',
                                 style='filled',
                                 color='#' + type_colors[type],
                                 fontcolor='#' + self.invertHexFull(type_colors[type])
                                 )
            sub = self.nx_port(subgraphs[type], sub, targetSubgraph=True)
            P.add_subgraph(sub)

        print('Rendering galaxies...')
        P.write(self.l3_path + 'galaxies_{}.dot'.format('iam_policy'))
        P.write_png(self.l3_path + 'galaxies_{}.png'.format('iam_policy'))

    def nx_port(self, G, targetP, targetSubgraph=False):
        """nx to pydot conversion  needs to happen manually to avoid node name issues

        :param G: originating nx graph
        :param targetP: target pydot graph
        :return:
        """
        n = G.nodes # this is how everything elds up here....
        for node in n:
            nn = pydot.Node(node.replace(":", "."),
                            style='filled',
                            fillcolor='#FFFFFF',
                            label=self.G_labels[node][1:-1])
            targetP.add_node(nn)

        # copy edges
        if targetSubgraph:
            pass
        else:
            # port edges directly
            ed = G.edges
            for e in ed:
                e = pydot.Edge(pydot.Node(e[0].replace(":", ".")), pydot.Node(e[1].replace(":", ".")),
                               # label=edge_labels[(e[0],e[1])]
                               )
                targetP.add_edge(e)
        return targetP

    def make_data(self):
        """Rebuild graph with emphasis on object type

        :return:
        """
        # get all existing object types
        types = self.type_collector(self.G_labels)
        print('found types: ' + str(types))
        # generate pretty colors
        type_colors = {}
        for type in types:
            type_colors[type] = "%06x" % random.randint(0, 0xFFFFFF)

        # G2 = nx.Graph()
        subnodes = {}
        subgraphs = {}

        for type in types:
            subnodes[type] = []
            query = {"contains": ["label", '"{}\n'.format(type)]}
            print('nxquery: ' + str(query))

            # find corresponsing nodes
            for node_id in search_nodes(self.G, query):
                # G2.add_node(node_id)
                subnodes[type].append(node_id)

            subgraphs[type] = self.G.subgraph(subnodes[type])
            print('________')

        print("ok!")
        self.nx_to_pywiz(type_colors, subgraphs)
