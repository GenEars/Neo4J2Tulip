# TulipFromNEO4J

Share of an old plug-in project started in 2017 that was aiming to link [Neo4J](https://neo4j.com/) to the [Tulip Data Visualization Software](https://tulip.labri.fr/TulipDrupal/) tool.
The plug-in code has been sent to the Labri team by e-mail on the 03/06/2017; things may have evolved since then, you may however expand this work if you ever need it.

## Plugin principles
```
   Le plugin utilise l'interface bolt d'une instance Neo4J active
   Le module python pour Neo4J doit etre installe
      => https://neo4j.com/developer/python/
      => pip install neo4j-driver
   Pseudo-code :
      - collecte Neo4J et creation des noeuds dans Tulip,
      - pour chaque noeud Tulip,
          - collecte des adjacences Neo4J
          - recherche de l'objet Tulip correspondant
          - creation de l'adjacence Tulip
   Notes d'utilisation :
      - La variable Node_s_type permet de filtrer les noeuds a recuperer selon la syntaxe Neo4J
          - <rien> => tous les noeuds sont importes
          - :<TYPE> => seuls les noeuds de type :<TYPE> sont importes
      - La variable Node_s_propertyName_label permet de selectionner la propriete des neouds a importer 
        en tant que label; l'id Neo4j du noeud est importe dans tous les cas.
```

## Expectations
* le Plug-in est fonctionnel.
* les améliorations à apporter sont indiquées en `#TODO`.
* une étude de parallélisation du code Python est à envisager pour les jeux de données importants (>500 adjacences).
