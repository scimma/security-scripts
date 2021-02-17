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
        self.G_tags = nx.get_node_attributes(self.G, 'tags')
        self.G_labels = nx.get_node_attributes(self.G, 'label')  # reference this to get label

        self.make_data()
        self.clean_data()

    def get_self_formula(self, service, function, definitions_self):
        pass

    def service_collector(self, tags):
        srv = []
        # loop through passed tags, turning them into json and parsing for key:service//value:??
        for tag in tags:
            # skip empty tags
            if tags[tag] != 'None' and tags[tag] != '"[]"':
                # fix quotes, escapes, newlines, tails etc
                parsed = json.loads(tags[tag].replace("'", '"').replace("\\", "").replace("\n", "")
                                    .replace("True",'"True"').replace("False", '"False"')[1:-1])
                ss = pyjq.all('.[] | select(.Key=="{}") | .Value'.format(self.args.tag), parsed)
                # multiple services are possible for a single object
                for s in ss:
                    srv.append(s)
        return list(set(srv))

    def get_node_service(self, tags, node):
        try:
            parsed = json.loads(tags[node].replace("'", '"').replace("\\", "").replace("\n", "")[1:-1])
            ss = pyjq.all('.[] | select(.Key=="{}") | .Value'.format(self.args.tag), parsed)
            label = ", ".join(s for s in ss)
            print("{}'s tag is {}".format(node, label))
        except json.decoder.JSONDecodeError:
            return ''
        if label == '':
            return ''
        else:
            return '\n' + label

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

    def nx_port(self, G, targetP, labels, tags, edge_labels=None, targetSubgraph=False):
        """nx to pydot conversion  needs to happen manually to avoid node name issues

        :param G: originating nx graph
        :param targetP: target pydot graph
        :return:
        """
        n = G.nodes
        for node in n:
            nn = pydot.Node(node.replace(":", "."),
                            style='filled',
                            fillcolor='#FFFFFF',
                            label=labels[node][1:-1] + self.get_node_service(tags, node))
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

    def nx_to_pywiz(self, G, subgraphs, service_colors, labels, tags):
        # build pydot from scratch
        P = pydot.Dot(graph_type='graph', strict=True)
        P = self.nx_port(G, P, labels, tags, edge_labels=nx.get_edge_attributes(G, 'label'))
        # build subgraphs
        for service in subgraphs:
            sub = pydot.Subgraph('cluster_' + service.replace(" ", "_"),
                                 strict=True,
                                 graph_type='digraph',
                                 label=service + ' cluster',
                                 style='filled',
                                 color='#' + service_colors[service],
                                 fontcolor='#' + self.invertHexFull(service_colors[service])
                                 )
            sub = self.nx_port(subgraphs[service], sub, labels, tags, targetSubgraph=True)
            P.add_subgraph(sub)

        print('Rendering galaxies...')
        P.write(self.l3_path + 'galaxies_{}.dot'.format(self.args.tag))
        P.write_png(self.l3_path + 'galaxies_{}.png'.format(self.args.tag))

    def just_one(self, G, node):
        """check if the node only has one connection in G

        :return:
        """
        edges = G.edges
        f = 0
        for edge in edges:
            if (edge[0] == node and edge[0] != edge[1]) or (edge[1] == node and edge[0] != edge[1]):
                f += 1
        if f == 1:
            print('{} is unique'.format(node))
            return True
        else:
            return False

    def get_edge_property(self, G, property, node1, node2):
        G_edge_properties = nx.get_edge_attributes(G, property)
        return G_edge_properties[(node1, node2, 0)][1:-1]
        # G_edge_properties[(node2, node1, 0)] is never needed because the derivative table has the same order

    def append_based_on_service(self, G, node, partner):
        # find all existing connections for this node
        query = {"contains": ["label", node]}


        # what happens on the next executable line is
        # 1. find where node is source
        # 2. find where node is target and flip tuples there
        # 3. Merge the two
        all_matches = list(search_direct_relationships(graph=G, source=query)) + [t[::-1] for t in list(
            search_direct_relationships(graph=G, target=query))]


        # only partners with service tags be used for galaxy deduction
        matches = []
        for match in all_matches:
            if self.get_node_service(self.G_tags, match[1]) != '':
                matches.append(match)
        # get node type
        node_type = node.split('-')[0]



        # load priority dict from file
        rules = {}
        # help our little script find the attachment priority file
        import security_scripts.information
        for row in csv.reader(open(security_scripts.information.__path__[0] + '/attachment_priority.csv')):
            key = row[0]
            # ignore comments
            if key[0] != "#":
                rules[key] = row[1:]


        # loop through rules, trying to find the partner
        top_match = ''
        for rule in rules[node_type]:
            for match in matches:
                # the rule list is in attachment order
                # the following if will always go off at the top attachment priority
                if match[1].split('-')[0] == rule:
                    # we found something that matches the rule!
                    top_match = match
                    # is it our partner, though?
                    if top_match[1] == partner:
                        return True
                    else:
                        return False

        # no matches found :(
        return False


    def make_data(self):
        """Rebuild graph with emphasis on services and the "galaxies" they form

        :return:
        """
        # get all existing services
        services = self.service_collector(nx.get_node_attributes(self.G, 'tags'))
        print('found services: ' + str(services))
        # generate pretty colors
        service_colors = {}
        for service in services:
            service_colors[service] = "%06x" % random.randint(0, 0xFFFFFF)

        # prepare first graph for node-node connection checking
        G2 = nx.Graph()

        # find service galaxy connections
        print('building G2 reference graph...')
        for service in services:
            query = {"contains": ["tags", service]}

            matching_sources = list(search_direct_relationships(graph=self.G, source=query))
            matching_targets = list(search_direct_relationships(graph=self.G, target=query))

            for r in matching_sources:
                # add found nodes
                G2.add_node(r[0])
                G2.add_node(r[1])
                # connect them
                G2.add_edge(r[0], r[1])

            for r in matching_targets:
                # add found nodes
                G2.add_node(r[0])
                G2.add_node(r[1])
                # connect them
                G2.add_edge(r[0], r[1])

        # testing: dump intermediate graph
        # nx_to_pywiz(G2, [], service_colors, G_labels)

        # build G3, similar to G2, but with subgraphs and referencing G2 to check for single-connection situations
        # prepare galaxies graph
        G3 = nx.Graph()

        subgraphs = {}
        subnodes = {}

        # find service galaxy connections
        for service in services:
            query = {"contains": ["tags", service + "'"] } 
            print('nxquery: ' + str(query))

            matching_sources = list(search_direct_relationships(graph=self.G, source=query))
            matching_targets = list(search_direct_relationships(graph=self.G, target=query))

            subnodes[service] = []

            for r in matching_sources:
                # verify that our finding is not just a substring match in tags
                if service in self.get_node_service(self.G_tags, r[0]):
                    # add found nodes
                    G3.add_node(r[0])
                    subnodes[service].append(r[0])
                    G3.add_node(r[1])
                    # sort out the target and hwere it belongs
                    if self.just_one(G2, r[1]) and self.get_node_service(self.G_tags,
                                                               r[1]) == '':  # situation: True, False core-network
                        subnodes[service].append(r[1])
                    elif not self.just_one(self.G, r[1]) and self.get_node_service(self.G_tags, r[1]) == '':
                        # okay, it might not be a singleton...
                        # but it's still missing a service!
                        if self.append_based_on_service(self.G, r[1], r[0]):
                            subnodes[service].append(r[1])
                    print('Added nodes {} and {}'.format(r[0], r[1]))
                    # connect them
                    G3.add_edge(r[0], r[1],
                                label='Origin: {}\nReason: {}'.format(self.get_edge_property(self.G, 'origin', r[0], r[1]),
                                                                      self.get_edge_property(self.G, 'reason', r[0], r[1])))
                    print('Added edge {} to {}'.format(r[0], r[1]))

            for r in matching_targets:
                # verify that our finding is not just a substring match in tags
                if service in self.get_node_service(self.G_tags, r[1]):
                    # add found nodes
                    G3.add_node(r[0])
                    # sort out the source
                    if self.just_one(G2, r[0]) and self.get_node_service(self.G_tags, r[0]) == '':
                        subnodes[service].append(r[0])
                    elif not self.just_one(self.G, r[0]) and self.get_node_service(self.G_tags, r[0]) == '':
                        # okay, it might not be a singleton...
                        # but it's still missing a service!
                        if self.append_based_on_service(self.G, r[0], r[1]):
                            subnodes[service].append(r[0])
                    G3.add_node(r[1])
                    subnodes[service].append(r[1])
                    print('Added nodes {} and {}'.format(r[0], r[1]))
                    # connect them
                    G3.add_edge(r[0], r[1],
                                label='Origin: {}\nReason: {}'.format(self.get_edge_property(self.G, 'origin', r[0], r[1]),
                                                                      self.get_edge_property(self.G, 'reason', r[0], r[1])))
                    print('Added edge {} to {}'.format(r[0], r[1]))

            # loner handling
            loners = list(search_nodes(self.G, query))
            for r in loners:
                G3.add_node(r)
                subnodes[service].append(r)

            subgraphs[service] = G3.subgraph(subnodes[service])
            print('________')

        self.nx_to_pywiz(G3, subgraphs, service_colors, self.G_labels, self.G_tags)