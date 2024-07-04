import geopy.distance

from database.DAO import DAO
import networkx as nx

from model.fermata import Fermata
from model.linea import Linea


class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph()
        self._idMap = {}
        for f in self._fermate:
            self._idMap[f.id_fermata] = f
        self._linee = DAO.getAllLinee()
        self._lineaMap = {}
        for linea in self._linee:
            self._lineaMap[linea.id_linea] = linea

    def getBestPath(self, v0, v1):
        costoTot, path = nx.single_source_dijkstra(self._grafo, v0, v1, weight="weight")
        return costoTot, path

    def buildGraph(self):
        self._grafo.add_nodes_from(self._fermate)

        # for u in self._fermate:
        #     vicini = DAO.getEdgesVicini(u)
        #     for vicino in vicini:
        #         self._grafo.add_edge(u, self._idMap[vicino.id_stazA])
        #         print(f"Added edge between {u} and {self._idMap[vicino.id_stazA]}")

        self.addEdgePesati()

    def addEdgesMode3(self):
        # altro modo: unica query che legge tutte le connessioni
        allConnessioni = DAO.getAllConnessioni()
        for c in allConnessioni:
            u_nodo = self._idMap[c.id_stazP]
            v_nodo = self._idMap[c.id_stazA]
            self._grafo.add_edge(u_nodo, v_nodo)
        return self._grafo

    def getBFSNodes(self, source):  # Breath First Search
        edges = nx.bfs_edges(self._grafo, source)
        visited = []
        for u, v in edges:
            visited.append(v)
        return visited

    def getDFSNodes(self, source):
        edges = nx.dfs_edges(self._grafo, source)
        visited = []
        for u, v in edges:
            visited.append(v)
        return visited

    def addEdgePesati(self):
        self._grafo.clear_edges()
        allConnessioni = DAO.getAllConnessioni()
        for c in allConnessioni:
            v0 = self._idMap[c.id_stazP]
            v1 = self._idMap[c.id_stazA]
            linea = self._lineaMap[c.id_linea]
            peso = self.getTraversalTime(v0, v1, linea)

            # scelgo l'arco più veloce
            if self._grafo.has_edge(v0, v1):
                if self._grafo[v0][v1]["weight"] > peso:
                    self._grafo[v0][v1]["weight"] = peso
            else:
                self._grafo.add_edge(v0, v1, weight=peso)

            # if self._grafo.has_edge(self._idMap[c.id_stazP], self._idMap[c.id_stazA]):
            #     self._grafo[self._idMap[c.id_stazP]][self._idMap[c.id_stazA]]["weight"] += 1
            # else:
            #     self._grafo.add_edge(self._idMap[c.id_stazP], self._idMap[c.id_stazA], weight=1)

    @staticmethod
    def getTraversalTime(v0: Fermata, v1: Fermata, linea: Linea):
        p0 = (v0.coordX, v0.coordY)
        p1 = (v1.coordX, v1.coordY)
        distanza = geopy.distance.distance(p0, p1).km
        velocita = linea.velocita
        tempo = distanza / velocita * 60  # in minuti
        return tempo

    def getEdgeWeight(self, v1, v2):
        return self._grafo[v1][v2]["weight"]

    def buildGraphPesato(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        self.addEdgePesati()

    def getArchiPesoMaggiore(self):
        if len(self._grafo.edges) == 0:
            print("Il grafo è vuoto")
            return

        edges = self._grafo.edges
        result = []
        for u, v in edges:
            peso = self._grafo[u][v]["weight"]
            if peso > 2:
                result.append((u, v, peso))
        return result

    @property
    def fermate(self):
        return self._fermate

    def getNumNodes(self):
        return len(self._grafo.nodes)

    def getNumEdges(self):
        return len(self._grafo.edges)
