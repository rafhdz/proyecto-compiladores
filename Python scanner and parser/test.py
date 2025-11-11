import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser

def main():
    data = FileStream(sys.argv[1], encoding='utf-8')
    lexer = PatitoLexer(data)
    stream = CommonTokenStream(lexer)
    parser = PatitoParser(stream)
    tree = parser.program()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()