"""
L1 to L2 data products

This module turns L1 data products (interconnect meta-info)
into L2 data products (interconnections list)
"""

from security_scripts.information.lib import measurements
import os
import networkx as nx
from networkx.readwrite import json_graph
import pyjq
from random import randrange
import json


class Acquire(measurements.Dataset):
    """
    Clean aquired data, elevating it from L0A to L0B

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)

        # init graph
        self.G = nx.Graph()


        # dir enforcement
        self.l0b_path = args.report_path + '/L0B/'
        self.l1_path = args.report_path + '/L1/'
        self.l2_path = args.report_path + '/L2/'
        if not os.path.exists(self.l2_path):
            os.makedirs(self.l2_path)

        self.make_data()
        self.clean_data()

    def get_self_formula(self, service, function, definitions_self):
        """Return jq formula for finding self main id

        :return:
        """
        out = []
        for definition in definitions_self:
            if definition['my_service'] == service and definition['my_function'] == function:
                out.append(definition['path'])
        if out == []:
            return None
        else:
            return out


    def linked_everything(self, definitions_others, source, definitions_self, node):
        """Return self Ids of everything that is attaching the specified node

        :return: list
        """
        # find other places where this service is mentioned (aka links)
        links = []
        for endpoint in definitions_others:
            if endpoint['peer_service'] == source['peer_service']:
                links.append(endpoint)


        # loop through linked locations
        for link in links:
            # load linked file into memory
            linked_file = self.l0b_path + '{}_{}.json'.format(link['my_service'], link['my_function'])
            print('Reading ' + linked_file)
            linked_file = self.json_from_file(linked_file)

            # find entries in linked file where path value is equal to node value
            # break down lists to get individual entries to parse
            dict_path = "".join([e + '[] | ' for e in link['path'].split('[]')[:-1]])
            self_formula = '{}select({}=="{}")'.format(dict_path,
                                                       "." + link['path'].split('.')[-1:][0],
                                                       node)
            print(
                'Getting mentions of {} in {}_{}.json with jq: {}'.format(node, link['my_service'], link['my_function'],
                                                                          self_formula))
            self_mentions = pyjq.all(self_formula, linked_file)
            print('Found {} mentioning objects'.format(len(self_mentions)))

            # parse objects mentioning the node to get self-identifiers of said objects
            linked_self_formulas = self.get_self_formula(link['my_service'], link['my_function'], definitions_self)
            if linked_self_formulas is None:
                print('Could not find self formula for {}_{}'.format(link['my_service'], link['my_function']))
                # dump exceptions
                with open(self.l2_path + 'exceptions.txt', 'a') as exc:
                    exc.write('{},{},{}\n'.format(link['my_service'], link['my_function'], source['peer_service']))
            else:
                if self_mentions != []:
                    # idea: break down self-identifier with | ?
                    for linked_self_formula in linked_self_formulas:
                        if link['path'] == '.[].Reservations[].Instances[].NetworkInterfaces[].VpcId':
                            print('gotcha')
                        # toss out the part of the formula we unpacked
                        linked_self_formula_short = ".[]" + linked_self_formula.replace(".".join(link['path'].split('.')[:-1]), "")
                        if linked_self_formula_short.startswith('.[].[].'):
                            with open(self.l2_path + 'jq_exceptions.txt', 'a') as exc:
                                exc.write('{}_{},{},{},{}\n'.format(link['my_service'], link['my_function'], link['path'], linked_self_formula, linked_self_formula_short))
                            break
                        else:
                            print('Getting self IDs from {}_{}.json attached to {} with jq: {}\nSelf formula is {}\nlink formula is {}'.format(link['my_service'],
                                                                                                       link['my_function'],
                                                                                                       node,
                                                                                                       linked_self_formula_short,
                                                                                                       linked_self_formula,
                                                                                                       link['path']))
                            linked_matches = pyjq.all(linked_self_formula_short, self_mentions)
                            print('Found {} attachments'.format(len(linked_matches)))
                            yield linked_matches
            print('_____________')

    def get_self_tags(self, node, node_file, source):
        pass

    def make_data(self):
        """loop through many, many things to find connections

        :return:
        """
        # ingest to_self to build nodes
        definitions_self = self.json_from_file(self.l1_path + '/to_self.json')
        # ingest to_others to build edges
        definitions_others = self.json_from_file(self.l1_path + '/to_others.json')

        for source in definitions_self:
            # open json from vault and parse with pre-calculated jq
            node_file = self.json_from_file(self.l0b_path + '/{}_{}.json'.format(source['my_service'], source['my_function']))
            nodes = pyjq.all(source['path'], node_file)

            # build nodes from self-identifiers
            for node in nodes:
                print('Added node ' + node)
                self.G.add_node(node, label=source['peer_service'] + '\n' + node, data="i'm data",
                           tags=str(randrange(11)))
                # todo: add tag scraper
                # get self-id from objects mentioning the node
                for page in self.linked_everything(definitions_others, source, definitions_self, node):
                    for attachment in page:
                        print('Adding edge {} to {}'.format(node, attachment))
                        self.G.add_edge(node, attachment.replace(':', '_'))

        # dump to json
        with open(self.l2_path + 'networkdata1.json', 'w') as outfile1:
            outfile1.write(json.dumps(json_graph.node_link_data(self.G)))
