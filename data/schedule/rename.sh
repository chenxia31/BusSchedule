#!/bin/bash
prefix="route"

# 进入data文件夹

# 使用find命令查找以"road"开头的文件并进行重命名
find . -type f -name "*Route*" -exec sh -c 'new_file=$(echo "$0" | sed "s/Route/$1/"); mv "$0" "$new_file"' {} "$prefix" \;
