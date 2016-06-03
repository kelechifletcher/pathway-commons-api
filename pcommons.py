#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3

import sys
import requests


class Graph:
    gene_list = []
    edge_list = []

    def __init__(self, g_list=None, e_list=None):
        if g_list:
            self.gene_list = g_list
        else:
            self.gene_list = []

        if e_list:
            self.edge_list = e_list
        else:
            self.edge_list = []


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

    return gene_list, edge_list


def main(argv):
    if len(argv) > 0:
        for source in argv:
            (gene_list, edge_list) = get_graph(source)

            if gene_list and edge_list:
                v = len(gene_list)
                e = len(edge_list)
                density = (2 * e) / (v * (v - 1))

                print('V: %i\nE: %i\ndensity: %f' % (v, e, density))

            else:
                print('\'%s\' was not found.' % source)


if __name__ == '__main__':
    main(sys.argv[1:])
