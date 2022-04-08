import csv
import networkx as nx
import networkx.algorithms.community as nx_comm

FILE_GEXF = 'covid_2022.gexf'

for gexf_file in [
    'covid_2020.gexf',
    'covid_2021.gexf',
    'covid_2022.gexf'
]:

    G = nx.read_gexf('../gexf/' + gexf_file)

    nodes = G.nodes.data()

    # get nodes *degree_centrality*
    degree_centrality_nodes = nx.degree_centrality(G)
    # sort result, decreasing
    degree_centrality_nodes = {k: v for k, v in sorted(degree_centrality_nodes.items(), key=lambda item: item[1], reverse=True)}
    # top 10
    degree_centrality_nodes_top = [nodes[node_id] for node_id in degree_centrality_nodes.keys()][0:10]

    with open('../dist/centrality-' + gexf_file + '.csv', 'w', newline='') as csvfile:
        fieldnames = ['nb', 'name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for i, node in enumerate(degree_centrality_nodes_top):
            writer.writerow({
                'nb': i + 1,
                'name': node['name']
            })
    """
    clustering_nodes = nx_comm.louvain_communities(G, weight=None, resolution=0.001, seed=123)

    # print(clustering_nodes)
    for cluster in clustering_nodes:
        print(list(cluster))

    with open('../dist/cluster-' + gexf_file + '.csv', 'w', newline='') as csvfile:
        fieldnames = ['cluster_id', 'name', 'category', 'pages_total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for i, cluster in enumerate(clustering_nodes):
            for node_id in list(cluster):
                writer.writerow({
                    'cluster_id': i + 1,
                    'name': nodes[node_id]['name'],
                    'category': nodes[node_id]['Type_Acteur'] if 'Type_Acteur' in nodes[node_id] else 'inconnu',
                    'pages_total': nodes[node_id]['pages_total']
                })
    """