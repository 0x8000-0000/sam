#!/usr/bin/env python3

import unittest
from xml.etree import ElementTree

import sys

sys.path.append("..")

import samparser


class StringWrapper:
    """Adapts an input string to be read from like a stream."""

    def __init__(self, inputString):
        self.strings = inputString.splitlines(keepends=True)
        self.pos = 0

    def readline(self):
        """Simulate reading from a stream"""
        if self.pos < len(self.strings):
            oldPos = self.pos
            self.pos += 1
            return self.strings[oldPos]

        return ""


def isRecordSet(node):
    if node is None:
        return []

    if isinstance(node, samparser.RecordSet):
        return [node]

    return []


def isRecipe(node):
    if node is None:
        return []

    if isinstance(node, samparser.RecordSet) and "recipe" == node.block_type:
        return [node]

    return []


class TestPlainRecordSets(unittest.TestCase):
    def test_simple(self):

        input = StringWrapper(
            """!annotation-lookup: case insensitive
!smart-quotes: on

cookbook: This is the great cookbook

    introduction:

        Some random text

    recipe:: ingredient, amount, unit
        coffee, 50, grams
        milk, 50, ml
        water, 100, ml

    measurements:: source, destination, ratio
        cup, ml, 236
        tbsp, ml, 15
"""
        )

        parser = samparser.SamParser()
        parser.parse(input)

        recordSets = parser.doc.root.find_all(isRecordSet)
        self.assertEqual(len(recordSets), 2)

        recipes = parser.doc.root.find_all(isRecipe)
        self.assertEqual(len(recipes), 1)

        theRecipe = recipes[0]

        self.assertEqual(theRecipe.field_names, ["ingredient", "amount", "unit"])

        self.assertEqual(len(theRecipe.children), 3)

        xmlOutput = ""
        for token in parser.doc.serialize_xml():
            xmlOutput += token.decode()

        tree = ElementTree.fromstring(xmlOutput)


class TestConditionalRecordSets(unittest.TestCase):
    def test_simple(self):

        input = StringWrapper(
            """!annotation-lookup: case insensitive
!smart-quotes: on

cookbook: This is the great cookbook

    introduction:

        Some random text

    recipe:: , ingredient, amount, unit
        , coffee, 50, grams
        ,(?vegan=no) milk, 70, ml
        ,(?vegan=yes)(?fancy=super) oat-milk, 50, ml
        ,(?vegan=yes) soy-milk, 50, ml
        , water, 100, ml

    measurements::(?needed=true)(?super=duper) source, destination, ratio
        cup, ml, 236
        tbsp, ml, 15
"""
        )

        parser = samparser.SamParser()
        parser.parse(input)

        recordSets = parser.doc.root.find_all(isRecordSet)
        self.assertEqual(len(recordSets), 2)

        recipes = parser.doc.root.find_all(isRecipe)
        self.assertEqual(len(recipes), 1)

        theRecipe = recipes[0]

        self.assertEqual(theRecipe.field_names, ["ingredient", "amount", "unit"])
        self.assertTrue(theRecipe.has_condition)

        self.assertEqual(len(theRecipe.children), 5)

        xmlOutput = ""
        for token in parser.doc.serialize_xml():
            xmlOutput += token.decode()

        xmlTree = ElementTree.fromstring(xmlOutput)

        xmlRecipes = list(xmlTree.iter("recipe"))
        self.assertEqual(len(xmlRecipes), 1)
        noCondition = xmlRecipes[0][0]
        self.assertEqual(noCondition.get("conditions"), None)
        oneCondition = xmlRecipes[0][1]
        self.assertEqual(oneCondition.get("conditions"), "vegan=no")
        twoConditions = xmlRecipes[0][2]
        self.assertEqual(twoConditions.get("conditions"), "vegan=yes,fancy=super")


if __name__ == "__main__":
    unittest.main()
