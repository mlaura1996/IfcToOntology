import ifcopenshell
from rdflib import Graph, Namespace, URIRef, RDF, Literal
import os

# Define namespaces for the ontology
BEO = Namespace("https://pi.pauwel.be/voc/buildingelement#")
BOT = Namespace("https://w3id.org/bot#")

# Additional relationships namespace
REL = Namespace("http://example.org/ifc/relations#")

def initialize_mapping():
    """
    Initializes the mapping between IFC types and ontology classes.
    """
    return {
        "IfcBuildingElement": BEO.BuildingElement,
        "IfcWall": BEO.Wall,
        "IfcBeam": BEO.Beam,
        "IfcColumn": BEO.Column,
        "IfcSlab": BEO.Slab,
        "IfcRoof": BEO["Slab-ROOF"],
        "IfcWindow": BEO.Window,
        "IfcDoor": BEO.Door,
        "IfcFooting": BEO.Footing,
    }

def initialize_graph():
    """
    Initializes and returns an RDF graph with the BEO, BOT, and REL namespaces.
    """
    g = Graph()
    g.bind("beo", BEO)
    g.bind("bot", BOT)
    g.bind("rel", REL)
    return g

def sanitize_uri_component(component):
    """
    Replaces spaces in a string with underscores to make it URI-safe.
    """
    return component.replace(" ", "_") if isinstance(component, str) else component

def add_hosting_relationships(element, element_uri, ifc_file_name, graph):
    """
    Adds hosting relationships for an IFC element to the RDF graph.

    Parameters:
    - element: The IFC element (e.g., wall).
    - element_uri: The URI of the RDF individual representing the element.
    - ifc_file_name: The name of the IFC file (for URI generation).
    - graph: The RDF graph to add triples to.
    """
    # Check for voiding relationships (e.g., walls hosting openings)
    if hasattr(element, "HasOpenings") and element.HasOpenings:
        for void in element.HasOpenings:
            opening = void.RelatedOpeningElement

            # Check if the opening has fillings (windows/doors)
            if hasattr(opening, "HasFillings") and opening.HasFillings:
                for fill in opening.HasFillings:
                    related_building_element = fill.RelatedBuildingElement
                    if related_building_element:  # Ensure it exists
                        related_building_element_id = sanitize_uri_component(
                            getattr(related_building_element, "GlobalId", str(related_building_element))
                        )
                        related_building_element_uri = URIRef(f"http://example.org/{ifc_file_name}/{related_building_element_id}")

                        # Link the wall to the related building element
                        graph.add((element_uri, BOT.containsElement, related_building_element_uri))



def convert_element_to_rdf(element, ifc_file_name, mapping, graph):
    """
    Converts a single IFC element into RDF triples and adds them to the graph.

    Parameters:
    - element: The IFC element.
    - ifc_file_name: The name of the IFC file (for URI generation).
    - mapping: The mapping between IFC types and ontology classes.
    - graph: The RDF graph to add triples to.
    """
    ifc_type = element.is_a()
    if ifc_type in mapping:
        # Create RDF individual
        element_global_id = sanitize_uri_component(element.GlobalId)
        element_uri = URIRef(f"http://example.org/{ifc_file_name}/{element_global_id}")
        beo_class = mapping[ifc_type]

        # Add individual and class relationship to the graph
        graph.add((element_uri, RDF.type, beo_class))

        # Add RDF label using the "Name" attribute of the IFC element
        if element.Name:
            sanitized_name = sanitize_uri_component(element.Name)
            graph.add((element_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(sanitized_name, lang="en")))

        # Add hosting relationships
        add_hosting_relationships(element, element_uri, ifc_file_name, graph)

def convert_ifc_to_rdf(ifc_file_path, rdf_file_path):
    """
    Converts IfcElements from an IFC file into RDF individuals based on the BEO ontology.

    Parameters:
    - ifc_file_path: Path to the IFC file.
    - rdf_file_path: Path to save the RDF output in Turtle format.
    """
    # Initialize mapping and graph
    ifc_to_beo_mapping = initialize_mapping()
    g = initialize_graph()

    # Load IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Extract the file name without extension for generating URIs
    ifc_file_name = os.path.splitext(os.path.basename(ifc_file_path))[0]

    # Iterate over all elements in the IFC file
    for element in ifc_file.by_type("IfcElement"):
        convert_element_to_rdf(element, ifc_file_name, ifc_to_beo_mapping, g)

    # Serialize RDF graph to a file in Turtle format
    g.serialize(destination=rdf_file_path, format="turtle")

