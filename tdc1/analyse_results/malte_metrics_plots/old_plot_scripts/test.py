import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import numpy.random 

N = 15
scatter_data = numpy.random.rand(3, N)
G=nx.Graph()

data_nodes = []
init_pos = {}
for j, b in enumerate(scatter_data.T):
    x, y, _ = b
    data_str = 'ddsaata_{0}'.format(j)
    ano_str = 'ano_{0}'.format(j)
    G.add_node(data_str)
    G.add_node(ano_str)
    G.add_edge(data_str, ano_str)
    data_nodes.append(data_str)
    init_pos[data_str] = (x, y)
    init_pos[ano_str] = (x, y)

pos = nx.spring_layout(G, pos=init_pos, fixed=data_nodes)

plt.scatter(scatter_data[0], scatter_data[1], c=scatter_data[2], s=scatter_data[2]*150)
ax = plt.gca()

for j in range(N):
    data_str = 'data_{0}'.format(j)
    ano_str = 'ano_{0}'.format(j)
    ax.annotate(ano_str,
                xy=pos[data_str], xycoords='data',
                xytext=pos[ano_str], textcoords='data',
                arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3"))

all_pos = np.vstack(pos.values())
mins = np.min(all_pos, 0)
maxs = np.max(all_pos, 0)

ax.set_xlim([mins[0], maxs[0]])
ax.set_ylim([mins[1], maxs[1]])

plt.show()