#! /usr/bin/env python3
# :vim:et ai sw=4 ts=4 sts=4 :
from collections import Counter
from csv import DictReader


def extract_names(fname):
    all_names = Counter()
    with open(fname, "r") as f:
        for line in DictReader(f, delimiter="\t"):
            namestr = line["Vote-Distinct"]
            names = namestr.split("-")
            all_names.update(names)
    return all_names


# Pattern minilanguage:
# 1..9 : candidates best rank on this ballot.
# W : WriteIn
# N : No Vote
# O : overvote
# X : W, N, or O

special_codes = {
    "No Vote": "N",
    "WriteIn": "W",
    "overvote": "O",
}


def is_major_candidate(c):
    return c not in special_codes


def classify_names(names):
    # Set earliest rank latest.
    rank_for_name = dict(
        map(
            reversed,
            reversed(list(enumerate(names, start=1))),
        )
    )
    pattern = []
    for name in names:
        if is_major_candidate(name):
            pattern.append(str(rank_for_name[name]))
            continue
        pattern.append(special_codes[name])
    return "".join(pattern)


def extract_patterns(fname):
    all_patterns = Counter()
    with open(fname, "r") as f:
        for line in DictReader(f, delimiter="\t"):
            namestr = line["Vote-Distinct"]
            cnt = int(line["Cnt"])
            names = namestr.split("-")
            pattern = classify_names(names)
            all_patterns.update({pattern: cnt})
    return all_patterns


scores_for_pattern = {
    # Confused special cases, with clear intent
    "1NN4": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "1114": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "N23N": ([0, 1, 0, 0], [0, 0, 1, 0]),
    "1212": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "1211": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "121N": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "1222": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "122N": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "1133": ([1, 0, 0, 0], [0, 0, 1, 0]),
    "1N3N": ([1, 0, 0, 0], [0, 0, 1, 0]),
    "N2NN": ([0, 1, 0, 0], [0, 0, 0, 0]),
    "1233": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "N234": ([0, 1, 0, 0], [0, 0, 1, 0]),
    "113N": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "12NW": ([1, 0, 0, 0], [0, 1, 0, 0]),

    # 2 or 3 marked: effective 3-ranks, given 3
    "12NN": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "123N": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "12WN": ([1, 0, 0, 0], [0, 1, 0, 0]),
    "1W3N": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "W23N": ([0, 0, 0, 0], [0, 1, 0, 0]),
    "W2NN": ([0, 0, 0, 0], [0, 1, 0, 0]),

    # 3-ranks with good indicator of acceptable
    "12N4": ([1, 1, 0, 0], [0, 0, 0, 0]),
    "1N34": ([1, 0, 0, 0], [0, 0, 0, 0]),

    # Bullets
    "1NNN": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "1WNN": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "1111": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "111N": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "11NN": ([1, 0, 0, 0], [0, 0, 0, 0]),

    # Bullets -- assuming O is equal ranking of others.
    "1NNO": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "1ONN": ([1, 0, 0, 0], [0, 0, 0, 0]),

    # Wasted
    "NNNN": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "WNNN": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "WWWW": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "ONNN": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "NNNO": ([0, 0, 0, 0], [0, 0, 0, 0]),

    # Uninterpretable
    "O2NN": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "ONN4": ([0, 0, 0, 0], [0, 0, 0, 0]),
    "NNN4": ([0, 0, 0, 0], [0, 0, 0, 0]),

    # Four-ranks.  Hard, but we'll binarize
    "W234": ([0, 1, 0, 0], [0, 0, 0, 0]),
    "1W34": ([1, 0, 0, 0], [0, 0, 0, 0]),
    "12W4": ([1, 1, 0, 0], [0, 0, 0, 0]),
    "123W": ([1, 1, 0, 0], [0, 0, 0, 0]),
    "12WW": ([1, 1, 0, 0], [0, 0, 0, 0]),
}


def approval_report(fname):
    unhandled_patterns = Counter()
    approval_votes = Counter()
    partial_votes = Counter()
    with open(fname, "r") as f:
        for line in DictReader(f, delimiter="\t"):
            namestr = line["Vote-Distinct"]
            cnt = int(line["Cnt"])
            names = namestr.split("-")
            pattern = classify_names(names)
            if pattern in scores_for_pattern:
                full, partial = scores_for_pattern[pattern]
                update = calc_update(names, full, cnt)
                approval_votes.update(update)
                update = calc_update(names, partial, cnt)
                partial_votes.update(update)
            else:
                unhandled_patterns.update({pattern: cnt})

    return approval_votes, partial_votes, unhandled_patterns


def calc_update(names, scores, cnt):
    return {n: cnt * s for (n, s) in zip(names, scores) if s}
