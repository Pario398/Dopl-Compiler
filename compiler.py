def main():
    import sys

    if len(sys.argv) < 2:
        return
    with open(sys.argv[1], 'r') as file:
        code = file.read()
    context = {
        'tokens': tokenize(code),
        'pointer': 0,
        'variables': {},
        'dataType': None
    }
    print("ok" if readProgram(context) else "error")

def read(ctx):
    token = current(ctx)
    ctx['pointer'] += 1
    return token

def current(ctx):
    return ctx['tokens'][ctx['pointer']] if ctx['tokens'] and ctx['pointer'] < len(ctx['tokens']) else None

def readToken(ctx, expected):
    return expected == read(ctx)

def tokenize(program):
    program = program.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    program = program.replace('(', ' ( ').replace(')', ' ) ')
    program = program.replace(';', ' ; ').replace(',', ' , ')
    program = program.replace('.plus.', ' .plus. ').replace('.minus.', ' .minus. ')
    program = program.replace('.mul.', ' .mul. ').replace('.div.', ' .div. ')
    program = program.replace('.and.', ' .and. ').replace('.or.', ' .or. ')
    program = program.replace('.eq.', ' .eq. ').replace('.ne.', ' .ne. ')
    program = program.replace('.lt.', ' .lt. ').replace('.gt.', ' .gt. ')
    program = program.replace('.le.', ' .le. ').replace('.ge.', ' .ge. ')
    program = program.replace('character', ' character ').replace('do', ' do ')
    program = program.replace('else', ' else ').replace('endif', ' endif ')
    program = program.replace('endloop', ' endloop ').replace('finish', ' finish ')
    program = program.replace('integer', ' integer ').replace('logical', ' logical ')
    program = program.replace('loopif', ' loopif ').replace('print', ' print ')
    program = program.replace('start', ' start ').replace('then', ' then ')
    program = program.replace('<-', ' <- ').replace('.not.', ' .not. ')
    tokens = program.split()
    return [token for token in tokens if token]

def readProgram(ctx):
    return (
        readToken(ctx, 'start') and
        readDeclarations(ctx) and
        readStatements(ctx) and
        readToken(ctx, 'finish') and
        readToken(ctx, None)
    )

def readDeclarations(ctx):
    while current(ctx) in ['integer', 'character', 'logical']:
        valid = readOneDeclaration(ctx) and readToken(ctx, ';')
        if not valid:
            return False
    return True

def readOneDeclaration(ctx):
    ctx['dataType'] = read(ctx)
    return readIdentifiers(ctx)

def readIdentifiers(ctx):
    readOneIdentifier(ctx)
    while current(ctx) == ',':
        read(ctx)
        if not readOneIdentifier(ctx):
            return False
    return True

def readOneIdentifier(ctx):
    keywords = [
        'character', 'do', 'else', 'endif', 'endloop', 'finish', 'if',
        'integer', 'logical', 'loopif', 'print', 'start', 'then'
    ]
    identifier = read(ctx)
    isAlphanumeric = identifier.isidentifier()
    isNotKeyword = identifier not in keywords
    isUnique = ctx['variables'].get(identifier) is None
    ctx['variables'][identifier] = ctx['dataType']
    return isAlphanumeric and isNotKeyword and isUnique

def readStatements(ctx):
    while current(ctx) in ['if', 'print', 'loopif'] or current(ctx) == '<-':
        if not readOneStatement(ctx) or not readToken(ctx, ';'):
            return False
    return True

def readOneStatement(ctx):
    ctx['expressionType'] = 'integer'
    if current(ctx) == 'if':
        return readConditional(ctx)
    elif current(ctx) == 'print':
        return readPrint(ctx)
    elif current(ctx) == 'loopif':
        return readLoop(ctx)
    else:
        return readAssignment(ctx)

def readAssignment(ctx):
    identifier = read(ctx)
    return (
        readToken(ctx, '<-') and
        readExpression(ctx) and
        ctx['expressionType'] == ctx['variables'].get(identifier)
    )

def readConditional(ctx):
    return (
        readToken(ctx, 'if') and
        readExpression(ctx) and
        ctx['expressionType'] == 'logical' and
        readToken(ctx, 'then') and
        readStatements(ctx) and
        (current(ctx) != 'else' or (readToken(ctx, 'else') and readStatements(ctx))) and
        readToken(ctx, 'endif')
    )

def readPrint(ctx):
    return readToken(ctx, 'print') and readExpression(ctx)

def readLoop(ctx):
    return (
        readToken(ctx, 'loopif') and
        readExpression(ctx) and
        ctx['expressionType'] == 'logical' and
        readToken(ctx, 'do') and
        readStatements(ctx) and
        readToken(ctx, 'endloop')
    )

def readExpression(ctx):
    if not readTerm(ctx):
        return False
    while currentIsBinaryOp(ctx):
        read(ctx)
        if not readTerm(ctx):
            return False
    return True

def currentIsBinaryOp(ctx):
    if currentIsArithmeticOp(ctx):
        return True
    if currentIsRelationalOp(ctx) or currentIsLogicalOp(ctx):
        ctx['expressionType'] = 'logical'
        return True
    return False

def currentIsArithmeticOp(ctx):
    return current(ctx) in ['.plus.', '.minus.', '.mul.', '.div.']

def currentIsLogicalOp(ctx):
    return current(ctx) in ['.and.', '.or.']

def currentIsRelationalOp(ctx):
    return current(ctx) in ['.eq.', '.ne.', '.lt.', '.gt.', '.le.', '.ge.']

def readTerm(ctx):
    token = current(ctx)
    if token and token.isnumeric():
        read(ctx)
        return True
    if currentIsCharacterConstant(ctx):
        if ctx['expressionType'] != 'logical':
            ctx['expressionType'] = 'character'
        read(ctx)
        return True
    if token == '(':
        return readToken(ctx, '(') and readExpression(ctx) and readToken(ctx, ')')
    if token == '.minus.':
        return readToken(ctx, token) and readTerm(ctx)
    if token == '.not.':
        valid = readToken(ctx, token) and readTerm(ctx)
        ctx['expressionType'] = 'logical'
        return valid
    identifier = read(ctx)
    identifierType = ctx['variables'].get(identifier)
    if identifierType == 'character' and ctx['expressionType'] != 'logical':
        ctx['expressionType'] = 'character'
    if identifierType == 'logical':
        ctx['expressionType'] = 'logical'
    return ctx['variables'].get(identifier) is not None

def currentIsCharacterConstant(ctx):
    token = current(ctx) or ''
    return len(token) == 3 and token[0] == token[2] == '"'

if __name__ == '__main__':
    main()
