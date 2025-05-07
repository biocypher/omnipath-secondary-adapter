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
    parser = argparse.ArgumentParser(description=usage)

    parser.add_argument(
        "-net",
        "--networks",
        metavar="TSV",
        nargs="+",
        help="Extract from the Omnipath networks TSV file.",
    )

    parser.add_argument(
        "-enz",
        "--enzyme-PTM",
        metavar="TSV",
        nargs="+",
        help="Extract from the Omnipath enzyme-PTM TSV file.",
    )

    parser.add_argument(
        "-co",
        "--complexes",
        metavar="TSV",
        nargs="+",
        help="Extract from the Omnipath complexes TSV file.",
    )

    parser.add_argument(
        "-an",
        "--annotations",
        metavar="TSV",
        nargs="+",
        help="Extract from the Omnipath annotations TSV file.",
    )

    parser.add_argument(
        "-int",
        "--intercell",
        metavar="TSV",
        nargs="+",
        help="Extract from the Omnipath intercell TSV file.",
    )

    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    parser.add_argument(
        "-v",
        "--verbose",
        choices=levels.keys(),
        default="WARNING",
        help="Set the verbose level (default: %(default)s).",
    )

    asked = parser.parse_args()

    # Actually extract data.
    nodes = []
    edges = []

    # Extract from databases not requiring preprocessing.
    if asked.networks:
        logging.info(f"Weave Omnipath networks data...")

        networks_df = pd.read_csv(asked.networks[0], sep="\t")
        print(networks_df.info())

        mapping_file = "./omnipath_secondary_adapter/adapters/networks.yaml"
        with open(mapping_file) as fd:
            mapping = yaml.full_load(fd)

        adapter = ontoweaver.tabular.extract_table(
            # df=networks_df, config=mapping, separator=":", affix="suffix"
            df=networks_df,
            config=mapping,
            separator=":",
            affix="none",
        )

        nodes += adapter.nodes
        edges += adapter.edges

        logging.info(f"Wove Networks: {len(nodes)} nodes, {len(edges)} edges.")

    # Fusion step: fuse duplicated nodes and edges.
    import_file = ontoweaver.reconciliate_write(
        nodes,
        edges,
        "config/biocypher_config.yaml",
        "config/schema_config.yaml",
        separator=", ",
    )


# Example of usage in CLI:
# poetry run python weave_knowledge_graph.py -net ./data_testing/subset_interactions.tsv
