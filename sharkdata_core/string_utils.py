#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from fnmatch import fnmatch


def extract_pattern_values(
    string_to_parse,
    pattern_strings,
    pattern_var_start_sign="<",
    pattern_var_stop_sign=">",
):
    if type(pattern_strings) is list:
        for pattern_string in pattern_strings:
            identifier_values = extract_pattern_values(
                string_to_parse,
                pattern_string,
                pattern_var_start_sign,
                pattern_var_stop_sign,
            )
            if identifier_values != None:
                break
        return identifier_values
    else:
        pattern_string = pattern_strings

    keys = get_pattern_keys(
        pattern_string, pattern_var_start_sign, pattern_var_stop_sign
    )

    if not does_pattern_match(
        string_to_parse,
        pattern_string,
        keys,
        pattern_var_start_sign,
        pattern_var_stop_sign,
    ):
        return None

    identifier_values = {}
    file_name_parts = split_by_delimiters(
        pattern_string, delimiters=[pattern_var_start_sign, pattern_var_stop_sign]
    )
    file_name_parts = [
        part for part in file_name_parts if part != ""
    ]  # remove empty parts
    checked_part = ""
    for index, part in enumerate(file_name_parts):
        start_pos = len(checked_part)
        if part in keys:
            if index == len(file_name_parts) - 1:
                stop_pos = len(string_to_parse)
            else:
                next_part = file_name_parts[index + 1]
                stop_pos = string_to_parse.find(next_part, start_pos + 1)
            value_string = string_to_parse[start_pos:stop_pos]
            identifier_values[part] = value_string
            checked_part += value_string
        else:
            if not string_to_parse[start_pos:].startswith(part):
                return None
            checked_part += part
    return identifier_values


def does_pattern_match(
    string_to_parse,
    pattern_string,
    keys,
    pattern_var_start_sign="<",
    pattern_var_stop_sign=">",
):
    match_string = pattern_string
    for key in keys:
        key_string = "%s%s%s" % (pattern_var_start_sign, key, pattern_var_stop_sign)
        match_string = match_string.replace(key_string, "*")
    return fnmatch(string_to_parse, match_string)


def get_pattern_keys(
    pattern_string, pattern_var_start_sign="<", pattern_var_stop_sign=">"
):
    keys = []
    parts = pattern_string.split(pattern_var_start_sign)

    for part in parts:
        if pattern_var_stop_sign in part:
            key_str, _ = part.split(pattern_var_stop_sign)
            keys.append(key_str)

    return keys


def split_by_delimiters(string_to_split, delimiters):
    split_string = []
    previous_split_string = [string_to_split]
    for delimiter in delimiters:
        split_string = []
        for string_part in previous_split_string:
            split_string.extend(string_part.split(delimiter))
        previous_split_string = split_string
    return split_string
