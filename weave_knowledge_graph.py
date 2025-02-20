#!/usr/bin/env python3
import argparse
import logging
import pandas as pd
import yaml

from biocypher import BioCypher
import ontoweaver
# from omnipath_seconday_adapter.adapters.example_adapter import

if __name__ == "__main__":

    usage = f"Extract nodes and edges from CSV tables of Omnipath databse: networks, enzyme-PTM, complexes, annotations and intercell."
    parser = argparse.ArgumentParser(
        description=usage)

    parser.add_argument("-net", "--networks", metavar="TSV", nargs="+",
                        help="Extract from the Omnipath networks TSV file.")
    
    parser.add_argument("-enz", "--enzyme-PTM", metavar="TSV", nargs="+",
                    help="Extract from the Omnipath enzyme-PTM TSV file.")

    parser.add_argument("-co", "--complexes", metavar="TSV", nargs="+",
                    help="Extract from the Omnipath complexes TSV file.")

    parser.add_argument("-an", "--annotations", metavar="TSV", nargs="+",
                    help="Extract from the Omnipath annotations TSV file.")

    parser.add_argument("-int", "--intercell", metavar="TSV", nargs="+",
                    help="Extract from the Omnipath intercell TSV file.")

    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    parser.add_argument("-v", "--verbose", choices = levels.keys(), default = "WARNING",
                        help="Set the verbose level (default: %(default)s).")
    
    asked = parser.parse_args()

    # Instanciate biocypher with the config files
    bc = BioCypher(
        biocypher_config_path="config/biocypher_config.yaml",
        schema_config_path="config/schema_config.yaml"
    )

    # Actually extract data.
    nodes = []
    edges = []

    # Extract from databases not requiring preprocessing.
    if asked.networks:
        logging.info(f"Weave Omnipath networks data...")
        
        networks_df = pd.read_csv(asked.networks[0], sep='\t')
    
        # Sources
        source_mapping_file = "./omnipath_secondary_adapter/adapters/networks_source.yaml"
        with open(source_mapping_file) as fd:
            source_mapping = yaml.full_load(fd)

        adapter = ontoweaver.tabular.extract_table(df=networks_df, 
                                                 config=source_mapping,
                                                 separator = ":",
                                                 affix= "suffix")

        nodes += adapter.nodes
        edges += adapter.edges

        # # Targets
        # target_mapping_file = "./omnipath_secondary_adapter/adapters/networks_target.yaml"
        # with open(target_mapping_file) as fd:
        #     target_mapping = yaml.full_load(fd)

        # adapter = ontoweaver.tabular.extract_table(df=networks_df, 
        #                                          config=target_mapping,
        #                                          separator = ":",
        #                                          affix= "suffix")

        # nodes += adapter.nodes
        # edges += adapter.edges

        logging.info(f"Wove Networks: {len(nodes)} nodes, {len(edges)} edges.")

    # Fusion step: fuse duplicated nodes and edges.
    import_file = ontoweaver.reconciliate_write(nodes, 
                                                edges, 
                                                "config/biocypher_config.yaml", 
                                                "config/schema_config.yaml", 
                                                separator=", ")
