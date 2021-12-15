import ast
import copy
import itertools
import re

params = []
functions = []
constants = []
rules = []
constructors = {}
text = []
variables = {}
eqVars = {}
log = ""

def write(res):
    with open("result", "w") as f:
        print(res)
        f.write("Syntax error")
    quit()

# УНИФИКАТОР
# ----------------------------------------------
#

def getArgsList(argsString):
    start = 0
    end = 0
    argsDeclarations = []
    opencount = 0
    for symb in argsString:
        if symb == "(":
            opencount += 1
        if symb == ")":
            opencount -= 1
        if (symb == "," and opencount == 0):
            argsDeclarations.append(argsString[start:end])
            start = end+1
        elif end == len(argsString)-1:
            argsDeclarations.append(argsString[start:])
        end += 1
    return argsDeclarations


def parseTerm(term, k):
    global constructors
    if "(" not in term:
        if term not in constants:
            return [term+str(k)]
        else:
            return [term]

    termname = term.split(term[term.index("(")])[0]
    argsList = getArgsList(term[term.index("(") + 1:len(term) - 1])
    parsedArgs = []
    for arg in argsList:
        parsedArgs.append(parseTerm(arg,k))
    # print("term " + term)
    # # print(parsedArgs)
    # if len(parsedArgs) != int(constructors[termname]):
    #     write("Wrong term syntax")
    #     quit()
    return [termname, parsedArgs]


def unificateTerms(term1, term2):
    global log
    global variables, constructors, constants, parsedterm1, parsedterm2, eqVars
    if (term1[0] == term2[0]) and ((term1[0] in constants and term2[0] in constants) or (term1[0] in variables.keys() and term2[0] in variables.keys())):
        pass

    elif term1[0] != term2[0] and term1[0] in variables.keys() and term2[0] in variables.keys():
        eqVars[term1[0]].append(term2[0])
        eqVars[term2[0]].append(term1[0])

    elif term1[0] != term2[0] and term1[0] in variables.keys() and term2[0] in constants:
        variables[term1[0]].append(term2[0])

    elif term1[0] != term2[0] and term1[0] in constants and term2[0] in variables.keys():
        variables[term2[0]].append(term1[0])

    elif term1[0] != term2[0] and term1[0] in constructors.keys() and term2[0] in variables.keys():
        if term2[0] in str(term1):
            changedVariable = str(term1).replace(term2[0], "@"+term2[0])
            changedVariable = ast.literal_eval(changedVariable)
            variables[term2[0]].append(changedVariable)
        else:
            variables[term2[0]].append(term1)

    elif term1[0] != term2[0] and term1[0] in variables.keys() and term2[0] in constructors.keys():
        if term1[0] in str(term2):
            changedVariable = str(term2).replace(term1[0], "@" + term1[0])
            changedVariable = ast.literal_eval(changedVariable)
            variables[term1[0]].append(changedVariable)
        else:
            variables[term1[0]].append(term2)

    elif term1[0] == term2[0] and term1[0] in constructors.keys() and term2[0] in constructors.keys():
        for i in range(len(term1[1])):

            unificateTerms(term1[1][i], term2[1][i])

    else:
        log = "Can not be unificated"


def include(x, mas):
    for el in mas:
        if str(el) == str(x):
            return True
    return False


def result(parsedterm):
    global variables, eqVars, resString
    if parsedterm[0][0] == "@":
        resString += parsedterm[0][1]
    elif parsedterm[0] in variables.keys():
        if len(variables[parsedterm[0]]) == 0 and len(eqVars) != 0:
            mas = eqVars[parsedterm[0]].copy()
            mas.append(parsedterm[0])
            resString += sorted(mas)[0]
        elif len(variables[parsedterm[0]]) == 0 and len(eqVars) == 0:
            resString += parsedterm[0]
        else:
            if type(variables[parsedterm[0]][0]) == list:
                result(variables[parsedterm[0]][0])
            else:
                resString += str(variables[parsedterm[0]][0])
    elif parsedterm[0] in constants:
        resString += parsedterm[0]
    elif parsedterm[0] in constructors.keys():
        resString += (parsedterm[0] + "(")
        i = 0
        for arg in parsedterm[1]:
            result(arg)
            if i != len(parsedterm[1])-1:
                resString += ","
            i += 1
        resString += ")"
        return resString

# ---------------------------------------------
# ---------------------------------------------
# ---------------------------------------------

def extract_params(line):
    res = ['']
    balance = 0
    for c in line:
        if balance > 0:
            write("Wrong terms syntax with brackets at " + line)
        if c == ',' and balance == 0:
            res.append('')
        else:
            res[-1] += c

            if c == '(':
                balance -= 1
            elif c == ')':
                balance += 1
    return res


def parse_term(line):
    # print(str)
    regexp = r'([a-zA-Z]+|([a-zA-Z]+\(.*\)))'
    if not re.fullmatch(regexp, line):
        write("Wrong terms syntax at " + line)
    if "(" and ")" not in line:
        if line not in params and line not in constants:
            constants.append(line)
        return [line]

    if (line.find("(") == -1 and line.find(")") != -1) or (line.find("(") != -1 and line.find(")") == -1):
        write("Wrong brackets at " + line)

    if line.find("(") > line.find(")"):
        write("Wrong brackets at " + line)

    open_ind = line.find("(")
    close_ind = line.rfind(")")
    terms = [parse_term(term) for term in extract_params(line[open_ind+1:close_ind])]

    if line[:open_ind] not in functions:
        functions.append(line[:open_ind])
    if line[:open_ind] not in constructors.keys():
        constructors[line[:open_ind]] = len(terms)
    elif len(terms) != constructors[line[:open_ind]]:
        print(line)
        write("Error with count of arguments of " + line[:open_ind])

    return [line[:open_ind]] + terms


def parse_terms(line):
    line = line.replace(' ', '')
    if "->" not in line:
        write("Error in " + line)
    term1 = parse_term(line.split('->')[0])
    term2 = parse_term(line.split("->")[1])
    # print(str(term1) + "->" + str(term2))
    rules.append([term1, term2])


def parse(path):
    global params
    with open(path) as file:
        lines = file.read().split('\n')
        print(lines)
        text = file.read().split('\n')
        # print(lines)

        if len(lines) < 2:
            write("Error")

        params_r = r'\[(([a-zA-Z]+)(,[a-zA-Z]*)*)?\]'
        if not re.fullmatch(params_r, lines[0].strip()):
            write("Error in first line")
        params = lines[0].strip()[1:-1].split(",")
        for line in lines[1:]:
            if line.strip() != "":
                parse_terms(line)
        return lines


def check_functions_and_const(functions, constants):
    for func in functions:
        if func in constants:
            write("Error, " + func + " is function and constant")


def get_term(rule):
    rule = rule.strip()
    term = rule.split("->")[1].strip()
    return term


def unif(term1, term2):
    global resString
    global log
    parsedterm1 = parseTerm(term1, 1)
    parsedterm2 = parseTerm(term2, 2)
    print(parsedterm1)
    print(parsedterm2)
    unificateTerms(parsedterm1, parsedterm2)

    for var in eqVars.keys():
        vars = eqVars[var].copy()
        for equalvar in eqVars[var]:
            if equalvar not in vars:
                vars.append()
        eqVars[var] = vars

    for var in variables.keys():
        values = variables[var].copy()
        for equalvar in eqVars[var]:
            for newValue in variables[equalvar]:
                if not include(newValue, values):
                    if var in str(newValue):
                        log = "Can not be unificated"
                    values.append(newValue)
            if len(values) > 1:
                log = "Can not be unificated"
            variables[var] = values

    if log == "Can not be unificated":
        return log
    return result(parsedterm2)


text = parse("test.trs")[1:]
if len(rules) == 0:
    write("there no rules")
check_functions_and_const(functions, constants)


def is_lex():
    for k, v in constructors.items():
        if v > 1:
            return False
    if len(constants) > 0:
        return False
    if len(functions) > 20:
        return False
    return True



def check_permutation(permutation, arr1, arr2):
    for i in range(len(arr1)):
        term1 = arr1[i]
        term2 = arr2[i]
        res = check_rule_perm(permutation, term1, term2)
        if not res:
            return False
    return True


if is_lex():
    permutations = list(itertools.permutations(functions))
    # print(permutations)
    arr1 = []
    arr2 = []
    for rule in rules:
        term1 = rule[0]
        str1 = ""
        term2 = rule[1]
        str2 = ""
        string_arr1 = []
        string_arr2 = []
        while True:
            if term1[0] in params:
                break
            else:
                string_arr1.append(term1[0])
                term1 = term1[1]
        while True:
            if term2[0] in params:
                break
            else:
                string_arr2.append(term2[0])
                term2 = term2[1]
        arr1.append(string_arr1)
        arr2.append(string_arr2)
    # print(arr1)
    # print(arr2)






# for rule1 in text:
#     rule1 = rule1.strip()
#     term1 = rule1.split("->")[1].strip()
#     for rule2 in text:
#         for var in params:
#             variables[var.strip() + "1"] = []
#             variables[var.strip() + "2"] = []
#             eqVars[var.strip() + "1"] = []
#             eqVars[var.strip() + "2"] = []
#
#         rule2 = rule2.strip()
#         term2 = rule2.split("->")[0].strip()
#         resString = ""
#         unificator = unif(term1, term2)
#         print(unificator)