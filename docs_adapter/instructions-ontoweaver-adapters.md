## Steps to create an adapter with Ontoweaver
1. Create a folder to store the data in our project. This folder can called `data`.
2. Add the folder `data` to the `.gitignore` file to avoid uploading large datasets in our repository.
3. [**TO DO**] If there is a step of preprocessing, create `weave_knowledge_graph.py` following the ontoweaver python template. If not, use the CLI command in the new version.

4. Create an Ontoweaver mapping file (`.yaml`) in the folder `/omnipath_secondary_adapter/adapters`. You should create one Ontoweaver mapping file for each table you are interested in use for building your knowledge graph. The purpose of each file is to map columns from each table with graph entities (nodes and relationships). At the same time, you can apply [Ontoweaver Transformers](https://ontoweaver.readthedocs.io/en/latest/readme_sections/mapping_api.html#available-transformers) to the data before use the data.

5. Create a BioCypher schema file  (`schema_config.yaml`) in the folder `/config/`. This file will serve to define which nodes and relationships will be present in our graph. For more information [click here](https://biocypher.org/quickstart.html#the-schema-configuration-yaml-file)

> [!IMPORTANT]
> Remember: You should create one single `schema_config_file.yaml`. On the other hand, you should create one ontoweaver YAML file per table you are using.

6. Add an ontology to be based on in `config/biocypher_config.yaml` and refer the entities and associations of the ontology in the `config/schema_config.yaml`.

## Not to forget

- For each column that you want extract, you need ot have (at least) one transformer.
- 'label' == 'node|edge type'
- underscore are necessary in labels in OntoWeaver adapters

## TO DO

1. Estimate time for:
     - processing biocypher output:
          - [X] Edwin  
          - [X] Matthieu 
     - [ ] importing data in neo4j.(Matthieu)
2. Check if the graph is consistent with the tabular data. (Edwin and Matthieu)
    - Possible tests:
     - [X] Verify there is not error when a source and a target are the same.
      - [X] Count the number of edges in total.
      - [X] Count the number of nodes in total.
      - [X] Test if the schema is correct.
3. [ ] Show the ontoweave command.(next Wed 19/03)
4. Implement data validation in ontoweaver adapter.(next Wed 26/03)
5. [X] Have the description with chatGPT. (Edwin)
6. Add the other properties to the edges. (Matthieu)
6. Import the other tables. (longer term)
     - Add meta data.
7. [X] Add the ability to download the data from Omnipath archive directly and automatically. (Edwin)
 

# Frequently Asked Questions

1. **What does it mean "secondary adapter"?** -- it means the data in the adapter has been the result of harmonized procedures and does not constitute the primary source of information. For instance: the omnipath interactions table has been built by using more than one original resource (other tables).
