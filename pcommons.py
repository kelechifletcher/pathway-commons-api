#!/usr/bin/python

from __future__ import division
import sys
import requests
from optparse import OptionParser


class Graph:
    name = ''
    description = ''
    gene_list = []
    edge_list = []

    def __init__(self, name='', description='', g_list=None, e_list=None):
        self.name = name
        self.description = description

        if g_list:
            self.gene_list = g_list
        else:
            self.gene_list = []

        if e_list:
            self.edge_list = e_list
        else:
            self.edge_list = []

    def to_string(self):
        string = ''

        #essentials
        score_type = '! Binary'
        species = '@ Homo Sapiens'
        gene_id_type = '% Gene Symbol'
        abbr = ': '
        name = '= '
        desc = '+ '

        string += '%s\n%s\n%s\n%s\n%s\n%s\n\n' % (score_type, species,
                                                gene_id_type, abbr + self.name,
                                                name + self.name, desc + self.description)

        for gene in self.gene_list:
            string += '%s\n' % gene

        string += '\n'

        for edge in self.edge_list:
            string += '%s\t%s\n' % (edge[0], edge[2])

        return string


def get_graph(source):
    # PC2 REST API
    pc2 = 'http://www.pathwaycommons.org/pc2/graph'
    payload = {'kind': 'neighborhood', 'source': source, 'format': 'extended_binary_sif'}

    response = requests.get(url=pc2, params=payload)

    gene_list = []
    edge_list = []

    if response.status_code == requests.codes.ok:
        data = response.text

        (edg_list, vtx_list) = data.split('\n\n')

        # Parse and filter vertices
        vtx_list = vtx_list.split('\n')

        for vtx in vtx_list[1:]:
            gene = tuple(vtx.split('\t'))

            if 'ProteinReference' in gene[1] or 'RnaReference' in gene[1]:
                gene_list.append(gene[0])

        # Parse and filter edges
        edg_list = edg_list.split('\n')

        for edg in edg_list[1:]:
            edge = tuple(edg.split('\t'))

            if edge[0] in gene_list and edge[2] in gene_list:
                edge_list.append(edge[:3])

    return Graph(name='%s Gene Interaction Network' % source,
                 description='%s Gene Interaction Network Retrieved From Pathway Commons',
                 g_list=gene_list,
                 e_list=edge_list)


def main(argv):
    usage = 'usage: %s [options] <gene id> or <unigene id>' % argv[0]
    parser = OptionParser(usage=usage)

    parser.add_option('-i', '--info', dest='info', default=False, action='store_true',
                      help='report # of vertices and edges, graph density')

    parser.add_option('-f', '--file', dest='file', action='store',
                      help='write graph(s) to file')

    (opts, args) = parser.parse_args()

    if len(args) > 0:
        for source in args:
            graph = get_graph(source)

            if opts.info:
                if graph.gene_list:
                    v = len(graph.gene_list)
                    e = len(graph.edge_list)
                    density = (2 * e) / (v * (v - 1))

                    print('V: %i\nE: %i\ndensity: %f' % (v, e, density))

                else:
                    print('\'%s\' was not found.' % source)

            if opts.file:
                out_file = open(opts.file, 'w+')
                out_file.write(graph.to_string())
                out_file.close()

                print(out_file.name)


if __name__ == '__main__':
    main(sys.argv)
