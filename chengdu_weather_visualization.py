import requests
from tkinter import *
from tkinter import messagebox
import sqlite3
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import dates
# %matplotlib notebook
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import numpy.ma as ma


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master=master)
        self.pack()
        self.past_temps = []
        self.future_temps = []

        self.fig1 = plt.figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.axis((0, 100, 0, 60))
        self.canvas = FigureCanvasTkAgg(self.fig1, master)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=CENTER)
        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.line1, = self.ax1.plot([], [], color='orange', marker='o')
        self.line2, = self.ax1.plot([], [], color='lightblue', marker='o')
        self.create_window()

    def create_window(self):
        def plot():
            r = requests.get('http://www.nmc.cn/rest/weather?stationid=56294')
            self.past_temps = r.json()['data']['tempchart']
            self.future_temps = r.json()['data']['predict']['detail']
            x = [dt.strptime(temp['time'], '%Y/%m/%d').date() for temp in self.past_temps]
            y1 = np.array([temp['max_temp'] for temp in self.past_temps])
            mc = ma.array(y1)
            mask_pos = np.where(y1 == 9999.0)
            mc[mask_pos] = ma.masked
            y1 = mc
            y2 = [temp['min_temp'] for temp in self.past_temps]

            self.line1.set_xdata(x)
            self.line1.set_ydata(y1)
            self.line2.set_xdata(x)
            self.line2.set_ydata(y2)

            for (xn, yn1, yn2) in zip(x, y1, y2):
                self.ax1.annotate('%.1f' % yn1, (xn, yn1), xycoords='data', textcoords="offset points", xytext=(0, 10), ha='center')
                self.ax1.annotate('%.1f' % yn2, (xn, yn2), xycoords='data', textcoords="offset points", xytext=(0, 10), ha='center')
            self.ax1.grid()
            formats = dates.DateFormatter("%Y-%m-%d")
            self.ax1.xaxis.set_major_formatter(formats)

            self.ax1.set_ylim([0, 50])
            self.ax1.set_xlabel('Date')
            self.ax1.set_ylabel('Temperature (\N{DEGREE SIGN}C)')
            labels = self.ax1.get_xticklabels()
            plt.setp(labels, rotation=45, fontsize=10)
            plt.legend(['Max temp', 'Min temp'])

            self.canvas.draw()
            self.toolbar.update()

        def clear():
            self.past_temps = []
            self.future_temps = []
            self.line1.set_xdata([])
            self.line1.set_ydata([])
            self.line2.set_xdata([])
            self.line2.set_ydata([])

        def save():
            conn = sqlite3.connect('chengdu_temp.db')
            cur = conn.cursor()
            try:
                cur.execute('''CREATE TABLE pastDaysTemp (date text, maxtemp real, mintemp real)''')
                cur.execute('''CREATE TABLE futureDaysTemp (date text, temp real, weather text)''')
            except:
                pass
            for temp in self.past_temps:
                cur.execute("INSERT INTO pastDaysTemp VALUES ('%s', '%s', '%s')"
                            % (temp['time'], temp['max_temp'], temp['min_temp']))

            for temp in self.future_temps:
                cur.execute("INSERT INTO futureDaysTemp VALUES ('%s', '%s', '%s')"
                            % (temp['date'], temp['day']['weather']['temperature'], temp['day']['weather']['info']))

            conn.commit()
            conn.close()
            messagebox.showinfo(title='提示', message='保存成功！')

        plot_button = Button(master=root,
                             command=plot,
                             height=1,
                             width=10,
                             text="绘制天气曲线", )
        plot_button.place(x=800 / 3, y=10)
        clear_button = Button(master=root,
                              command=clear,
                              height=1,
                              width=10,
                              text="清除", )
        clear_button.place(x=800 / 3 + 100, y=10)
        save_button = Button(master=root,
                             command=save,
                             height=1,
                             width=10,
                             text="保存数据", )
        save_button.place(x=800 / 3 + 200, y=10)


root = Tk()
root.title('成都天气查询')
root.geometry("800x650")
root.deiconify()
root.resizable(0, 0)
app = Window(root)
app.mainloop()
