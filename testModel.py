from database.DAO import DAO
from model.model import Model

mymodel = Model()
mymodel.buildGraph()

myLinee = DAO.getAllLinee()

print(f"The graph has {mymodel.getNumNodes()} nodes and {mymodel.getNumEdges()} edges.")
print(myLinee)

