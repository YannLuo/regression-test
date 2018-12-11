from unidiff import PatchSet


class Diff(object):
    def __init__(self, src_file, tar_file, hunk_infos):
        self.src_file = src_file
        self.tar_file = tar_file
        self.hunk_infos = hunk_infos

    def __str__(self):
        return f"Diff <src_file: {self.src_file}  tar_file: {self.tar_file}  hunk_infos: {self.hunk_infos}>"

    def __repr__(self):
        return f"Diff <src_file: {self.src_file}  tar_file: {self.tar_file}  hunk_infos: {self.hunk_infos}>"


def dump_one_hunk(hunk):
    src_st_lineno = hunk.source_start
    tar_st_lineno = hunk.target_start
    d_cnt = 0
    delete_linenos = []
    a_cnt = 0
    add_linenos = []
    # print(hunk)
    for line in hunk.source:
        if line.startswith('-'):
            delete_linenos.append(src_st_lineno + d_cnt)
            d_cnt += 1
        else:
            d_cnt += 1
    for line in hunk.target:
        if line.startswith('+'):
            add_linenos.append(tar_st_lineno + a_cnt)
            a_cnt += 1
        else:
            a_cnt += 1
    delete_linenos = sorted(delete_linenos)
    add_linenos = sorted(add_linenos)
    return {
        "d": delete_linenos,
        "a": add_linenos
    }


def dump_one_patch(patch):
    src_file = patch.source_file
    tar_file = patch.target_file
    delete_linenos = []
    add_linenos = []
    for hunk in patch:
        hunk_info = dump_one_hunk(hunk)
        delete_linenos.extend(hunk_info["d"])
        add_linenos.extend(hunk_info["a"])
    modify_info = {
        "d": delete_linenos,
        "a": add_linenos
    }
    return Diff(src_file, tar_file, modify_info)


def parse_diff(diff):
    patches = PatchSet(diff)
    diff = []
    for patch in patches:
        patch_info = dump_one_patch(patch)
        diff.append(patch_info)
    return diff
