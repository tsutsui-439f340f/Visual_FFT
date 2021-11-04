import threading
import queue
import matplotlib.pyplot as plt
import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import pyaudio
import sys

class Record():
    def __init__(self,q):
        self.RATE=44100
        self.CHUNK=2024
        self.FORMAT = pyaudio.paInt16
        self.p=pyaudio.PyAudio()
        self.q=q
        self.stream=self.p.open(format =self.FORMAT,
                channels = 1,
                rate = self.RATE,
                frames_per_buffer = self.CHUNK,
                input = True,
                output = True)
        
    def run(self):
        try:
            while self.stream.is_active():
                data = self.stream.read(self.CHUNK)
                self.q.put(data)
                #print(self.q.qsize())
                #output = self.stream.write(data)
                
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except SystemExit:
            print("SystemExit")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
    
class GUI():
    def __init__(self,q):
        self.root = tkinter.Tk()
        self.root.wm_title("Sound Wave")
        self.fig ,self.ax= plt.subplots(figsize=(16,8)) 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.fig.patch.set_alpha(0.5)
        self.ax.patch.set_facecolor('black')
        self.ax.set_ylim([0, 300])
        self.ax.set_xlabel("Hz")
        #self.ax.set_xticks([])
	
        self.q=q
        
	#self.step=21
        self.line, = self.ax.plot(np.linspace(0, 5000, 238),np.zeros(238),c="white")
    
    def run(self):
        l = np.arange(0, 80, 0.01)  
        ani = animation.FuncAnimation(self.fig, self.animate, l,
            init_func=self.init, interval=52, blit=True,
            )

      
        self.canvas.get_tk_widget().pack()

        button = tkinter.Button(master=self.root, text="Quit", command=self._quit)
        button.pack()
        tkinter.mainloop()
        

    def _quit(self):
        
        self.root.quit()     
        self.root.destroy()
        sys.exit()


    def init(self): 
        self.line.set_ydata(np.random.randn(238))
        return self.line,


    def animate(self,i):
        if self.q.qsize()>0:
            
            x=np.fromstring(self.q.get(), dtype=np.int16)
            h=np.hanning(2024)
            sp=np.abs(np.fft.fft(x*h)[:238])
            self.line.set_ydata(sp*0.001)

            if self.q.qsize()>3:
                self.q.get()
        
        return self.line,

      
class Threading(threading.Thread):

    def __init__(self,q,daemon):
        
        super(Threading,self).__init__()
        self.q=q
        self.daemon=daemon
    
    def run(self):
      
        r=Record(self.q)
        r.run()   
        
        
q = queue.Queue()

t1 = Threading(q,daemon=True)
t1.start()



gui=GUI(q)
gui.run()





