# TerminatorBattle2021

Выложена тестовая группа TRS:
- Dickson --- лексикографический порядок на *n*-ках (мономиальный порядок);
- Lex --- лексикографический порядок на именах конструкторов;
- Kruskal --- незавершающиеся TRS с разрастанием;
- WFMA --- TRS с оценкой в ФуМА;
- Loop --- незавершающиеся TRS с простым зацикливанием.

Вместо `dummy_terminator` вызываете в скрипте свой прувер. Скрипт выбрасывает тестовые trs в файл `test.trs` и читает результат работы прувера из файла `result` (без расширения) в формате True-False-Unknown-Syntax error. 
