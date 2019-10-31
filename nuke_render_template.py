# -*- coding: utf-8 -*-
__author__ = "yangtao"
import nuke

import sys
import re
import os




class Nuke_Render_Template:
    def __init__(self, template_path):
        self.template = template_path
        nuke.scriptReadFile(self.template)

    def __set_item_value(self, node, node_data):
        for item, value in node_data.items():
            node_type = node.Class()
            if node_type == "Read":
                self.readnode.append(node)
                if item == "file":
                    node[item].fromUserText(value)
            elif node_type == "Write":
                self.wirtenode.append(node)
            else:
                node[item].setValue(value)

    def __set_node_data(self, nodes_data):
        for node_name, node_data in nodes_data.items():
            node = nuke.toNode(node_name)
            if not node:
                raise Exception("Can not find Node name %s"%node)
            self.__set_item_value(node, node_data)

    def __find_nodes(self, type):
        nodes = []
        for node in nuke.allNodes():
            if node.Class() == type:
                nodes.append(node)
        return nodes

    def render(self, input_path, export_path, frame_range, nodes_data=None):
        if nodes_data:
            self.__set_node_data(nodes_data)

        frame_range_pattern = re.match("^(?P<first_frame>\d+)[\s,;_\-](?P<last_frame>\d+)$", frame_range)
        if not frame_range_pattern:
            raise ValueError("%s 参数错误"%frame_range)
        first_frame = int(frame_range_pattern.group("first_frame"))
        last_frame = int(frame_range_pattern.group("last_frame"))

        for readnode in self.__find_nodes("Read"):
            readnode["file"].fromUserText(input_path)

        for wirtenode in self.__find_nodes("Write"):
            if os.path.isdir(export_path):
                export_basename = os.path.basename(wirtenode["file"].value())
                export_path = os.path.join(export_path, export_basename)
            wirtenode["file"].fromUserText(export_path)
            nuke.execute(wirtenode, first_frame, last_frame)




if __name__ == "__main__":
    script = sys.argv[0]
    template = sys.argv[1]
    input_path = sys.argv[2]
    export_path = sys.argv[3]
    frame_range = sys.argv[4]
    try:
        nodes_data = sys.argv[5]
    except:
        nodes_data = None
    NRT = Nuke_Render_Template(template)
    NRT.render(input_path, export_path, frame_range, nodes_data)