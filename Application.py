import IfcParsing



ifc_file = "Models/ExampleModel.ifc"


rdf_file = "Models/ExampleModel.ttl"
IfcParsing.convert_ifc_to_rdf(ifc_file, rdf_file)



