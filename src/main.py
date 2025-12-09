from src.urdf_parser import URDFParser

# Path to your URDF file
urdf_path = "/home/sorin/dev/URDFParser/resources/apartment.urdf"

# Path where ontology should be saved
ontology_path = "robot_ontology.owl"

# Instantiate parser
parser = URDFParser(urdf_path=urdf_path, ontology_path=ontology_path)

# First, parse the URDF
parser.parse()

# List of TBox concepts you defined
concepts = [
    "Wardrobe", "Root", "Armchair", "Table", "Cabinet", "Drawer",
    "Door", "Handle", "Machine", "Countertop", "Cooktop",
    "Diswasher", "Hotplate", "Oven", "Sink", "Sofa", "Tap",
    "Wall", "Link", "Joint", "RevoluteJoint", "PrismaticJoint",
    "FixedJoint", "FloatingJoint", "PlanarJoint", "ContinuousJoint"
]

# Build ontology and save it
parser.build_ontology(concepts)

print("Ontology exported to:", ontology_path)
