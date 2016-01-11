import os
os.environ['CLASSPATH'] = 'st76a9.jar'

from jnius import autoclass
from jnius import JavaException

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
Context = autoclass('st76.simulator.Context')

class Simulator:
    def __init__(self, context):
        self.active_context = context

    def run(self):
        active_context = self.active_context
        try:
            while True:
                active_context = active_context.step()
        except JavaException, e:
            if e.classname == 'st76.simulator.ReturnValue':
                return e.exception.value()
            raise e

def simulator_evaluate(expression):
     altoSource = Transcoder.toAlto("doIt [^[" + expression + "]]")
     objectCls = Runtime.Smalltalk._ref(UniqueString._for("Object"))
     method_tuple = Compiler().compileIn(ByteString(altoSource), objectCls)
     method = method_tuple._ref(Integer(2))
     return Simulator(Context().set(None, Obj.NIL, objectCls, method)).run()

def simulator_evaluateAll(fileRef):
    ci = fileRef.chunks()
    while ci.hasMoreChunks():
        chunk = ci.nextChunk()
        simulator_evaluate(chunk)

def exec_main():
    Runtime.initialize()
    HostSystemBuilder.defineClasses()
    HostSystemBuilder.defineBootSupport()
    Runtime.Smalltalk.defineAs(UniqueString._for("HasGUI"), Obj.FALSE)
    ref = SourcecodeRef.create('jar:/source/bootstrap.utf.txt', Exec)
    simulator_evaluateAll(ref)
    print simulator_evaluate('3 + 4')

if __name__ == '__main__':
    exec_main()
