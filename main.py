import difflib
from git.repo import Repo

d = difflib.Differ()
# from ptpython.repl import embed
# embed(globals(), locals())

def read_blob(b):
    if not b:
        return []

    if b.name.endswith(".png"):
        return []

    return b.data_stream.read().decode('utf-8').split("\n")


def is_TODO_line(line):
    return "TODO" in line


def show_diff(ca, cb):
    acc0 = 0
    acc1 = 0
    for di in cb.diff(ca):
        a = read_blob(di.a_blob)
        b = read_blob(di.b_blob)

        added_lines = [s.replace("+ ", "") for s in d.compare(a, b) if s.startswith("+ ")]
        removed_lines = [s.replace("- ", "") for s in d.compare(a, b) if s.startswith("- ")]

        added_todo_lines = sum(map(is_TODO_line, added_lines))
        removed_todo_lines = sum(map(is_TODO_line, removed_lines))

        acc0 += added_todo_lines
        acc1 += removed_todo_lines

    return acc0, acc1

def main():
    repo = Repo('~/Desktop/network-observability')

    q = [repo.head.commit]
    seen = set()
    diffpairs = set()
    acc = 0
    while q:
        commit = q.pop()
        if commit in seen:
            continue
        seen.add(commit)

        acc += 1

        # acutal logic
        if len(commit.parents) == 1: # exclude merge commits
            diffpairs = diffpairs.union({(commit, p) for p in commit.parents})

        assert len(commit.parents) <= 2
        q += list(commit.parents)

        # if acc > 50:
            # break

    points = []
    for dp in diffpairs:
        c = dp[0] 
        date = max(c.authored_date, c.committed_date)
        tododiff = show_diff(*dp)
        points.append((date, *tododiff, c))

    points.sort(key=lambda s: s[0])
    for p in points:
        # print also commit
        # print(f"{p[0]}, {-p[2]}, {p[1]}, {p[3]}")
        print(f"{p[0]}, {-p[2]}, {p[1]}, {p[3]}")
    
if __name__ == "__main__":
    main()
