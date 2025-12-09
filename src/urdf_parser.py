import xml.etree.ElementTree as ET
from typing import List, Dict

from owlready2 import *
import xml.etree.ElementTree as ET
from typing import List, Dict


class URDFParser:
    def __init__(self, urdf_path: str, ontology_path: str = "robot_ontology.owl"):
        self.urdf_path = urdf_path
        self.ontology_path = ontology_path
        self.links: List[str] = []
        self.joints: Dict[str, Dict[str, str]] = {}
        self.parent_child_relations: Dict[str, List[str]] = {}

        # Create ontology
        self.onto = get_ontology(f"file://{self.ontology_path}")

    def parse(self):
        tree = ET.parse(self.urdf_path)
        root = tree.getroot()

        # Extract links
        for link in root.findall('link'):
            name = link.get('name')
            if name:
                self.links.append(name)

        # Extract joints
        for joint in root.findall('joint'):
            joint_name = joint.get('name')
            joint_type = joint.get('type')
            parent = joint.find('parent')
            child = joint.find('child')
            parent_name = parent.get('link') if parent is not None else None
            child_name = child.get('link') if child is not None else None

            self.joints[joint_name] = {
                'parent': parent_name,
                'child': child_name,
                'type': joint_type
            }

            # Build parent -> children map (hasPart)
            if parent_name and child_name:
                if parent_name not in self.parent_child_relations:
                    self.parent_child_relations[parent_name] = []
                self.parent_child_relations[parent_name].append(child_name)

    def map_links_to_concepts(self, concepts: list) -> dict:
        mapped = {}
        concepts_lower = {c.lower(): c for c in concepts}

        for link in self.links:
            normalized = ''.join([ch for ch in link if not ch.isdigit()])
            parts = normalized.split('_')
            parts = [p.lower() for p in parts if p]

            matched_concept = None
            for part in reversed(parts):
                for concept_l, concept_original in concepts_lower.items():
                    if concept_l in part:
                        matched_concept = concept_original
                        break
                if matched_concept:
                    break

            mapped[link] = matched_concept

        return mapped

    def build_ontology(self, concepts: list):
        with self.onto:
            # Create classes dynamically
            class Link(Thing):
                pass

            class Joint(Thing):
                pass

            # Joint type subclasses
            class RevoluteJoint(Joint):
                pass

            class PrismaticJoint(Joint):
                pass

            class FixedJoint(Joint):
                pass

            class FloatingJoint(Joint):
                pass

            class PlanarJoint(Joint):
                pass

            class ContinuousJoint(Joint):
                pass

            # Domain classes (user-provided concepts)
            concept_classes = {}
            for concept in concepts:
                if concept in ["Link", "Joint",
                               "RevoluteJoint", "PrismaticJoint", "FixedJoint",
                               "FloatingJoint", "PlanarJoint", "ContinuousJoint"]:
                    continue  # skip classes already defined

                concept_classes[concept] = types.new_class(concept, (Link,))

            # Object properties
            class hasPart(ObjectProperty, TransitiveProperty):
                domain = [Link]
                range = [Link]

            class hasParentLink(ObjectProperty):
                domain = [Joint]
                range = [Link]

            class hasChildLink(ObjectProperty):
                domain = [Joint]
                range = [Link]

            # Create link individuals
            link_individuals = {}
            for link in self.links:
                link_individuals[link] = Link(link)

            # Assign concepts by substring matching
            mapped = self.map_links_to_concepts(concepts)
            for link, concept in mapped.items():
                if concept is not None:
                    link_individuals[link].is_a.append(concept_classes[concept])

            # Create joint individuals and link relationships
            for joint_name, info in self.joints.items():
                joint_type = info['type']
                parent = info['parent']
                child = info['child']

                # Map type to class
                joint_class_map = {
                    'revolute': RevoluteJoint,
                    'continuous': ContinuousJoint,
                    'prismatic': PrismaticJoint,
                    'fixed': FixedJoint,
                    'floating': FloatingJoint,
                    'planar': PlanarJoint
                }

                cls = joint_class_map.get(joint_type.lower(), Joint)

                joint_ind = cls(joint_name)
                if parent:
                    joint_ind.hasParentLink.append(link_individuals[parent])
                if child:
                    joint_ind.hasChildLink.append(link_individuals[child])
                    link_individuals[parent].hasPart.append(link_individuals[child])

        self.onto.save(file=self.ontology_path, format="rdfxml")
