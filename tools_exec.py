from __future__ import print_function

import json
import os
os.environ['CLASSPATH'] = 'st76a9.jar'
from jnius import autoclass
from jnius import JavaException
# from binascii import b2a_hex


Runtime = autoclass('st76.runtime.Runtime')
HostSystemBuilder = autoclass('st76.simulator.host.HostSystemBuilder')
UniqueString = autoclass('st76.runtime.UniqueString')
Obj = autoclass('st76.runtime.Obj')
Exec = autoclass('st76.tools.Exec')
SourcecodeRef = autoclass('st76.io.SourcecodeRef')
Transcoder = autoclass('st76.io.Transcoder')
Compiler = autoclass('st76.compiler.Compiler')
ByteString = autoclass('st76.runtime.ByteString')
Int = autoclass('st76.runtime.Int')
Integer = autoclass('java.lang.Integer')
JContext = autoclass('st76.simulator.Context')
Disassembler = autoclass('st76.tools.Disassembler')


class Simulator:
    def __init__(self, context):
        self.active_context = context

    def run(self):
        active_context = self.active_context
        try:
            # while True:
            for i in range(1000):
                active_context = active_context.step()
        except JavaException as e:
            if e.classname == 'st76.simulator.ReturnValue':
                return e.innermessage
            print("p1", e.classname)
            print("p2", e.innermessage)
            print("p3", e.stacktrace)
            raise e
        except ReturnValue as e:
            return e.value


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Context:

    # plus_symbol = UniqueString._for("HasGUI")
    # SpecialSelectors = [plus_symbol]
    # except JavaException, e:
    #     print "p1", e.classname
    #     print "p2", e.innermessage
    #     print "p3", e.stacktrace
    #     raise e

    def __init__(self, sender, receiver, mclass, method):
        # print Disassembler(method).disassemble()
        self.sender = sender
        self.receiver = receiver
        self.mclass = mclass
        self.method = method
        self.temp_frame = [None] * method.tempFrameSize()
        self.pc = method.startPC() - 1
        self.sp = method.startSP() - 1
        plus_symbol = UniqueString._for("+")
        minus_symbol = UniqueString._for("-")
        lt_symbol = UniqueString._for("<")
        self.special_selectors = [plus_symbol, minus_symbol, lt_symbol]
        self.constants = [None] * 16
        self.constants[0] = -1
        self.constants[1] = 0
        self.constants[2] = 1
        self.constants[3] = 2
        self.constants[4] = 10
        self.constants[5] = Obj.NIL
        self.constants[6] = Obj.FALSE
        self.constants[7] = Obj.TRUE

    def next_byte(self):
        self.pc += 1
        return self.method.code(self.pc)

    def step(self):
        byte_code = self.next_byte()
        # print "ip={:2} bc={}".format(self.pc, hex(byte_code)),
        #       self.temp_frame[:self.sp+1]
        lobits = byte_code & 0xF
        hibits = byte_code >> 4
        if hibits == 2:
            self.push(self.method.literal(lobits))
        elif hibits == 7:
            if (lobits == 1):
                self.push(self.receiver)
            else:
                self.push(self.constants[(lobits - 8)])
        elif hibits == 8:
            if lobits == 3:
                if self.sender is None:
                    # print "ReturnValue"
                    raise ReturnValue(self.top())
                self.sender.push(self.top())
                return self.sender
            else:
                self.bad_code(byte_code)
        elif hibits == 9:
            if lobits <= 7 or self.pop() is False:
                self.pc += (lobits & 0x7) + 1
        elif hibits == 0xB:
            return self.send(self.special_selectors[lobits])
        elif hibits == 0xD:
            return self.send(self.method.literal(lobits))
        else:
            self.bad_code(byte_code)
        return self

    def bad_code(self, byte_code):
        raise Exception("unknown bytecode: " + hex(byte_code))

    def push(self, value):
        self.sp += 1
        self.temp_frame[(self.sp)] = value

    def top(self):
        return self.temp_frame[self.sp]

    def pop(self):
        result = self.temp_frame[self.sp]
        self.sp -= 1
        return result

    def send(self, selector):
        # print "selector.toString()", selector.toString()
        # top = self.top()
        # print "self.top()", top
        # print "type(self.top())", type(self.top())
        top_class = Obj.cls(Integer(3))
        # print "top_class.toString()", top_class.toString()
        search_class = top_class
        method = search_class._lookup(selector)
        while search_class is None:
            search_class = search_class._superclass()
            method = search_class._lookup(selector)
        if method is None:
            raise Exception(top_class.toString() + " does not understand " +
                            selector.toString())
        # print "method", method.toString()
        # check if it's a primitive
        if method.hasPrimitive():
            result = self.call_primitive(method)
            if result is not None:
                # print "return result"
                return result
        # it's not a primitive
        callee = Context(self, self.pop(), top_class, method)
        p = method.numArgs() - 1
        # target_frame = callee.temp_frame
        while (p >= 0):
            # targetFrame[(p)] = pop()
            p -= 1
        # print "method", method.toString()
        # print "return callee"
        return callee

    def pop2push(self, result):
        self.sp -= 1
        self.temp_frame[self.sp] = result

    def call_primitive(self, method):
        primitive = method.primitive()
        # print "primitive", primitive
        if primitive == 6:
            result = self.temp_frame[self.sp] + self.temp_frame[self.sp-1]
            self.pop2push(result)
            return self
        elif primitive == 7:
            result = self.temp_frame[self.sp] - self.temp_frame[self.sp-1]
            self.pop2push(result)
            return self
        elif primitive == 8:
            result = self.temp_frame[self.sp] < self.temp_frame[self.sp-1]
            self.pop2push(result)
            return self
        raise Exception("primitive implementation not finished")

class EscapeAll(bytes):
    def __str__(self):
        return 'b\'{}\''.format(''.join('\\x{:02x}'.format(b) for b in self))

def simulator_evaluate(expression):
    altoSource = Transcoder.toAlto("doIt [^[" + expression + "]]")
    objectCls = Runtime.Smalltalk._ref(UniqueString._for("Object"))
    method_tuple = Compiler().compileIn(ByteString(altoSource), objectCls)
    method = method_tuple._ref(Integer(2))
    # print [each for each in method.codes().fBytes]
    result = Simulator(Context(None, None, objectCls, method)).run()
    print(expression, "=>", result)

def simulator_jevaluate(source, evaluation_list):
    evaluation_dictionary = {}
    evaluation_list.append(evaluation_dictionary)
    evaluation_dictionary['source'] = source
    altoSource = Transcoder.toAlto("doIt [^[" + source + "]]")
    evaluation_dictionary['alto_source'] = altoSource
    evaluation_dictionary['lexem'] = ByteString(altoSource).asVector().toString()
    evaluation_dictionary['lexem'] = ([each if isinstance(each, int)else each.toString() for each in ByteString(altoSource).asVector().elements()])
    objectCls = Runtime.Smalltalk._ref(UniqueString._for("Object"))
    method_tuple = Compiler().compileIn(ByteString(altoSource), objectCls)
    evaluation_dictionary['selector'] = method_tuple._ref(Integer(1)).toString()
    evaluation_dictionary['codes '] = str(EscapeAll(bytes(method_tuple._ref(Integer(2)).codes().fBytes)))
    method = method_tuple._ref(Integer(2))
    return Simulator(JContext().set(None, Obj.NIL, objectCls, method)).run()

def simulator_evaluateAll(fileRef, evaluation_list=[]):
    ci = fileRef.chunks()
    while ci.hasMoreChunks():
        chunk = ci.nextChunk()
        simulator_jevaluate(chunk, evaluation_list)

def exec_main():
    Runtime.initialize()
    HostSystemBuilder.defineClasses()
    HostSystemBuilder.defineBootSupport()
    Runtime.Smalltalk.defineAs(UniqueString._for("HasGUI"), Obj.FALSE)
    ref = SourcecodeRef.create('jar:/source/bootstrap.utf.txt', Exec)
    evaluation_list = []
    simulator_evaluateAll(ref, evaluation_list)
    with open('evaluation.json', 'w') as json_file:
        json.dump(evaluation_list, json_file, indent=4)
    ref = SourcecodeRef.create('jar:/source/bench.utf.txt', Exec)
    simulator_evaluateAll(ref)
    simulator_evaluate('3 + 4')
    simulator_evaluate('3 - 4')
    simulator_evaluate('1 benchFib')
    simulator_evaluate('5 benchFib')

if __name__ == '__main__':
    exec_main()
