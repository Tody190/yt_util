# -*- coding: utf-8 -*-
__author__ = "yangtao"
import re
import os




class Footage_bk:
    def __init__(self, path, deep=False):
        self.deep = deep
        self.path = path
        self.set_pattern()
        self.__data_data_filter = ["files",
                                   "frames",
                                   "path",
                                   "basename",
                                   "ext",
                                   "footage name",
                                   "frame range",
                                   "nuke read path"]

    def set_pattern(self, basename=None, step=None, frame=None, ext=None):
        if not basename:
            basename = "^.+"
        if not step:
            step = "[._]"
        if not frame:
            frame = "#+|%\d*d|\$F\d*|\d+"
        if not ext:
            ext = "(\..+$)"
        self.pattern = re.compile("(?P<basename>%s)"%basename +
                                  "(?P<step>%s)"%step +
                                  "(?P<frame>%s)"%frame +
                                  "(?P<ext>%s)"%ext)

    def __data_build(self, footage_metadata):
        footage_groups = []
        multiple_filter = True
        if not isinstance(self.__data_data_filter, list):
            self.__data_data_filter = [self.__data_data_filter]
            multiple_filter = False

        for footage_name, footage_data in footage_metadata.items():
            footage = {}
            for filter_key in self.__data_data_filter:
                if filter_key == "frame range":
                    footage["frame range"] = "%s-%s"%(footage_data["frames"][0],
                                                      footage_data["frames"][-1])
                elif filter_key == "nuke read path":
                    footage["nuke read path"] = "%s %s" % (os.path.join(footage_data["path"], footage_data["footage name"]),
                                                           "%s-%s" % (footage_data["frames"][0], footage_data["frames"][-1]))
                else:
                    footage[filter_key] = footage_data[filter_key]

            if multiple_filter:
                footage_groups.append(footage)
            else:
                footage_groups.append(footage_data[self.__data_data_filter[0]])

        return footage_groups

    def __get_footage(self):
        footage_metadata = {}
        if os.path.isdir(self.path):
            for root, dirs, files in os.walk(self.path):
                for f in files:
                    match_file = self.pattern.match(f)
                    if match_file:
                        file_basename = match_file.group("basename")
                        file_step = match_file.group("step")
                        file_ext = match_file.group("ext")
                        file_frame = match_file.group("frame")
                        footage_name = file_basename + file_step + "#"*len(str(file_frame)) + file_ext
                        file_path = os.path.join(root, f).replace("\\", "/")
                        if footage_name not in footage_metadata:
                            footage_metadata[footage_name] = {"files": [file_path],
                                                            "frames": [file_frame],
                                                            "path": root,
                                                            "basename": file_basename,
                                                            "ext": file_ext,
                                                            "footage name": footage_name,
                                                            }
                        else:
                            groups_data = footage_metadata[footage_name]
                            if file_path not in groups_data["files"]:
                                groups_data["files"].append(file_path)
                                groups_data["frames"].append(file_frame)

                if not self.deep:
                    break

        # 排序
        for d in footage_metadata.values():
            if len(d["files"]) >= 2:
                d["files"].sort()
                d["frames"].sort()

        # 返回序列组
        return self.__data_build(footage_metadata)

    def __frame_code_to_re_str(self, frame_code):
        if "#" in frame_code:
            return  "\d{%s}"%len(frame_code)
        if "%" in frame_code:
            num = re.search("\d+", frame_code)
            return "\d{%s}"%str(int(num.group()))

    def get(self, data_filter=None):
        if data_filter:
            self.__data_data_filter = data_filter

        if os.path.isdir(self.path):
            return self.__get_footage()
        else:
            footage_code = os.path.basename(self.path)
            match_file = self.pattern.match(footage_code)
            if match_file:
                basename = match_file.group("basename")
                frame_code = match_file.group("frame")
                ext = match_file.group("ext")
                re_str = self.__frame_code_to_re_str(frame_code)
                if re_str:
                    self.path = os.path.dirname(self.path)
                    self.set_pattern(basename=basename, frame=re_str, ext=ext)
                    return self.__get_footage()


class Footage_group(list):
    def __init__(self):
        self.footage_name = None
        self.basename = None
        # self.ext = None
        # self.frames = None
        # self.frame_range = None

    def add_file(self, file):
        if file not in self:
            self.append(file)
        self.sort()


class Footage(list):
    def __init__(self, files=None):
        self.set_pattern()
        if files:
            self.add_files(files)

    def set_pattern(self, basename=None, frame=None, ext=None):
        if not basename:
            basename = ".+"
        if not frame:
            frame = "((\.|_|-)\d+|(\(|\[|\{)\d+(\}|\]|\)))"
        if not ext:
            ext = ".+"
        self.pattern = re.compile("^" +
                                  "(?P<basename>%s)"%basename +
                                  "(?P<frame>%s)"%frame +
                                  "\." +
                                  "(?P<ext>%s)"%ext +
                                  "$")

    def __get_footage_group(self, re_match):
        basename = re_match.group("basename")
        ext = re_match.group("ext")
        frame = re_match.group("frame")
        frame_nume = re.search("\d+", frame).group()
        frame_len = frame.replace(frame_nume, "#" * len(str(frame_nume)))
        footage_name = basename + frame_len + ".%s"%ext

        for group in self:
            if footage_name == group.footage_name:
                return group

        group = Footage_group()
        group.footage_name = footage_name
        group.basename = basename
        group.ext = ext
        return group

    def add_file(self, file):
        # 获取文件名
        file_name = os.path.basename(file)
        # 正则匹配是否符合序列命名
        re_match = self.pattern.match(file_name)
        if re_match:
            footage_group = self.__get_footage_group(re_match)
            footage_group.append(file)
            self.append(footage_group)
            return True
        else:
            return False

    def add_files(self, files):
        for f in files:
            self.add_file(f)

    # def get(self):
    #     for f in self.__files:
    #         # 获取文件名
    #         file_name = os.path.basename(f)
    #         file_dir = os.path.dirname(f)
    #         # 正则匹配是否符合序列命名
    #         match_file = self.pattern.match(file_name)
    #         if match_file:
    #             file_basename = match_file.group("basename")
    #             file_step = match_file.group("step")
    #             file_ext = match_file.group("ext")
    #             file_frame = match_file.group("frame")
    #             footage_name = file_basename + file_step + "#" * len(str(file_frame)) + file_ext
    #             file_path = os.path.join(file_dir, f).replace("\\", "/")
    #             if footage_name not in footage_metadata:
    #                 footage_metadata[footage_name] = {"files": [file_path],
    #                                                   "frames": [file_frame],
    #                                                   "path": root,
    #                                                   "basename": file_basename,
    #                                                   "ext": file_ext,
    #                                                   "footage name": footage_name,
    #                                                   }
    #             else:
    #                 groups_data = footage_metadata[footage_name]
    #                 if file_path not in groups_data["files"]:
    #                     groups_data["files"].append(file_path)
    #                     groups_data["frames"].append(file_frame)


class Files:
    def __init__(self, path, deep=True):
        self.path = path
        self.deep = deep

    def __get_files(self):
        # 获取所有文件
        file_paths = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                file_path = os.path.join(root, f).replace("\\", "/")
                if os.path.isfile(file_path):
                    file_paths.append(file_path)
            if not self.deep:
                break
        return file_paths

    def get(self):
        pass

    def footage(self):
        files = self.__get_files()
        return Footage(files)




if __name__ == "__main__":
    path = r"D:\temp\ACES\output_beauty"
    #file = r"D:\temp\ACES\output_beauty\h75170.lgt.lighting.v005.%04d.exr"
    a = Files(path)
    for footage_group in a.footage():
        print(footage_group.footage_name)

