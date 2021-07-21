import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
from acquisition import Connection


class Animation:
    def __init__(self, nbr_scan):
        self.conn = Connection()
        self.conn.get_acquisition_temps_reel()
        self.start = time.time()
        self.nbr_scan = nbr_scan

    def data_gen(self):
        cnt = 0
        self.start = time.time()
        while cnt < self.nbr_scan:
            cnt += 1
            t = time.time() - self.start
            self.conn.inst.write("INIT;")
            self.conn.inst.write(":FETCH?;")
            y1, y2 = self.conn.inst.read().split(',')[:2]
            # adapted the data generator to yield both sin and cos
            yield t, float(y1), float(y2)

    @staticmethod
    def save(data):
        t, y1, y2 = data
        df = pd.DataFrame(
            {"time": t, "Temp @101": y1, "Temp @102": y2},
            columns=['time', "Temp @101", "Temp @102"]
        )
        print(df)
        return df

    def loop(self):
        fig, (ax1, ax2) = plt.subplots(2, 1)
        # intialize two line objects (one in each axes)
        line1, = ax1.plot([], [], lw=2)
        line2, = ax2.plot([], [], lw=2, color='r')
        line = [line1, line2]
        self.conn.inst.write("INIT;")
        self.conn.inst.write(":FETCH?;")
        # Read temperature (Celsius) from TMP102
        y1_start, y2_start = list(map(lambda x: float(x), self.conn.inst.read().split(',')[:2]))
        ax1.set_ylim(y1_start - 1, y1_start + 1)
        ax1.set_xlim(0, 10)
        ax1.grid()
        ax2.set_ylim(y2_start - 1, y2_start + 1)
        ax2.set_xlim(0, 10)
        ax2.grid()
        ax1.set_title('Channel 101')
        ax2.set_title('Channel 102')
        ax1.set_xlabel('time (seconds)')
        ax2.set_xlabel('time (seconds)')
        ax1.set_ylabel('Temperature (°C)')
        ax2.set_ylabel('Temperature (°C)')
        # initialize the data arrays
        xdata, y1data, y2data = [], [], []

        def run(data):
            # update the data
            t, y1, y2 = data
            xdata.append(t)
            y1data.append(y1)
            y2data.append(y2)

            # axis limits checking. Same as before, just for both axes
            for ax in [ax1, ax2]:
                xmin, xmax = ax.get_xlim()
                if t >= xmax:
                    ax.set_xlim(xmin, 2 * xmax)
                    ax.figure.canvas.draw()
            ymin, ymax = ax1.get_ylim()
            if y1 >= ymax or y1<=ymin:
                ax1.set_ylim(min(y1data)-2,max(y1data)+2)
                ax1.figure.canvas.draw()
            ymin, ymax = ax2.get_ylim()
            if y2 >= ymax or y2<=ymin:
                ax2.set_ylim(min(y2data)-2,max(y2data)+2)
                ax2.figure.canvas.draw()

            # update the data of both line objects
            line[0].set_data(xdata, y1data)
            line[1].set_data(xdata, y2data)

            return line

        ani = animation.FuncAnimation(fig, run, self.data_gen, blit=False, interval=1000, repeat=False)
        plt.tight_layout()
        plt.show()
        df = Animation.save(data=(xdata, y1data, y2data))
        df.to_excel(f'acquisition.xlsx',sheet_name="acquisition")
