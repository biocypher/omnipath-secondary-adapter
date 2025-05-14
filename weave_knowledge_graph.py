#!/usr/bin/env python3
"""
Script Name: Omnipath Adapter (secondary type)
Description:
    This script retrieves information from Omnipath databases

Usage:
    Example 1:
    # Download and process the latest Omnipath file (dataset) from Omnipath Archive.
    poetry run python weave_knowledge_graph_backup.py \
    -net download

    Example 2:
    # Process the specified file, e.g., ./data_testing/networks/subset_interactions_edgecases.tsv
    poetry run python weave_knowledge_graph.py \
    -net ./data_testing/networks/subset_interactions_edgecases.tsv

Arguments:
    -net, --networks        Path to the 'networks' dataset, or download the latest from the archive.
    -enz, --enzyme-PTM      Path to the 'enz-PTM' dataset, or download the latest from archive.
    -co, --complexes        Path to the 'complexes' dataset, or download the latest from archive.
    -an, --annotations      Path to the 'annotations' dataset, or download the latest from archive.
    -inter, --intercell     Path to the 'intercell' dataset, or download the latest from archive.
    -v, --verbose

"""


import argparse
import logging
import os
import yaml
import sys
from typing import (
    Any,
    Dict,
)

import ontoweaver
import pandas as pd
from biocypher._get import (
    Downloader,
    FileDownload,
)

from omnipath_secondary_adapter.models import (
    NetworksPanderaModel,
    EnzymePTMPanderaModel,
    # IntercellPanderaModel,
    # AnnotationsPanderaModel,
)

# ----------------------    CONSTANTS    ----------------------
CACHE_DATA_PATH = "./data"

URLS_OMNIPATH = {
    "annotations": "https://archive.omnipathdb.org/omnipath_webservice_annotations__latest.tsv.gz",
    "complexes": "https://archive.omnipathdb.org/omnipath_webservice_complexes__latest.tsv.gz",
    "enzyme_PTM": "https://archive.omnipathdb.org/omnipath_webservice_enz_sub__latest.tsv.gz",
    "intercell": "https://archive.omnipathdb.org/omnipath_webservice_intercell__latest.tsv.gz",
    "networks": "https://archive.omnipathdb.org/omnipath_webservice_interactions__latest.tsv.gz",
}

PANDERA_SCHEMAS = {
    # "annotations": AnnotationsPanderaModel,
    "enzyme_PTM": EnzymePTMPanderaModel,
    # "intercell": IntercellPanderaModel,
    "networks": NetworksPanderaModel,
}

ONTOWEAVER_MAPPING_FILES = {
    "annotations": "./omnipath_secondary_adapter/adapters/annotations.yaml",
    "enzyme_PTM": "./omnipath_secondary_adapter/adapters/enzymePTM.yaml",
    "intercell": "./omnipath_secondary_adapter/adapters/intercell.yaml",
    "networks": "./omnipath_secondary_adapter/adapters/networks.yaml",
}

BIOCYPHER_CONFIG_PATHS = {
    "annotations": "config/biocypher_config_annotations.yaml",
    "enzyme_PTM": "config/biocypher_config_enzymePTM.yaml",
    "intercell": "config/biocypher_config_intercell.yaml",
    "networks": "config/biocypher_config.yaml",
}

BIOCYPHER_SCHEMA_PATHS = {
    "annotations": "config/schema_config_annotations.yaml",
    "enzyme_PTM": "config/schema_config_enzymePTM.yaml",
    "intercell": "config/schema_config_intercell.yaml",
    "networks": "config/schema_config.yaml",
}


logger = logging.getLogger("biocypher")


# ----------------------    HELPER FUNCTIONS    ----------------------
def parse_arguments():
    """
    Extract nodes and edges from CSV tables of the Omnipath database: networks, enzyme-PTM, complexes, annotations, and intercell.

    This function uses 'argparse' to define and parse arguments related to different
    Omnipath data sources, including networks, enzyme-PTM interactions, complexes,
    annotations, and intercellular interactions. Additionally, it allows setting the
    verbosity level for logging.

    Arguments:
        -net, --networks        Path to the 'networks' dataset, or download latest from archive.
        -enz, --enzyme-PTM      Path to the 'enz-PTM' dataset, or download latest from archive.
        -co, --complexes        Path to the 'complexes' dataset, or download latest from archive.
        -an, --annotations      Path to the 'annotations' dataset, or download latest from archive.
        -inter, --intercell     Path to the 'intercell' dataset, or download latest from archive.
        -v, --verbose

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.

    """

    usage = "Extract nodes and edges from CSV tables of Omnipath database: networks, enzyme-PTM, complexes, annotations and intercell."

    epilog = """Example Usage:
        poetry run python weave_knowledge_graph_backup.py -net download
        poetry run python weave_knowledge_graph.py -net ./data_testing/networks/subset_interactions_edgecases.tsv
    """

    parser = argparse.ArgumentParser(
        description=usage, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-net",
        "--networks",
        metavar="TSV",
        nargs="?",
        help="extract from the Omnipath 'networks' TSV file.",
    )

    parser.add_argument(
        "-enz",
        "--enzyme-PTM",
        metavar="TSV",
        nargs="?",
        help="extract from the Omnipath 'enzyme-PTM' TSV file.",
    )

    parser.add_argument(
        "-co",
        "--complexes",
        metavar="TSV",
        nargs="?",
        help="extract from the Omnipath 'complexes' TSV file.",
    )

    parser.add_argument(
        "-an",
        "--annotations",
        metavar="TSV",
        nargs="?",
        help="extract from the Omnipath 'annotations' TSV file.",
    )

    parser.add_argument(
        "-inter",
        "--intercell",
        metavar="TSV",
        nargs="?",
        help="extract from the Omnipath 'intercell' TSV file.",
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
        help="set the verbose level (default: %(default)s).",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)  # Exit with error code 1

    return parser.parse_args()


def download_resource(resource_name: str, url_resource: str) -> list:

    # Define the directory where the data will be store
    cache_directory = CACHE_DATA_PATH

    # Instantiate the Downloader class
    downloader = Downloader(cache_dir=cache_directory)

    # Create a resource to download
    file_resource = FileDownload(
        name="omnipath_" + resource_name,
        url_s=url_resource,
        lifetime=7,  # Cache for 7 days
    )

    # Download the resource and return the stored file paths
    paths = downloader.download(file_resource)

    return paths


def access_to_resource(resource_name: str, argument_resource: str) -> str:

    logger.info(f"Processing resource: {resource_name} with option: {argument_resource}")

    if argument_resource is None:
        logger.error("Invalid option: None. Use --help for guidance.")
        raise ValueError("Invalid option: None. Consult the menu using --help.")

    if argument_resource == "download":
        url = URLS_OMNIPATH.get(resource_name)
        if not url:
            logger.error(f"No download URL found for resource: {resource_name}")
            raise ValueError(f"Download URL not found for resource: {resource_name}")

        paths = download_resource(resource_name=resource_name, url_resource=url)
        if not paths:
            logger.error(f"Download failed for resource: {resource_name}")
            raise RuntimeError(f"Failed to download resource: {resource_name}")

        return paths[0]

    if os.path.isfile(argument_resource):
        return argument_resource

    logger.error(f"Invalid option provided: {argument_resource}")
    raise ValueError(f"Invalid option: {argument_resource}")


def load_dataframe(resource_path: str, resource_name: str) -> pd.DataFrame:
    """
    Load a TSV file into a pandas DataFrame using a specified Pandera schema.

    Args:
        resource_path (str): Path to the TSV file.
        resource_name (str): The name of the resource used to retrieve the schema.

    Returns:
        pd.DataFrame: A cleaned and schema-conformant DataFrame.
    """
    schema_model = PANDERA_SCHEMAS.get(resource_name)

    if schema_model is None:
        logger.warning(f"No schema model found for resource: {resource_name}")

    try:
        dataframe_resource = pd.read_table(
            resource_path,
            sep="\t",
            dtype=schema_model._return_pandas_dtypes() if schema_model else None,
        )
        logger.info("DataFrame successfully loaded.")
    except Exception as e:
        logger.error(f"Failed to load dataset from {resource_path}: {e}")
        raise

    # Identify boolean columns using pandas type system
    boolean_columns = dataframe_resource.select_dtypes(include=["boolean"]).columns

    if not boolean_columns.empty:
        # Replace NaN with False and ensure dtype is bool
        dataframe_resource[boolean_columns] = (
            dataframe_resource[boolean_columns].fillna(False).astype(bool)
        )

    logger.info(f"DataFrame shape: {dataframe_resource.shape}")
    memory_mb = dataframe_resource.memory_usage(deep=True).sum() / 1024**2
    logger.info(f"Memory usage (MB): {memory_mb:.2f}")

    return dataframe_resource


def validate_schema(
    dataframe: pd.DataFrame,
    resource_name: str,
    enable_validation: bool = False,
) -> None:
    """
    Whether to enable schema validation. Set to False to skip validation.

    Args:
        dataframe (pd.DataFrame): The DataFrame to validate.
        resource_name (str): The key to retrieve the schema from PANDERA_SCHEMAS.
        enable_validation (bool): Whether to perform schema validation.
    """
    if not enable_validation:
        logger.info("Skipping schema validation.")
        return

    schema = PANDERA_SCHEMAS.get(resource_name)
    if schema is None:
        logger.warning(
            f"No schema defined for resource: {resource_name}. Skipping validation."
        )
        return

    try:
        schema.validate(dataframe)
        logger.info("DataFrame complies with the schema.")
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        raise


def filtering_data(resource_name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Apply additional filtering to the data in before using it

    Args:
        resource_name (str): Name of the database, i.e networks, annotations, etc.
        dataframe (pd.DataFrame): DataFrame, for now it is a Pandas DataFrame_

    Returns:
        pd.DataFrame: Returns a Pandas DataFrame
    """
    if resource_name == "annotations":
        dataframe = dataframe

    if resource_name == "complexes":
        dataframe = dataframe

    if resource_name == "enzyme_PTM":
        dataframe = dataframe

    if resource_name == "intercell":
        dataframe = dataframe

    if resource_name == "networks":
        dataframe = dataframe

    return dataframe


def extract_nodes_edges_ontoweaver(resource_name: str, dataframe_resource: pd.DataFrame):

    # Read Ontoweaver mapping file
    mapping_file = ONTOWEAVER_MAPPING_FILES.get(resource_name)
    if mapping_file is None:
        raise ValueError(f"No mapping file found for resource: {resource_name}")

    try:
        with open(mapping_file) as fd:
            mapping = yaml.full_load(fd)
    except FileNotFoundError:
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the mapping file: {e}")

    # Extract nodes and edges with Ontoweaver
    logger.info("Ontoweaver adapter start...")
    nodes, edges = [], []
    adapter = ontoweaver.tabular.extract_table(
        df=dataframe_resource,
        config=mapping,
        separator=":",
        affix="none",
        parallel_mapping=min(32, (os.cpu_count() or 1) + 4),
    )
    nodes += adapter.nodes
    edges += adapter.edges

    logger.info("Ontoweaver adapter end.")

    return nodes, edges


def fuse_and_write(nodes, edges, resource_name):
    """Fuse duplicated nodes and edges and write the output."""
    logger.info("Fuse step starting...")

    schema_path = BIOCYPHER_SCHEMA_PATHS.get(resource_name)
    biocypher_config_path = BIOCYPHER_CONFIG_PATHS.get(resource_name)

    import_file = ontoweaver.reconciliate_write(
        nodes=nodes,
        edges=edges,
        biocypher_config_path=biocypher_config_path,
        schema_path=schema_path,
        separator=", ",
    )
    logger.info("Fuse step end.")
    return import_file


def process_resource(resource_name: str, argument_resource: str):
    """Process a given resource, extract nodes and edges, and update the lists."""

    logger.info(f"Resource Option: {argument_resource}")
    logger.info(f"Resource Name: {resource_name}")

    # EXTRACTION
    logger.info("======================")
    logger.info("=  STEP: Extraction  =")
    logger.info("======================")
    path_resource = access_to_resource(
        resource_name=resource_name,
        argument_resource=argument_resource,
    )

    # LOADING
    logger.info("===================")
    logger.info("=  STEP: Loading  =")
    logger.info("===================")
    dataframe = load_dataframe(path_resource, resource_name=resource_name)
    validate_schema(dataframe, resource_name, enable_validation=False)

    # TRANSFORMATION
    # -- Filtering information
    logger.info("==========================")
    logger.info("=  STEP: Transformation  =")
    logger.info("==========================")
    dataframe = filtering_data(resource_name, dataframe)

    # -- Extract nodes and edges
    nodes, edges = extract_nodes_edges_ontoweaver(
        resource_name=resource_name,
        dataframe_resource=dataframe,
    )

    # -- Fuse nodes, edges and write script for importing to Neo4j
    import_file = fuse_and_write(nodes, edges, resource_name)
    logger.info(f"Processed {resource_name}: {len(nodes)} nodes, {len(edges)} edges.")


def resources_to_process(cli_arguments: argparse.Namespace) -> Dict[str, Any]:
    resource_mapping = {
        key: value
        for key, value in vars(cli_arguments).items()
        if value is not None and key != "verbose"
    }

    return resource_mapping


# ---------------------------------------------------------------------------
# ----------------------    M A I N   F U N T I O N    ----------------------
# ---------------------------------------------------------------------------
def main():

    # Parse CLI arguments
    cli_parsed = parse_arguments()
    logger.info(f"CLI arguments: {cli_parsed}")

    # Map the resources to be processed based on CLI arguments
    resource_mapping = resources_to_process(cli_arguments=cli_parsed)
    logger.info(f"Resources to process: {resource_mapping}")

    # Process the resources (ELT)
    for resource_name, argument_resource in resource_mapping.items():
        process_resource(resource_name, argument_resource)


if __name__ == "__main__":
    main()


# Examples for execute:
# poetry run python weave_knowledge_graph.py -net download
# poetry run python weave_knowledge_graph.py -net ./data_testing/networks/subset_interactions_edgecases.tsv
# poetry run python -m cProfile -s time weave_knowledge_graph.py -net ./data_testing/networks/subset_interactions_edgecases.tsv > profile_.txt

# poetry run python weave_knowledge_graph.py -enz download
