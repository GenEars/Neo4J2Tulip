from tulip import *
import tulipplugins
from neo4j.v1 import GraphDatabase, basic_auth

# Plugin principle
#   Le plugin utilise l'interface bolt d'une instance Neo4J active
#   Le module python pour Neo4J doit etre installe
#      => https://neo4j.com/developer/python/
#      => pip install neo4j-driver
#   Pseudo-code :
#      - collecte Neo4J et creation des noeuds dans Tulip,
#      - pour chaque noeud Tulip,
#          - collecte des adjacences Neo4J
#          - recherche de l'objet Tulip correspondant
#          - creation de l'adjacence Tulip
#   Notes d'utilisation :
#      - La variable Node_s_type permet de filtrer les noeuds a recuperer selon la syntaxe Neo4J
#          - <rien> => tous les noeuds sont importes
#          - :<TYPE> => seuls les noeuds de type :<TYPE> sont importes
#      - La variable Node_s_propertyName_label permet de selectionner la propriete des neouds a importer 
#        en tant que label; l'id Neo4j du noeud est importe dans tous les cas.

class TulipNEO4J(tlp.ImportModule):
  def __init__(self, context):
    tlp.ImportModule.__init__(self, context)
    
    # TODO : indiquer les prerequis au niveau des imports
    self.addStringParameter("URL_to_server", "URL to access bolt service of an active NEO4J instance", "bolt://localhost:7687", True, True, False)
    self.addStringParameter("DB_username", "DB Authentication : username", "neo_bolt", True, True, False)
    self.addStringParameter("DB_password", "DB Authentication : password", "neo_bolt", True, True, False)
    self.addStringParameter("Node_s_type", "Type of Source node for import filtering (format = ':TYPE')", "", False, True, False)    
    self.addStringParameter("Node_s_propertyName_label", "Property of Source nodes to be used for labelling", "label", True, True, False)
    self.addBooleanParameter("DEBUG_Print", "Choose if logging should be printed out in Python console", "false", False)
      
  def importGraph(self):

    # Proprietes des noeuds
    n_id = self.graph.getIntegerProperty("n_id")
    n_label = self.graph.getStringProperty("n_label")

    def findNodeFromIdProperty(id_value):
      # TODO : optimiser la recherche en utilisant des appels internes
      for n in self.graph.getNodes():
        n_id_retrieved = n_id.getNodeValue(n)
        if n_id_retrieved == id_value :
          return n

    # TODO : gerer les exceptions
    
    # Instanciation NEO4J
    self.pluginProgress.setComment("Connecting to DB ...")
    driver = GraphDatabase.driver(self.dataSet["URL_to_server"], auth = basic_auth("neo_bolt", "neo_bolt"))
    session = driver.session()    
        
    # Requete des noeuds en BDD
    if self.dataSet["DEBUG_Print"] : print("*** RUN MATCH COUNT ***")
    self.pluginProgress.setComment("Getting DB node count ...")
    match_string = "MATCH (a) RETURN COUNT(a) AS n_count"      
    result = session.run(match_string)
    for record_count in result :
      n_count = int(record_count["n_count"])
    if self.dataSet["DEBUG_Print"] : print("DB node count = %s" % n_count)
    
    # Requete des noeuds en BDD
    if self.dataSet["DEBUG_Print"] : print("*** RUN MATCH NODES ***")
    self.pluginProgress.setComment("Getting nodes ...")

    n_type_filter = self.dataSet["Node_s_type"] # TODO : Verifier la validite du filtre (regex; strip; etc.)

    if len(self.dataSet["Node_s_propertyName_label"]) > 0 :
      match_string = "MATCH (a" + n_type_filter + ") RETURN ID(a) AS id, a." + self.dataSet["Node_s_propertyName_label"] + " AS label"
    else :
      match_string = "MATCH (a" + n_type_filter + ") RETURN ID(a) AS id, ID(a) AS label"      
    result = session.run(match_string)

    i_for = 0
    for record in result :
      i_for += 1
      self.pluginProgress.progress(i_for, n_count)

      if self.pluginProgress.state() == tlp.TLP_STOP :
        break

      if self.dataSet["DEBUG_Print"] : print("Node : id = %s, label = %s" % (record["id"], record["label"]))
      
      n_s = self.graph.addNode()
      
      n_id[n_s] = record["id"]
      
      if record["label"] :
        n_label[n_s] = record["label"]
      else :
        n_label[n_s] = ""

    # Requete des relations a partir des noeuds Tulip
    self.pluginProgress.setComment("Getting relationships ...")
    if self.dataSet["DEBUG_Print"] : print("*** RUN MATCH RELATIONSHIPS ***")
    i_for = 0
    for n_current in self.graph.getNodes() :
      i_for += 1
      self.pluginProgress.progress(i_for, n_count)

      if self.pluginProgress.state() == tlp.TLP_STOP :
        break

      n_current_prop_dict = self.graph.getNodePropertiesValues(n_current)
      n_current_id = n_id.getNodeValue(n_current)

      match_string = "MATCH (s)-[l]-(d) WHERE ID(s) = " + str(n_current_id) + " RETURN ID(d) AS id_d"

      if self.dataSet["DEBUG_Print"] :
        print("--------------------------------")
        print(n_current_prop_dict)
        print("n_current_id = %s" % n_current_id)
        print(match_string)


      result_match2 = session.run(match_string)
      
      for record2 in result_match2 :
		# TODO : identifier les causes de ralentissement du parcours de result_match2
        n_d_id = record2["id_d"]
        if self.dataSet["DEBUG_Print"] :
          print("(n_current_id = %s) --> (n_d_id = %s)" % (n_current_id, n_d_id))
        self.graph.addEdge(n_current, findNodeFromIdProperty(n_d_id))

    # Cloture
    self.pluginProgress.setComment("Ending ...")
    session.close()
    
    # TODO : gerer l'etat tlp.TLP_CANCEL    
    
    return True

# The line below does the magic to register the plugin into the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPlugin("TulipNEO4J", "TulipFromNEO4J", "Lionel TAILHARDAT", "03/06/2017", "Import nodes and relationships from NEO4J DB", "1.0")
