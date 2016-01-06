import os
os.environ['CLASSPATH'] = 'st76a9.jar'

from jnius import autoclass

Runtime = autoclass('st76.runtime.Runtime')
HostSystemBuilder = autoclass('st76.simulator.host.HostSystemBuilder')
UniqueString = autoclass('st76.runtime.UniqueString')
Obj = autoclass('st76.runtime.Obj')
Exec = autoclass('st76.tools.Exec')
SourcecodeRef = autoclass('st76.io.SourcecodeRef')
Simulator = autoclass('st76.simulator.Simulator')

def simulator_evaluateAll(fileRef):
    ci = fileRef.chunks()
    while ci.hasMoreChunks():
        chunk = ci.nextChunk()
        Simulator.evaluate(chunk)

def exec_main():
    Runtime.initialize()
    HostSystemBuilder.defineClasses()
    HostSystemBuilder.defineBootSupport()
    Runtime.Smalltalk.defineAs(UniqueString._for("HasGUI"), Obj.FALSE)
    ref = SourcecodeRef.create('jar:/source/bootstrap.utf.txt', Exec)
    Simulator_evaluateAll(ref)

if __name__ == '__main__':
    exec_main()
