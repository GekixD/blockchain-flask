#!/bin/bash
cd src || exit 1
grep -r --include='*.py' 'TODO:' . | sed -E 's/.*TODO:/TODO:/' > todo_list.txt
echo "TODO list has been created in src/todo_list.txt"