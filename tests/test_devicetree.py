#!/usr/bin/env python3

import unittest

from pydevicetree.source import parseTree
from pydevicetree.ast import *

class TestDevicetree(unittest.TestCase):
    def setUp(self):
        self.source = """
        /dts-v1/;
        /* ignore this comment */
        chosen {
            my-cpu = "/cpus/cpu@0";
        };
        / {
            #address-cells = <2>; // ignore this comment
            #size-cells = <2>;
            cpus {
                cpu0: cpu@0 {
                    #address-cells = <1>;
                    compatible = "riscv";
                    reg = <0>;
                };
                cpu@1 {
                    #size-cells = <1>;
                    /* ignore this comment */
                    compatible = "riscv";
                    reg = <1>;
                };
            };
            soc {
                delete-property {
                    delete-me = "foo";
                    /delete-property/ delete-me;
                };
                delete_label: delete-by-label {
                };
                delete-by-name {
                };
                /delete-node/ &delete_label;
                /delete-node/ delete-by-name;
            };
        };
        """

    def test_get_path(self):
        tree = parseTree(self.source)

        cpu0 = tree.match("riscv")[0]
        self.assertEqual(cpu0.get_path(), "/cpus/cpu@0")

    def test_get_by_path(self):
        tree = parseTree(self.source)

        cpu0 = tree.get_by_path("/cpus/cpu@0")
        self.assertEqual(cpu0.name, "cpu")
        self.assertEqual(cpu0.address, 0)
        self.assertEqual(cpu0.get_field("compatible"), "riscv")

        cpus = tree.get_by_path("/cpus")
        self.assertEqual(cpus.name, "cpus")
        self.assertEqual(len(cpus.children), 2)

    def test_delete_directive(self):
        tree = parseTree(self.source)

        soc = tree.get_by_path("/soc")
        self.assertEqual(type(soc), Node)
        self.assertEqual(len(soc.children), 1)

        delete_property = tree.get_by_path("/soc/delete-property")
        self.assertEqual(type(delete_property), Node)
        self.assertEqual(delete_property.get_field("delete-me"), None)

    def test_get_by_label(self):
        tree = parseTree(self.source)

        cpu0 = tree.get_by_label("cpu0")
        self.assertEqual(cpu0.name, "cpu")
        self.assertEqual(cpu0.address, 0)
        self.assertEqual(cpu0.get_field("compatible"), "riscv")

    def test_get_field(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        cpu = tree.children[1].children[0].children[0]

        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.name, "cpu")
        self.assertEqual(cpu.address, 0)
        self.assertEqual(cpu.get_field("compatible"), "riscv")
        self.assertEqual(cpu.get_field("reg"), 0)

    def test_cells(self):
        tree = parseTree(self.source)

        cpu0 = tree.match("riscv")[0]
        cpu1 = tree.match("riscv")[1]
        self.assertEqual(type(cpu0), Node)
        self.assertEqual(type(cpu1), Node)

        self.assertEqual(cpu0.address_cells(), 1)
        self.assertEqual(cpu0.size_cells(), 2)
        self.assertEqual(cpu1.address_cells(), 2)
        self.assertEqual(cpu1.size_cells(), 1)

    def test_match(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(cpu):
            self.assertEqual(type(cpu), Node)
            self.assertEqual(cpu.name, "cpu")
            self.assertEqual(cpu.address, cpu.get_field("reg"))
            self.assertEqual(cpu.get_field("compatible"), "riscv")

        tree.match("riscv", func)

    def test_chosen(self):
        tree = parseTree(self.source)

        self.assertEqual(type(tree), Devicetree)

        def func(values):
            self.assertEqual(values[0], "/cpus/cpu@0")

        tree.chosen("my-cpu", func)

        cpu = tree.get_by_reference("&{/cpus/cpu@0}")
        self.assertEqual(type(cpu), Node)
        self.assertEqual(cpu.get_path(), "/cpus/cpu@0")
        self.assertEqual(cpu.get_field("reg"), 0)

if __name__ == "__main__":
    unittest.main()
