#!/usr/bin/python3

import os
import sys
import time
import shutil


class ArgumentsMap:
    """
    Analysis args from string list into key-value
    """

    def __init__(self, args):
        """
        :type args: List[str]
        :param args: sys.argv
        """
        self.__data = dict()
        for i in range(len(args) - 1):
            if args[i].startswith("--"):
                if args[i + 1].startswith("--"):
                    key = args[i][2:]
                    self.__data[key] = True
                else:
                    key = args[i][2:]
                    value = args[i + 1]
                    self.__data[key] = value
        if args[-1].startswith("--"):
            key = args[-1][2:]
            self.__data[key] = True

    def query(self, key):
        if key not in self.__data:
            raise Exception("key %s not in args" % key)
        return self.__data[key]

    def query_default(self, key, default_value):
        if key in self.__data:
            return self.__data[key]
        else:
            return default_value

    def query_all(self):
        return self.__data


class TBUFileName:
    def __init__(self, prefix: str, tick: int, suffix: str = "tbu"):
        assert prefix.find(".") < 0, "prefix should'n contain '.'"
        assert suffix.find(".") < 0, "suffix should'n contain '.'"
        self.prefix = prefix
        self.tick = tick
        self.suffix = suffix

    def __str__(self):
        return "{}.{}.{}".format(
            self.prefix,
            self.tick,
            self.suffix
        )

    @staticmethod
    def decode(filename: str):
        segments = filename.split(".")
        assert len(segments) == 3, "invalid filename"
        return TBUFileName(
            prefix=segments[0],
            tick=int(segments[1]),
            suffix=segments[2]
        )


def main():
    args = ArgumentsMap(sys.argv)
    # necessary parameters
    save_path = args.query("path")
    command_script = args.query("cmd")
    generated_file_name = args.query("gen_name")
    save_name = args.query("save_name")

    decrease_size_check = float(args.query_default("check_size", "0"))
    version_count = int(args.query_default("version_count", "1"))

    assert version_count > 0, "version count must greater than 0"

    # prepare file path
    os.makedirs(os.path.join(save_path, "versions"), exist_ok=True)
    os.makedirs(os.path.join(save_path, "permanent"), exist_ok=True)

    # execute shell for get file
    os.system(command_script)

    # move file by given name
    tbu_fn = TBUFileName(save_name, int(time.time() * 1000000))
    shutil.move(
        generated_file_name,
        os.path.join(save_path, "versions", str(tbu_fn))
    )

    # verify last 2 files and check is decreased
    tbu_files = [f for f in os.listdir(os.path.join(save_path, "versions")) if f.endswith(".tbu")]
    tbu_files.sort()
    if decrease_size_check > 0 and len(tbu_files) >= 2:
        last_size = os.path.getsize(
            os.path.join(save_path, "versions", tbu_files[-1])
        )

        before_last_size = os.path.getsize(
            os.path.join(save_path, "versions", tbu_files[-2])
        )

        if before_last_size * decrease_size_check > last_size:
            shutil.copy(
                os.path.join(save_path, "versions", tbu_files[-2]),
                os.path.join(save_path, "permanent", tbu_files[-2])
            )

    # version manager
    if version_count > 0:
        for fn in tbu_files[:-version_count]:
            os.remove(os.path.join(save_path, "versions", fn))


if __name__ == '__main__':
    main()
