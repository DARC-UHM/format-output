taxon_tree = {
  "AphiaID": 1,
  "rank": "Superdomain",
  "scientificname": "Biota",
  "child": {
    "AphiaID": 2,
    "rank": "Kingdom",
    "scientificname": "Animalia",
    "child": {
      "AphiaID": 1267,
      "rank": "Phylum",
      "scientificname": "Cnidaria",
      "child": {
        "AphiaID": 1292,
        "rank": "Class",
        "scientificname": "Anthozoa",
        "child": {
          "AphiaID": 1340,
          "rank": "Subclass",
          "scientificname": "Hexacorallia",
          "child": {
            "AphiaID": 1360,
            "rank": "Order",
            "scientificname": "Actiniaria",
            "child": {
              "AphiaID": 888371,
              "rank": "Suborder",
              "scientificname": "Enthemonae",
              "child": {
                "AphiaID": 853973,
                "rank": "Superfamily",
                "scientificname": "Actinioidea",
                "child": {
                  "AphiaID": 100653,
                  "rank": "Family",
                  "scientificname": "Actiniidae",
                  "child": {
                    "AphiaID": 100698,
                    "rank": "Genus",
                    "scientificname": "Bolocera",
                    "child": None
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

flattened_tree = {
  'Superdomain': 'Biota',
  'Kingdom': 'Animalia',
  'Phylum': 'Cnidaria',
  'Class': 'Anthozoa',
  'Subclass': 'Hexacorallia',
  'Order': 'Actiniaria',
  'Suborder': 'Enthemonae',
  'Superfamily': 'Actinioidea',
  'Family': 'Actiniidae',
  'Genus': 'Bolocera'
}

aphia_record = {
  "AphiaID": 140621,
  "url": "https://www.marinespecies.org/aphia.php?p=taxdetails&id=140621",
  "scientificname": "Illex coindetii",
  "authority": "(Vérany, 1839)",
  "status": "accepted",
  "unacceptreason": None,
  "taxonRankID": 220,
  "rank": "Species",
  "valid_AphiaID": 140621,
  "valid_name": "Illex coindetii",
  "valid_authority": "(Vérany, 1839)",
  "parentNameUsageID": 138278,
  "kingdom": "Animalia",
  "phylum": "Mollusca",
  "class": "Cephalopoda",
  "order": "Oegopsida",
  "family": "Ommastrephidae",
  "genus": "Illex",
  "citation": "MolluscaBase eds. (2023). MolluscaBase. Illex coindetii (Vérany, 1839). Accessed through: World Register of Marine Species at: https://www.marinespecies.org/aphia.php?p=taxdetails&id=140621 on 2023-03-31",
  "lsid": "urn:lsid:marinespecies.org:taxname:140621",
  "isMarine": 1,
  "isBrackish": None,
  "isFreshwater": 0,
  "isTerrestrial": 0,
  "isExtinct": None,
  "match_type": "like",
  "modified": "2016-06-11T23:30:29.807Z"
}