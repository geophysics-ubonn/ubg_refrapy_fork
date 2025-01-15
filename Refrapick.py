#!/usr/bin/env python

# #Refrapy - Seismic Refraction Data Analysis
# #Refrapick - First-break picking
# #Author: Victor Guedes, MSc
# #E-mail: vjs279@hotmail.com
import warnings
from os import path, makedirs, getcwd

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.colors import is_color_like
from matplotlib import lines, markers
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from tkinter import Tk, Toplevel, Frame, Button, Label, filedialog
from tkinter import messagebox, PhotoImage, simpledialog, Entry
from obspy import read
from obspy.signal.filter import lowpass, highpass
from scipy.signal import resample
from scipy.interpolate import interp1d
from numpy import array, where, polyfit, isclose, unique
from Pmw import initialise, Balloon
from tqdm import tqdm

warnings.filterwarnings('ignore')

class Refrapick(Tk):

    def __init__(self):

        super().__init__()
        self.geometry("1600x900")
        self.title('Refrapy - Refrapick v2.1.0 - SP fork')
        self.configure(bg = "#F0F0F0")
        # self.resizable(0,0)

        frame_toolbar = Frame(self)
        frame_toolbar.grid(row=0,column=0,sticky="WE")

        # self.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())
        photo = PhotoImage(file="%s/images/ico_refrapy.gif"%getcwd())
        labelPhoto = Label(frame_toolbar, image = photo, width = 151)
        labelPhoto.image = photo
        labelPhoto.grid(row=0, column =0, sticky="W")
        self.statusLabel = Label(frame_toolbar, text = "Create or load a project to start", font=("Arial", 11))
        self.statusLabel.grid(row = 0, column = 34, sticky = "W")
        initialise(self)
        self.ico_openWaveform = PhotoImage(file="%s/images/abrir.gif"%getcwd())
        self.ico_savePicks = PhotoImage(file="%s/images/salvar.gif"%getcwd())
        self.ico_nextWf = PhotoImage(file="%s/images/proximo.gif"%getcwd())
        self.ico_previousWf = PhotoImage(file="%s/images/voltar.gif"%getcwd())
        self.ico_expandY = PhotoImage(file="%s/images/baixo.gif"%getcwd())
        self.ico_zoomY = PhotoImage(file="%s/images/cima.gif"%getcwd())
        self.ico_moreGain = PhotoImage(file="%s/images/mais.gif"%getcwd())
        self.ico_lessGain = PhotoImage(file="%s/images/menos.gif"%getcwd())
        self.ico_invertY = PhotoImage(file="%s/images/invert.gif"%getcwd())
        self.ico_trim = PhotoImage(file="%s/images/cortar.gif"%getcwd())
        self.ico_wiggles = PhotoImage(file="%s/images/fill_null.gif"%getcwd())
        self.ico_fillNeg = PhotoImage(file="%s/images/fill_neg.gif"%getcwd())
        self.ico_fillPos = PhotoImage(file="%s/images/fill_pos.gif"%getcwd())
        self.ico_clip = PhotoImage(file="%s/images/clip.gif"%getcwd())
        self.ico_filters = PhotoImage(file="%s/images/ico_filter.gif"%getcwd())
        self.ico_pick = PhotoImage(file="%s/images/pick.gif"%getcwd())
        self.ico_connectPick = PhotoImage(file="%s/images/ligar.gif"%getcwd())
        self.ico_clearPicks = PhotoImage(file="%s/images/limpar.gif"%getcwd())
        self.ico_velMode = PhotoImage(file="%s/images/vel.gif"%getcwd())
        self.ico_tt = PhotoImage(file="%s/images/grafico.gif"%getcwd())
        self.ico_options = PhotoImage(file="%s/images/opt.gif"%getcwd())
        self.ico_reset = PhotoImage(file="%s/images/fechar.gif"%getcwd())
        self.ico_newProject = PhotoImage(file="%s/images/ico_newProject.gif"%getcwd())
        self.ico_loadProject = PhotoImage(file="%s/images/ico_loadProject.gif"%getcwd())
        self.ico_resample = PhotoImage(file="%s/images/ico_resample.gif"%getcwd())
        self.ico_survey = PhotoImage(file="%s/images/ico_survey.gif"%getcwd())
        self.ico_shotTime = PhotoImage(file="%s/images/ico_shotTime.gif"%getcwd())
        self.ico_loadPicks = PhotoImage(file="%s/images/ico_loadPicks.gif"%getcwd())
        self.ico_allPicks = PhotoImage(file="%s/images/ico_allPicks.gif"%getcwd())
        self.ico_restoreTraces = PhotoImage(file="%s/images/ico_restoreTraces.gif"%getcwd())
        self.ico_help = PhotoImage(file="%s/images/ico_help.gif"%getcwd())
        self.ico_plotOptions = PhotoImage(file="%s/images/ico_plotOptions.gif"%getcwd())
        self.ico_errorOptions = PhotoImage(file="%s/images/ico_error.png"%getcwd())

        bt = Button(frame_toolbar,image = self.ico_newProject,command = self.createProject,width=25)
        bt.grid(row = 0, column = 1, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Create new project path")

        bt = Button(frame_toolbar,image = self.ico_loadProject,command = self.loadProject,width=25)
        bt.grid(row = 0, column = 2, sticky="W")
        b = Balloon(self)
        b.bind(bt,"Load project path")

        bt = Button(frame_toolbar, image = self.ico_openWaveform,command = self.openWaveform)
        bt.grid(row = 0, column = 3, sticky="W")
        b = Balloon(self)
        b.bind(bt,"Open waveform file(s)")

        bt = Button(frame_toolbar, image = self.ico_previousWf,command = self.previousSection,width=25)
        bt.grid(row = 0, column = 4, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Previous file")

        bt = Button(frame_toolbar,image = self.ico_nextWf, command = self.nextSection,width=25)
        bt.grid(row = 0, column = 5, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Next file")

        bt = Button(frame_toolbar,image = self.ico_expandY ,command = self.yLimUp,width=25)
        bt.grid(row = 0, column = 6, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Decrease time axis limit")

        bt = Button(frame_toolbar,image = self.ico_zoomY,command = self.yLimDown,width=25)
        bt.grid(row = 0, column = 7, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Increase time axis limit")

        bt = Button(frame_toolbar,image = self.ico_moreGain,command = self.addGain,width=25)
        bt.grid(row = 0, column = 8, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Increase scale gain")

        bt = Button(frame_toolbar,image = self.ico_lessGain ,command = self.removeGain,width=25)
        bt.grid(row = 0, column = 9, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Decrease scale gain")

        bt = Button(frame_toolbar,image=self.ico_fillNeg,command = self.fillPositive,width=25)
        bt.grid(row = 0, column = 10, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Fill positive side of amplitudes")

        bt = Button(frame_toolbar,image=self.ico_fillPos,command = self.fillNegative,width=25)
        bt.grid(row = 0, column = 11, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Fill negative side of amplitudes")

        bt = Button(frame_toolbar,image=self.ico_wiggles,command = self.wigglesOnly,width=25)
        bt.grid(row = 0, column = 12, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"No filling (wiggles only)")

        bt = Button(frame_toolbar,image=self.ico_clip,command = self.clipAmplitudes,width=25)
        bt.grid(row = 0, column = 13, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Clip/unclip amplitudes")

        bt = Button(frame_toolbar,image=self.ico_shotTime,command = self.correctShotTime,width=25)
        bt.grid(row = 0, column = 14, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Correct shot time (delay)")

        bt = Button(frame_toolbar,image=self.ico_filters,command = self.applyFilters,width=25)
        bt.grid(row = 0, column = 15, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"High pass/low pass filters")

        bt = Button(frame_toolbar,image=self.ico_trim,command = self.trimTraces,width=25)
        bt.grid(row = 0, column = 16, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Trim traces")

        bt = Button(frame_toolbar,image=self.ico_resample,command = self.resampleTraces,width=25)
        bt.grid(row = 0, column = 17, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Resample traces")

        bt = Button(frame_toolbar,image=self.ico_invertY,command = self.invertTimeAxis,width=25)
        bt.grid(row = 0, column = 18, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Invert time axis")

        bt = Button(frame_toolbar,image=self.ico_restoreTraces,command = self.restoreTraces,width=25)
        bt.grid(row = 0, column = 19, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Restore default traces")

        bt = Button(frame_toolbar,image=self.ico_pick,command = self.pick,width=25)
        bt.grid(row = 0, column = 20, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Enable/disable pick mode")

        bt = Button(frame_toolbar,image=self.ico_errorOptions,command = self.setError,width=25)
        bt.grid(row = 0, column = 21, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Set error parameters")

        bt = Button(frame_toolbar,image=self.ico_connectPick,command = self.drawPicksLine,width=25)
        bt.grid(row = 0, column = 22, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Connect/disconnect picks")

        bt = Button(frame_toolbar,image=self.ico_clearPicks,command = self.clearPicks,width=25)
        bt.grid(row = 0, column = 23, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Clear picks")

        bt = Button(frame_toolbar,image=self.ico_allPicks,command = self.allPicks,width=25)
        bt.grid(row = 0, column = 24, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Show/hide traveltimes picks from other files")

        bt = Button(frame_toolbar,image = self.ico_savePicks, command = self.savePicks,width=25)
        bt.grid(row = 0, column = 25, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Save pick file")

        bt = Button(frame_toolbar,image=self.ico_loadPicks,command = self.loadPicks,width=25)
        bt.grid(row = 0, column = 26, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Load pick file)")

        bt = Button(frame_toolbar,image=self.ico_velMode,command = self.appVelMode,width=25)
        bt.grid(row = 0, column = 27, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Enable/disable apparent velocity mode")

        bt = Button(frame_toolbar,image = self.ico_tt,command = self.viewTraveltimes,width=25)
        bt.grid(row = 0, column = 28, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"View observed traveltimes")

        bt = Button(frame_toolbar,image=self.ico_survey,command = self.viewSurvey,width=25)
        bt.grid(row = 0, column = 29, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"View survey geometry")

        bt = Button(frame_toolbar,image = self.ico_plotOptions,command = self.plotOptions,width=25)
        bt.grid(row = 0, column = 30, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Plot options")

        bt = Button(frame_toolbar,image = self.ico_options,command = self.options,width=25)
        bt.grid(row = 0, column = 31, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Edit acquisition parameters")

        bt = Button(frame_toolbar,image = self.ico_reset,command = self.reset,width=25)
        bt.grid(row = 0, column = 32, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Reset all")

        bt = Button(frame_toolbar,image=self.ico_help,command = self.help,width=25)
        bt.grid(row = 0, column = 33, sticky="W")
        bl = Balloon(self)
        bl.bind(bt,"Help")

        self.protocol("WM_DELETE_WINDOW", self.kill)
        self.initiateVariables()

    def initiateVariables(self):

        self.frames = []
        self.figs = []
        self.axs = []
        self.axins = []
        self.sts = []
        self.xpicks = []
        self.tpicks = []
        self.errpicks = []
        self.sources = []
        self.dxs = []
        self.x1s = []
        self.xends = []
        self.xalls = []
        self.delay = 0
        self.tracesArts = []
        self.tracesArtsIn = []
        self.fillArts = []
        self.fillArtsIn = []
        self.gain = 1
        self.gains = []
        self.gainFactor = 2
        self.tracesMaxs = []
        self.tracesData = []
        self.nchannels = []
        self.tracesTime = []
        self.errors = [0.1, True, 0.5e-3, 5e-3]
        self.currentSt = 0
        self.fillSide = 1
        self.amplitudeClip = 0
        self.invertedTimeAxis = []
        self.samplingRates = []
        self.originalSamplingRates = []
        self.stNames = []
        self.originalTracesData = []
        self.originalTracesTimes = []
        self.filters = []
        self.receiverPositions = []
        self.picksArts = []
        self.picksArtsIn = []
        self.ttArts = []
        self.projReady = False
        self.pickMode = False
        self.velMode = False
        self.pickConnections = []
        self.velConnections = []
        self.pickLineArts = []
        self.maxTime = []
        self.traceColor = "k"
        self.fillColor = "k"
        self.backgroundColor = "white"
        self.grid = 1
        self.gridColor = "k"
        self.gridStyle = "-"
        self.pickColor = "r"
        self.pickMarker = "+"
        self.pickLineColor = "r"
        self.pickLineStyle = "--"
        self.traveltimesColor = "g"
        self.traveltimesStyle = "--"
        self.pickSize = 100

    def kill(self):

        out = messagebox.askyesno("Refrapick", "Do you want to close the software?")

        if out: self.destroy(); self.quit()

    def nextSection(self):

        if self.sts:

            if self.currentSt < len(self.sts)-1:

                self.currentSt += 1

                if len(self.ttArts) > 0:

                    self.allPicks()
                    self.figs[self.currentSt].canvas.draw_idle()
                    self.allPicks()

                self.yLimSet()
                self.setGain()


        self.frames[self.currentSt].tkraise()
        self.statusLabel.lift()

    def previousSection(self):

        if self.sts:

            if self.currentSt > 0:

                self.currentSt -= 1

                if len(self.ttArts) > 0:

                    self.allPicks()
                    self.figs[self.currentSt].canvas.draw_idle()
                    self.allPicks()

                self.yLimSet()
                self.setGain()

        self.frames[self.currentSt].tkraise()
        self.statusLabel.lift()

    def reset(self):

        if self.sts:

            if messagebox.askyesno("Refrapick", "Clear all?"):

                for frame in self.frames: frame.destroy()
                self.initiateVariables()
                self.statusLabel.configure(text="Create or load a project to start",font=("Arial", 11))
                messagebox.showinfo(title="Refrapick", message="All cleared successfully!")

    def plotOptions(self):

        def editMaxTime():

            new_max_time = simpledialog.askstring("Refrapick","Enter the new maximum time (in s):")

            if new_max_time:

                self.maxTime = float(new_max_time)

                self.yLimSet()

                # messagebox.showinfo(title="Refrapick", message="The maximum time has been changed")
                print("Refrapick: The maximum time has been changed")
                plotOptionsWindow.tkraise()

        def editTraceColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new trace color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.traceColor = new_color

                if self.sts:

                    for i in range(len(self.sts)):

                        for trArt in self.tracesArts[i]:

                            trArt.set_color(self.traceColor)

                        self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The trace color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editFillColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new fill color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.fillColor = new_color

                if self.sts:

                    for i in range(len(self.sts)):

                        if self.fillSide == 1: self.wigglesOnly(); self.fillPositive()
                        elif self.fillSide == -1: self.wigglesOnly(); self.fillNegative()

                messagebox.showinfo(title="Refrapick", message="The fill color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editBackgroundColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new background color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.backgroundColor = new_color

                if self.sts:

                    for i in range(len(self.sts)):

                        self.axs[i].set_facecolor(self.backgroundColor)
                        self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The plot background color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def gridOnOff():

            if self.grid:

                if messagebox.askyesno("Refrapick", "Disable grid?"):

                    self.grid = False

                    if self.sts:

                        for i in range(len(self.sts)):

                            self.axs[i].grid(False)
                            self.figs[i].canvas.draw_idle()

                        messagebox.showinfo(title="Refrapick", message="The grid lines have been disabled")

            else:

                if messagebox.askyesno("Refrapick", "Enable grid?"):

                    self.grid = True

                    if self.sts:

                        for i in range(len(self.sts)):

                            self.axs[i].grid(lw = .5, alpha = .5, c = self.gridColor, ls = self.gridStyle)
                            self.figs[i].canvas.draw_idle()

                        messagebox.showinfo(title="Refrapick", message="The grid lines have been enabled")

            plotOptionsWindow.tkraise()

        def editGridStyle():

            new_style = simpledialog.askstring("Refrapick","Enter the new grid line style (must be accepted by matplotlib):")

            if new_style in lines.lineStyles.keys():

                self.gridStyle = new_style

                if self.sts:

                    if self.grid:

                        for i in range(len(self.sts)):

                            self.axs[i].grid(lw = .5, alpha = .5, c = self.gridColor, ls = self.gridStyle)
                            self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The grid line style has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid line style!"); plotOptionsWindow.tkraise()

        def editGridColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new grid line color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.gridColor = new_color

                if self.sts:

                    if self.grid:

                        for i in range(len(self.sts)):

                            self.axs[i].grid(lw = .5, alpha = .5, c = self.gridColor, ls = self.gridStyle)
                            self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The grid line color color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editPickColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new pick marker color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.pickColor = new_color

                if self.sts:

                    for i in range(len(self.sts)):

                        if self.xpicks[i]:

                            for pickArt in self.picksArts[i]: pickArt.set_color(self.pickColor)
                            for pickArtIn in self.picksArtsIn[i]: pickArtIn.set_color(self.pickColor)

                        self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The pick marker color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editPickMarker():

            new_marker = simpledialog.askstring("Refrapick","Enter the new pick marker style (must be accepted by matplotlib):")

            if new_marker in markers.MarkerStyle.markers.keys():

                new_size = simpledialog.askfloat("Refrapick","Enter the new pick marker size:")

                if new_size:

                    self.pickSize = new_size
                    self.pickMarker = new_marker#markers.MarkerStyle(new_marker)

                    if self.sts:

                        for i in range(len(self.sts)):

                            if self.xpicks[i]:

                                for pickArt in self.picksArts[i]: pickArt.remove()
                                del self.picksArts[i][:]

                                for pickArtIn in self.picksArtsIn[i]: pickArtIn.remove()
                                del self.picksArtsIn[i][:]

                                for j,x in enumerate(self.xpicks[i]):

                                    pickline = self.axs[i].scatter(x, self.tpicks[i][j], marker = self.pickMarker, s = self.pickSize*self.dxs[i], color=self.pickColor)
                                    pickline_inset = self.axins[i].scatter(x, self.tpicks[i][j], marker = self.pickMarker, s = self.pickSize*self.dxs[i], color=self.pickColor)
                                    self.picksArts[i].append(pickline)
                                    self.picksArtsIn[i].append(pickline_inset)

                                self.figs[i].canvas.draw_idle()

                    messagebox.showinfo(title="Refrapick", message="The pick marker style has been changed")
                    plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid marker!"); plotOptionsWindow.tkraise()

        def editPickLineColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new pick line color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.pickLineColor = new_color

                if self.sts:

                    for i in range(len(self.sts)):

                        if self.pickLineArts[i]:

                            self.pickLineArts[i].set_color(self.pickLineColor)
                            self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The pick line color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editPickLineStyle():

            new_style = simpledialog.askstring("Refrapick","Enter the new pick line style (must be accepted by matplotlib):")

            if new_style in lines.lineStyles.keys():

                self.pickLineStyle = new_style

                if self.sts:

                    for i in range(len(self.sts)):

                        if self.pickLineArts[i]:

                            self.drawPicksLine()
                            self.pickLineArts[i] = False
                            self.drawPicksLine()
                            self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The pick line style has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid line style!"); plotOptionsWindow.tkraise()

        def editTraveltimeLineColor():

            new_color = simpledialog.askstring("Refrapick","Enter the new traveltimes line color (must be accepted by matplotlib):")

            if is_color_like(new_color):

                self.traveltimesColor = new_color

                if self.sts:

                    for i in range(len(self.sts)-1):

                        if self.ttArts[i]:

                            self.ttArts[i].set_color(self.traveltimesColor)
                            self.figs[i].canvas.draw_idle()

                messagebox.showinfo(title="Refrapick", message="The traveltimes line color has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid color!"); plotOptionsWindow.tkraise()

        def editTraveltimeLineStyle():

            new_style = simpledialog.askstring("Refrapick","Enter the new traveltimes line style (must be accepted by matplotlib):")

            if new_style in lines.lineStyles.keys():

                self.traveltimesStyle = new_style

                if self.sts:

                    for i in range(len(self.sts)-1):

                        if self.ttArts[i]:

                            self.allPicks()
                            self.figs[i].canvas.draw_idle()
                            self.allPicks()

                messagebox.showinfo(title="Refrapick", message="The traveltimes line style has been changed")
                plotOptionsWindow.tkraise()

            else: messagebox.showerror(title="Refrapick", message="Invalid line style!"); plotOptionsWindow.tkraise()

        def editGainFactor():

            new_gainFactor = simpledialog.askfloat("Refrapick","Enter the new gain factor (default is 2):")

            if new_gainFactor:

                self.gainFactor = new_gainFactor
                messagebox.showinfo(title="Refrapick", message="The gain factor has been changed")

        plotOptionsWindow = Toplevel(self)
        plotOptionsWindow.title('Refrapick - Plot options')
        plotOptionsWindow.configure(bg = "#F0F0F0")
        # plotOptionsWindow.geometry("350x520")
        plotOptionsWindow.resizable(0,0)
        # plotOptionsWindow.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())
        Label(plotOptionsWindow, text = "Plot options",font=("Arial", 11)).grid(row=0,column=0,sticky="EW",pady=5,padx=65)
        Button(plotOptionsWindow,text="Change maximum display time", command = editMaxTime, width = 30).grid(row = 1, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change trace color", command = editTraceColor, width = 30).grid(row = 2, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change fill color", command = editFillColor, width = 30).grid(row = 3, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change background color", command = editBackgroundColor, width = 30).grid(row = 4, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Enable/disable grid lines", command = gridOnOff, width = 30).grid(row = 5, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change grid lines style", command = editGridStyle, width = 30).grid(row = 6, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change grid lines color", command = editGridColor, width = 30).grid(row = 7, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change pick color", command = editPickColor, width = 30).grid(row = 8, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change pick marker", command = editPickMarker, width = 30).grid(row = 9, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change pick line color", command = editPickLineColor, width = 30).grid(row = 10, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change pick line style", command = editPickLineStyle, width = 30).grid(row = 11, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change traveltimes line color", command = editTraveltimeLineColor, width = 30).grid(row = 12, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change traveltimes line style", command = editTraveltimeLineStyle, width = 30).grid(row = 13, column = 0,pady=5,padx=65)
        Button(plotOptionsWindow,text="Change scale gain factor", command = editGainFactor, width = 30).grid(row = 14, column = 0,pady=5,padx=65)

        plotOptionsWindow.tkraise()

    def options(self):

        if self.sts:

            def editdx():

                new_dx = simpledialog.askfloat("Refrapick","Enter the new receiver spacing in meters (for %s):"%self.stNames[self.currentSt])

                if new_dx != None:

                    if new_dx > 0:

                        if self.xpicks[self.currentSt]: self.clearPicks()

                        self.receiverPositions[self.currentSt] = [i/self.dxs[self.currentSt] for i in self.receiverPositions[self.currentSt]]
                        self.xends[self.currentSt] = self.xends[self.currentSt]/self.dxs[self.currentSt]
                        self.dxs[self.currentSt] = new_dx
                        self.receiverPositions[self.currentSt] = [i*self.dxs[self.currentSt] for i in self.receiverPositions[self.currentSt]]
                        self.xends[self.currentSt] = self.xends[self.currentSt]*self.dxs[self.currentSt]

                        for i in range(len(self.tracesArts[self.currentSt])):

                            a = self.tracesData[self.currentSt][i]
                            self.tracesArts[self.currentSt][i].set_xdata(a/max(a)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                            self.tracesArtsIn[self.currentSt][i].set_xdata(a/max(a)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                        self.axs[self.currentSt].set_xlim(self.x1s[self.currentSt]-self.dxs[self.currentSt]/2, self.xends[self.currentSt]+self.dxs[self.currentSt]/2)

                        self.updatePlotTitle()

                        if self.fillSide == 0: self.wigglesOnly()
                        elif self.fillSide == -1: self.fillNegative()

                        self.clipAmplitudes()

                        messagebox.showinfo(title="Refrapick", message="The receiver spacing was updated in %s"%self.stNames[self.currentSt])
                        optionsWindow.tkraise()

                    else: messagebox.showerror(title="Refrapick", message="Invalid dx value!")

            def editx1():

                new_x1 = simpledialog.askfloat("Refrapick","Enter the new position for the first receiver in meters (for %s):"%self.stNames[self.currentSt])

                if new_x1:

                    if self.xpicks[self.currentSt]: self.clearPicks()

                    self.x1s[self.currentSt] = new_x1
                    self.xends[self.currentSt] = self.xends[self.currentSt]+new_x1
                    self.receiverPositions[self.currentSt] = [i+new_x1 for i in self.receiverPositions[self.currentSt]]

                    for i in range(len(self.tracesArts[self.currentSt])):

                        a = self.tracesData[self.currentSt][i]
                        self.tracesArts[self.currentSt][i].set_xdata(a/max(a)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                        self.tracesArtsIn[self.currentSt][i].set_xdata(a/max(a)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                    self.axs[self.currentSt].set_xlim(self.x1s[self.currentSt]-self.dxs[self.currentSt]/2, self.xends[self.currentSt]+self.dxs[self.currentSt]/2)

                    if self.fillSide == 0: self.wigglesOnly()
                    elif self.fillSide == -1: self.fillNegative()

                    self.clipAmplitudes()

                    self.axs[self.currentSt].set_xlim(self.x1s[self.currentSt]-self.dxs[self.currentSt]/2, self.xends[self.currentSt]+self.dxs[self.currentSt]/2)
                    self.figs[self.currentSt].canvas.draw_idle()
                    messagebox.showinfo(title="Refrapick", message="The position of the first receiver was updated in %s"%self.stNames[self.currentSt])
                    optionsWindow.tkraise()

            def editsource():

                new_source = simpledialog.askfloat("Refrapick","Enter the new source position in meters (for %s):"%self.stNames[self.currentSt])

                if new_source != None:

                    self.sources[self.currentSt] = new_source
                    self.updatePlotTitle()
                    messagebox.showinfo(title="Refrapick", message="The source position was updated in %s"%self.stNames[self.currentSt])
                    optionsWindow.tkraise()

            optionsWindow = Toplevel(self)
            optionsWindow.title('Refrapick - Edit parameters')
            optionsWindow.configure(bg = "#F0F0F0")
            # optionsWindow.geometry("350x170")
            optionsWindow.resizable(0,0)
            # optionsWindow.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())
            Label(optionsWindow, text = "Editing parameters in %s"%self.stNames[self.currentSt],font=("Arial", 11)).grid(row=0,column=0,sticky="EW",pady=5,padx=65)
            Button(optionsWindow,text="Edit receiver spacing", command = editdx, width = 30).grid(row = 1, column = 0,pady=5,padx=65)
            Button(optionsWindow,text="Edit first receiver position", command = editx1, width = 30).grid(row = 2, column = 0,pady=5,padx=65)
            Button(optionsWindow,text="Edit source position", command = editsource, width = 30).grid(row = 3, column = 0,pady=5,padx=65)
            optionsWindow.tkraise()

    def correctShotTime(self):

        if self.sts:

            delay = simpledialog.askfloat("Refrapick","Enter the delay time in seconds to correct shot time:")

            if delay:

                for i in range(len(self.sts)):

                    for j in range(len(self.tracesArts[self.currentSt])):

                        self.tracesArts[i][j].set_ydata(self.tracesTime[i][j]+delay)
                        self.tracesArtsIn[i][j].set_ydata(self.tracesTime[i][j]+delay)
                        self.tracesTime[i][j]+=delay

                    if self.invertedTimeAxis[i] == 0: self.axs[i].set_ylim(min(self.tracesTime[i][0]), max(self.tracesTime[i][0]))
                    else:
                        self.axs[i].invert_yaxis()
                        self.axs[i].set_ylim(min(self.tracesTime[i][0]), max(self.tracesTime[i][0]))
                        self.axs[i].invert_yaxis()

                    self.figs[i].canvas.draw_idle()

                    if self.fillSide == 0: self.wigglesOnly()
                    elif self.fillSide == -1: self.fillNegative()

                    self.clipAmplitudes()

                messagebox.showinfo(title="Refrapick", message="Shot time has been corrected for all opened waveforms!")

    def createProject(self):

        self.projPath = filedialog.askdirectory(initialdir=path.expanduser('~/Documents'))

        if self.projPath:

            projName = simpledialog.askstring("Refrapick","Enter the name of the project to be created:")

            if not path.exists(self.projPath+"/"+projName):

                makedirs(self.projPath+"/"+projName)
                local = self.projPath+"/"+projName+"/"
                makedirs(local+"data")
                self.p_data = local+"data/"
                makedirs(local+"picks")
                self.p_picks = local+"picks/"
                makedirs(local+"models")
                self.p_models = local+"models/"
                makedirs(local+"gps")
                self.p_gps = local+"gps/"
                self.projPath = local
                self.projReady = True
                print("Refrapick: Successfully created the project!")
                self.statusLabel.configure(text="Project path ready!",font=("Arial", 11))

            else:

                messagebox.showinfo(title="Refrapick", message="A project was detected, please choose another name or directory!")

    def loadProject(self):

        self.projPath = filedialog.askdirectory(initialdir=path.expanduser('~/Documents'))

        if self.projPath:

            if path.exists(self.projPath+"/"+"data") and \
            path.exists(self.projPath+"/"+"picks") and \
            path.exists(self.projPath+"/"+"models") and \
            path.exists(self.projPath+"/"+"gps"):

                self.p_data = self.projPath+"/"+"data/"
                self.p_picks = self.projPath+"/"+"picks/"
                self.p_models = self.projPath+"/"+"models/"
                self.p_gps = self.projPath+"/"+"gps/"
                self.projReady = True
                print("Refrapick: Successfully loaded the project path!")
                self.statusLabel.configure(text="Project path ready!",font=("Arial", 11))

            else: messagebox.showerror(title="Refrapick", message="Not all folders were detected!\nPlease, check the structure of the selected project.")

    def openWaveform(self):

        if self.projReady:

            if self.pickMode: self.pick()
            if self.velMode: self.appVelMode()

            files = filedialog.askopenfilenames(title='Open', initialdir = self.projPath+"/data/", filetypes=[('SEGY file', ('*.sgy', '*.segy')),
                                                                                                              ('SEG2 file', ('*.sg2', '*.dat')),
                                                                                                            ('SU file', '*.su')
                                                                                                            ])

            if files:

                if self.sts: n = len(self.sts)
                else: n = 0

                # Handle SU file containing multiple shots
                flag_long_su = False
                if len(files) == 1:
                    _, extension = path.splitext(files[0])
                    if extension.lower() == '.su':
                        st = read(files[0])

                        # Extract the original_field_record_number from each trace
                        original_field_record_numbers = [trace.stats.su.trace_header.original_field_record_number for trace in st]

                        # Find the unique original_field_record_numbers
                        unique_original_field_record_numbers = unique(original_field_record_numbers)

                        if len(unique_original_field_record_numbers) > 1:
                            # Create a list of lists of traces with the same original_field_record_number
                            st_all = [[tr for tr in st if tr.stats.su.trace_header.original_field_record_number == original_field_record_number] for original_field_record_number in unique_original_field_record_numbers]
                            flag_long_su = True
                            files = [files[0]]*len(st_all)

                for i, file in tqdm(enumerate(files), total=len(files), desc="Reading files"):

                    if flag_long_su == True:
                        st = st_all[i]
                    else:
                        st = read(file)

                    if st[0].stats._format == "SEG2":

                        dx = float(st[1].stats.seg2['RECEIVER_LOCATION'])-float(st[0].stats.seg2['RECEIVER_LOCATION'])
                        delay = float(st[0].stats.seg2['DELAY'])
                        source = float(st[0].stats.seg2['SOURCE_LOCATION'])
                        x1 = float(st[0].stats.seg2['RECEIVER_LOCATION'])
                        xend = float(st[-1].stats.seg2['RECEIVER_LOCATION'])
                        xall = []
                        for trace in st:
                            xall.append(float(trace.stats.seg2['RECEIVER_LOCATION']))

                    elif st[0].stats._format == "SU":
                        xsca = abs(float(st[0].stats.su['trace_header']['scalar_to_be_applied_to_all_coordinates']))
                        dx = (float(st[1].stats.su['trace_header']['group_coordinate_x'])-float(st[0].stats.su['trace_header']['group_coordinate_x']))/xsca
                        delay = float(st[0].stats.su['trace_header']['delay_recording_time']/1000)
                        source = float(st[0].stats.su['trace_header']['source_coordinate_x'])/xsca
                        x1 = float(st[0].stats.su['trace_header']['group_coordinate_x'])/xsca
                        xend = float(st[-1].stats.su['trace_header']['group_coordinate_x'])/xsca
                        xall = []
                        for trace in st:
                            xall.append(float(trace.stats.su['trace_header']['group_coordinate_x'])/xsca)

                    elif st[0].stats._format == "SEGY":
                        xsca = abs(float(st[0].stats.segy['trace_header']['scalar_to_be_applied_to_all_coordinates']))
                        dx = (float(st[1].stats.segy['trace_header']['group_coordinate_x'])-float(st[0].stats.segy['trace_header']['group_coordinate_x']))/xsca
                        delay = float(st[0].stats.segy['trace_header']['delay_recording_time']/1000)
                        source = float(st[0].stats.segy['trace_header']['source_coordinate_x'])/xsca
                        x1 = float(st[0].stats.segy['trace_header']['group_coordinate_x'])/xsca
                        xend = float(st[-1].stats.segy['trace_header']['group_coordinate_x'])/xsca
                        xall = []
                        for trace in st:
                            xall.append(float(trace.stats.segy['trace_header']['group_coordinate_x'])/xsca)

                    else:

                        dx = simpledialog.askfloat("Refrapick","Enter the receiver spacing (in meters) for %s:"%path.basename(file))
                        if dx == None or dx <= 0: dx = 1; messagebox.showinfo('Refrapick','No valid dx entered: dx = 1 m will be assigned to %s'%path.basename(file))
                        x1 = simpledialog.askfloat("Refrapick","Enter the first receiver position (in meters) for %s:"%path.basename(file))
                        if x1 == None: x1 = 0; messagebox.showinfo('Refrapick','No x1 value entered: x1 = 0 m will be assigned to %s'%path.basename(file))
                        source = simpledialog.askfloat("Refrapick","Enter the source position (in meters) for %s:"%path.basename(file))
                        if source == None: source = -1; messagebox.showinfo('Refrapick','No source value entered: source = -1 m will be assigned to %s'%path.basename(file))
                        delay = simpledialog.askfloat("Refrapick","Enter the delay for shot time correction (in seconds) for %s:"%path.basename(file))
                        if delay == None: delay = 0; messagebox.showinfo('Refrapick','No delay time entered: delay = 0 s will be used for %s'%path.basename(file))
                        xend = x1+dx*(len(st)-1)

                    self.dxs.append(dx)
                    self.sources.append(source)
                    self.x1s.append(x1)
                    self.xends.append(xend)
                    self.xalls.append(xall)
                    self.nchannels.append(len(st))
                    self.samplingRates.append(int(st[0].stats['sampling_rate']))
                    self.originalSamplingRates.append(int(st[0].stats['sampling_rate']))
                    self.originalMaxTime = max([max(tr.times()+self.delay) for tr in st])
                    self.delay = delay

                    frame = Frame(self)
                    frame.grid(row = 1, column = 0, sticky = "WE")
                    fig = plt.figure(figsize = (15.9,8.1))
                    canvas = FigureCanvasTkAgg(fig, frame)
                    canvas.draw_idle()
                    toolbar = NavigationToolbar2Tk(canvas, frame)
                    toolbar.update()
                    canvas._tkcanvas.pack()
                    ax = fig.add_subplot(111)
                    fig.patch.set_facecolor('#F0F0F0')
                    ax.set_facecolor(self.backgroundColor)

                    # Create an initial inset axes for the zoom window
                    axin = ax.inset_axes([0.5-0.45/2, -0.05, 0.45, 0.4])
                    # Set the color of the axes, ticks, and tick labels to blue
                    axin.spines['bottom'].set_color('blue')
                    axin.spines['top'].set_color('blue')
                    axin.spines['right'].set_color('blue')
                    axin.spines['left'].set_color('blue')

                    axin.xaxis.label.set_color('blue')
                    axin.yaxis.label.set_color('blue')

                    axin.tick_params(axis='x', colors='blue')
                    axin.tick_params(axis='y', colors='blue')

                    axin.set_visible(False)  # Hide the inset axes
                    self.axins.append(axin)

                    self.tracesMaxs.append([])
                    self.errpicks.append([])
                    self.tpicks.append([])
                    self.xpicks.append([])
                    self.frames.append(frame)
                    self.axs.append(ax)
                    self.figs.append(fig)
                    self.sts.append(st)
                    self.tracesArts.append([])
                    self.tracesArtsIn.append([])
                    self.pickLineArts.append(False)
                    self.fillArts.append([])
                    self.fillArtsIn.append([])
                    self.tracesData.append([])
                    self.tracesTime.append([])
                    self.pickConnections.append([False,False,False,False,False,False])
                    self.velConnections.append([False,False,False])
                    self.originalTracesData.append([])
                    self.originalTracesTimes.append([])
                    self.receiverPositions.append([])
                    self.gains.append(1)
                    # self.fillSide.append(-1)
                    # self.amplitudeClip.append(1)
                    self.invertedTimeAxis.append(1)
                    self.filters.append([False,False])
                    self.picksArts.append([])
                    self.picksArtsIn.append([])

                    for j, tr in enumerate(st):

                        tr.data *= -1
                        self.tracesMaxs[i+n].append(max(tr.data))
                        t, = ax.plot(tr.data/max(tr.data)+xall[j], tr.times()+self.delay, c = self.traceColor, lw = .7)
                        self.tracesArts[i+n].append(t)
                        tIn, = axin.plot(tr.data/max(tr.data)+xall[j], tr.times()+self.delay, c = self.traceColor, lw = .7)
                        self.tracesArtsIn[i+n].append(tIn)
                        self.tracesData[i+n].append(tr.data)
                        self.tracesTime[i+n].append(tr.times()+self.delay,)
                        self.originalTracesData[i+n].append(tr.data)
                        self.originalTracesTimes[i+n].append(tr.times()+self.delay,)

                        if st[0].stats._format == "SEG2": self.receiverPositions[i+n].append(float(tr.stats.seg2['RECEIVER_LOCATION']))
                        else: self.receiverPositions[i+n].append(xall[j])

                        t.get_xdata()[t.get_xdata() < xall[j]-((dx/2)*0.9)] = xall[j]-((dx/2)*0.9)
                        t.get_xdata()[t.get_xdata() > xall[j]+((dx/2)*0.9)] = xall[j]+((dx/2)*0.9)
                        t.set_xdata(t.get_xdata())

                        tIn.get_xdata()[tIn.get_xdata() < xall[j]-((dx/2)*0.9)] = xall[j]-((dx/2)*0.9)
                        tIn.get_xdata()[tIn.get_xdata() > xall[j]+((dx/2)*0.9)] = xall[j]+((dx/2)*0.9)
                        tIn.set_xdata(tIn.get_xdata())


                        fill = ax.fill_betweenx(t.get_ydata(),
                                            xall[j],
                                            t.get_xdata(),
                                            where = t.get_xdata() >= xall[j],
                                            color=self.fillColor)
                        self.fillArts[i+n].append(fill)

                        fillIn = axin.fill_betweenx(t.get_ydata(),
                                            xall[j],
                                            t.get_xdata(),
                                            where = t.get_xdata() >= xall[j],
                                            color=self.fillColor)
                        self.fillArtsIn[i+n].append(fillIn)

                    ax.set_ylabel("TIME [s]")
                    ax.set_xlabel("RECEIVER POSITION [m]")
                    axin.set_ylabel("TIME [s]")
                    axin.set_xlabel("RECEIVER POSITION [m]")

                    if self.grid: ax.grid(lw = .5, alpha = .5, c = self.gridColor, ls = self.gridStyle)
                    ax.set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d | sampling = %d Hz | gain = %d"%(i+n+1,
                                                                                                                                     n+len(files),
                                                                                                                                     path.basename(file),
                                                                                                                                     source,dx,
                                                                                                                                     self.nchannels[i],
                                                                                                                                     self.originalSamplingRates[i],
                                                                                                                                     self.gains[i]))
                    self.stNames.append(path.basename(file))

                    if self.maxTime:
                        max_time = self.maxTime
                    else:
                        max_time = self.originalMaxTime
                        self.maxTime = max_time

                    ax.set_ylim(min(tr.times()+self.delay,), max_time)
                    ax.set_xlim(x1-dx/2, xend+dx/2)
                    ax.invert_yaxis()

                    # Draw a cross at the center of the inset
                    axin.annotate('', xy=(0.5, 0), xycoords='axes fraction', xytext=(0.5, 1), textcoords='axes fraction', arrowprops=dict(arrowstyle="-", color='b'))
                    axin.annotate('', xy=(0, 0.5), xycoords='axes fraction', xytext=(1, 0.5), textcoords='axes fraction', arrowprops=dict(arrowstyle="-", color='b'))

                    self.yLimSet()

                    self.figs[i+n].canvas.draw_idle()

                self.frames[0].tkraise()
                self.statusLabel.lift()
                self.statusLabel.configure(text="Waveform(s) ready!",font=("Arial", 11))
                self.currentSt = 0

                if n == 0:
                    if flag_long_su == True:
                        print('Refrapick: %d shots loaded succesfully from SU file!' % len(st_all))
                    else:
                        print('Refrapick: %d file(s) loaded succesfully!' % len(files))
                else:
                    if flag_long_su == True:
                        print('Refrapick: %d new shots loaded succesfully from SU file!' % len(st_all))
                    else:
                        print('Refrapick: %d new file(s) loaded succesfully!' % len(files))

    def help(self):

        helpWindow = Toplevel(self)
        helpWindow.title('Refrapick - Help')
        helpWindow.configure(bg = "#F0F0F0")
        helpWindow.resizable(0,0)
        # helpWindow.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())

        Label(helpWindow, text = """Refrapy - Refrapick v2.0.0



Refrapick provides tools for basic waveform processing and first-breaks picking on seismic refraction data.

If you use Refrapy in your work, please consider citing the following paper:

Guedes, V.J.C.B., Maciel, S.T.R., Rocha, M.P., 2022. Refrapy: A Python program for seismic refraction data analysis,
Computers and Geosciences. https://doi.org/10.1016/j.cageo.2021.105020.

To report a bug and for more information, please visit github.com/viictorjs/Refrapy.



Author: Victor Guedes, MSc
E-mail: vjs279@hotmail.com
""",font=("Arial", 11)).pack()
        helpWindow.tkraise()

    def viewSurvey(self):

        if self.sts:

            surveyWindow = Toplevel(self)
            surveyWindow.title('Refrapick - View survey')
            surveyWindow.configure(bg = "#F0F0F0")
            surveyWindow.resizable(0,0)
            # surveyWindow.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())

            frame = Frame(surveyWindow, width=20, height=20)
            frame.grid(row = 0, column = 0)
            fig = plt.figure(figsize = (14.2,8.62))
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw_idle()
            toolbar = NavigationToolbar2Tk(canvas, frame)
            toolbar.update()
            canvas._tkcanvas.pack()
            ax = fig.add_subplot(111)
            fig.patch.set_facecolor('#F0F0F0')
            ax.set_ylabel("RECORD NAME")
            ax.set_xlabel("POSITION [m]")
            ax.grid(lw = .5, alpha = .5)
            ax.set_title("Survey geometry")

            for i in range(len(self.sts)):

                ax.plot(self.receiverPositions[i], [self.stNames[i]]*self.nchannels[i], "-v", c = "k")
                ax.scatter(self.sources[i], self.stNames[i], marker = "*", c = "y", edgecolor = "k", s = 150, zorder = 99)

            ax.invert_yaxis()
            fig.canvas.draw_idle()
            surveyWindow.tkraise()

    def invertTimeAxis(self):

        if self.sts:

            self.axs[self.currentSt].invert_yaxis()
            self.axins[self.currentSt].invert_yaxis()

            if self.invertedTimeAxis[self.currentSt] == 1: self.invertedTimeAxis[self.currentSt] = 0
            else: self.invertedTimeAxis[self.currentSt] = 1

            self.figs[self.currentSt].canvas.draw_idle()

    def updatePlotTitle(self):

        if self.filters[self.currentSt][1] and self.filters[self.currentSt][0]: self.axs[self.currentSt].set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d |sampling = %d Hz | filters = %.2f Hz - %.2f Hz | gain = %d"%(
                                                                                                                                         self.currentSt+1,
                                                                                                                                         len(self.sts),
                                                                                                                                         self.stNames[self.currentSt],
                                                                                                                                         self.sources[self.currentSt],
                                                                                                                                         self.dxs[self.currentSt],
                                                                                                                                         self.nchannels[self.currentSt],
                                                                                                                                         self.samplingRates[self.currentSt],
                                                                                                                                         self.filters[self.currentSt][0],
                                                                                                                                         self.filters[self.currentSt][1],
                                                                                                                                         self.gains[self.currentSt]))

        elif self.filters[self.currentSt][1] and not self.filters[self.currentSt][0]: self.axs[self.currentSt].set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d |sampling = %d Hz | filters = %.2f Hz (low-pass) | gain = %d"%(
                                                                                                                                    self.currentSt+1,
                                                                                                                                    len(self.sts),
                                                                                                                                    self.stNames[self.currentSt],
                                                                                                                                    self.sources[self.currentSt],
                                                                                                                                    self.dxs[self.currentSt],
                                                                                                                                    self.nchannels[self.currentSt],
                                                                                                                                    self.samplingRates[self.currentSt],
                                                                                                                                    self.filters[self.currentSt][1],
                                                                                                                                    self.gains[self.currentSt]))

        elif self.filters[self.currentSt][0] and not self.filters[self.currentSt][1]: self.axs[self.currentSt].set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d | sampling = %d Hz | filters = %.2f Hz (high-pass) | gain = %d"%(
                                                                                                                                    self.currentSt+1,
                                                                                                                                    len(self.sts),
                                                                                                                                    self.stNames[self.currentSt],
                                                                                                                                    self.sources[self.currentSt],
                                                                                                                                    self.dxs[self.currentSt],
                                                                                                                                    self.nchannels[self.currentSt],
                                                                                                                                    self.samplingRates[self.currentSt],
                                                                                                                                    self.filters[self.currentSt][0],
                                                                                                                                    self.gains[self.currentSt]))

        else: self.axs[self.currentSt].set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d | sampling = %d Hz | gain = %d"%(
                                                                                                                                     self.currentSt+1,
                                                                                                                                     len(self.sts),
                                                                                                                                     self.stNames[self.currentSt],
                                                                                                                                     self.sources[self.currentSt],
                                                                                                                                     self.dxs[self.currentSt],
                                                                                                                                     self.nchannels[self.currentSt],
                                                                                                                                     self.samplingRates[self.currentSt],
                                                                                                                                     self.gains[self.currentSt]))
        self.figs[self.currentSt].canvas.draw_idle()

    def resampleTraces(self):

        if self.sts:

            newSamplingFreq = simpledialog.askinteger("Refrapick","Enter the new sampling frequency (current = %d Hz):"%self.samplingRates[self.currentSt])

            if newSamplingFreq:

                if newSamplingFreq >= 100:

                    for i in range(len(self.sts[self.currentSt])):

                        if len(self.fillArts[self.currentSt]) > i:
                            self.fillArts[self.currentSt][:].pop(i).remove()
                            self.fillArtsIn[self.currentSt][:].pop(i).remove()

                    del self.fillArts[self.currentSt][:]
                    del self.fillArtsIn[self.currentSt][:]

                    for i, tr in enumerate(self.tracesData[self.currentSt]):

                        tlen = max(self.tracesTime[self.currentSt][i])
                        n = int(newSamplingFreq*tlen)
                        new_data, new_time = resample(tr, n, self.tracesTime[self.currentSt][i])
                        self.tracesData[self.currentSt][i] = new_data
                        self.tracesTime[self.currentSt][i] = new_time

                        self.tracesArts[self.currentSt][i].set_xdata(new_data/max(new_data)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                        self.tracesArts[self.currentSt][i].set_ydata(new_time)

                        self.tracesArtsIn[self.currentSt][i].set_xdata(new_data/max(new_data)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                        self.tracesArtsIn[self.currentSt][i].set_ydata(new_time)

                        tr = self.tracesArts[self.currentSt][i]
                        tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                        tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                        tr.set_xdata(tr.get_xdata())

                        tr = self.tracesArtsIn[self.currentSt][i]
                        tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                        tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                        tr.set_xdata(tr.get_xdata())

                        fill = self.axs[self.currentSt].fill_betweenx(self.tracesArts[self.currentSt][i].get_ydata(),
                                        self.xalls[self.currentSt][i],
                                        self.tracesArts[self.currentSt][i].get_xdata(),
                                        where = self.tracesArts[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                        color=self.fillColor)
                        self.fillArts[self.currentSt].append(fill)

                        fillIn = self.axins[self.currentSt].fill_betweenx(self.tracesArtsIn[self.currentSt][i].get_ydata(),
                                        self.xalls[self.currentSt][i],
                                        self.tracesArtsIn[self.currentSt][i].get_xdata(),
                                        where = self.tracesArtsIn[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                        color=self.fillColor)
                        self.fillArtsIn[self.currentSt].append(fillIn)

                    self.samplingRates[self.currentSt] = newSamplingFreq

                    self.updatePlotTitle()

                else: messagebox.showerror('Refrapick','Enter a value greater or equal than 100 Hz!')

    def trimTraces(self):

        if self.sts:

            maxTime = simpledialog.askfloat("Refrapick","Enter the new maximum time:")

            if maxTime:

                for i in range(len(self.tracesArts[self.currentSt])):

                    self.tracesData[self.currentSt][i] = self.tracesData[self.currentSt][i][self.tracesTime[self.currentSt][i] <= maxTime]
                    self.tracesTime[self.currentSt][i] = self.tracesTime[self.currentSt][i][self.tracesTime[self.currentSt][i] <= maxTime]

                    self.tracesArts[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                    self.tracesArts[self.currentSt][i].set_ydata(self.tracesTime[self.currentSt][i])

                    self.tracesArtsIn[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                    self.tracesArtsIn[self.currentSt][i].set_ydata(self.tracesTime[self.currentSt][i])

                    tr = self.tracesArts[self.currentSt][i]
                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                    tr = self.tracesArtsIn[self.currentSt][i]
                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                self.axs[self.currentSt].set_ylim(min(self.tracesArts[self.currentSt][0].get_ydata()),
                                                      max(self.tracesArts[self.currentSt][0].get_ydata()))

                if self.invertedTimeAxis[self.currentSt] == 1: self.axs[self.currentSt].invert_yaxis()

                self.figs[self.currentSt].canvas.draw_idle()

    def clipAmplitudes(self):

        if self.sts:

            if self.amplitudeClip == 1:

                for i, tr in enumerate(self.tracesArts[self.currentSt]):

                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):

                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                self.amplitudeClip = 0

            else:

                for i, tr in enumerate(self.tracesArts[self.currentSt]):

                    amp = self.tracesData[self.currentSt][i]
                    tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):

                    amp = self.tracesData[self.currentSt][i]
                    tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                self.amplitudeClip = 1

            if self.fillSide == 0: self.wigglesOnly()
            elif self.fillSide == -1: self.fillNegative()
            elif self.fillSide == 1: self.fillPositive()

            self.figs[self.currentSt].canvas.draw_idle()

    def wigglesOnly(self):

        if self.fillSide == 1 or self.fillSide == -1:

            for i in range(len(self.sts[self.currentSt])):

                self.fillArts[self.currentSt][:].pop(i).remove()
                self.fillArtsIn[self.currentSt][:].pop(i).remove()

            del self.fillArts[self.currentSt][:]
            del self.fillArtsIn[self.currentSt][:]
            self.fillSide = 0
            self.figs[self.currentSt].canvas.draw_idle()

    def fillNegative(self):

        if self.sts:

            if self.fillSide == -1 or self.fillSide == 1:

                for i in range(len(self.sts[self.currentSt])):

                    if len(self.fillArts[self.currentSt]) > i:
                        self.fillArts[self.currentSt][:].pop(i).remove()
                        self.fillArtsIn[self.currentSt][:].pop(i).remove()

                del self.fillArts[self.currentSt][:]
                del self.fillArtsIn[self.currentSt][:]

            for i in range(len(self.sts[self.currentSt])):

                fill = self.axs[self.currentSt].fill_betweenx(self.tracesArts[self.currentSt][i].get_ydata(),
                                self.xalls[self.currentSt][i],
                                self.tracesArts[self.currentSt][i].get_xdata(),
                                where = self.tracesArts[self.currentSt][i].get_xdata() <= self.xalls[self.currentSt][i],
                                color=self.fillColor)
                self.fillArts[self.currentSt].append(fill)

                fillIn = self.axins[self.currentSt].fill_betweenx(self.tracesArtsIn[self.currentSt][i].get_ydata(),
                                self.xalls[self.currentSt][i],
                                self.tracesArtsIn[self.currentSt][i].get_xdata(),
                                where = self.tracesArtsIn[self.currentSt][i].get_xdata() <= self.xalls[self.currentSt][i],
                                color=self.fillColor)
                self.fillArtsIn[self.currentSt].append(fillIn)

            self.fillSide = -1
            self.figs[self.currentSt].canvas.draw_idle()

    def fillPositive(self):

        if self.sts:

            if self.fillSide == -1 or self.fillSide == 1:

                for i in range(len(self.sts[self.currentSt])):

                    if len(self.fillArts[self.currentSt]) > i:
                        self.fillArts[self.currentSt][:].pop(i).remove()
                        self.fillArtsIn[self.currentSt][:].pop(i).remove()

                del self.fillArts[self.currentSt][:]
                del self.fillArtsIn[self.currentSt][:]


            for i in range(len(self.sts[self.currentSt])):

                fill = self.axs[self.currentSt].fill_betweenx(self.tracesArts[self.currentSt][i].get_ydata(),
                                self.xalls[self.currentSt][i],
                                self.tracesArts[self.currentSt][i].get_xdata(),
                                where = self.tracesArts[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                color=self.fillColor)
                self.fillArts[self.currentSt].append(fill)

                fillIn = self.axins[self.currentSt].fill_betweenx(self.tracesArtsIn[self.currentSt][i].get_ydata(),
                                self.xalls[self.currentSt][i],
                                self.tracesArtsIn[self.currentSt][i].get_xdata(),
                                where = self.tracesArtsIn[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                color=self.fillColor)
                self.fillArtsIn[self.currentSt].append(fillIn)

            self.fillSide = 1
            self.figs[self.currentSt].canvas.draw_idle()

    def setGain(self):

        if self.sts:

            for i in range(len(self.tracesArts[self.currentSt])):
                self.tracesArts[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gain+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArts[self.currentSt]):
                tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                tr.set_xdata(tr.get_xdata())

            for i in range(len(self.tracesArtsIn[self.currentSt])):
                self.tracesArtsIn[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gain+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):
                tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                tr.set_xdata(tr.get_xdata())

            self.gains[self.currentSt] = self.gain

            self.updatePlotTitle()
            self.figs[self.currentSt].canvas.draw_idle()

            if self.fillSide == 0: self.wigglesOnly()
            elif self.fillSide == -1: self.fillNegative()
            elif self.fillSide == 1: self.fillPositive()

            if self.amplitudeClip == 1: self.amplitudeClip = 0; self.clipAmplitudes()

    def addGain(self):

        if self.sts:

            self.gains[self.currentSt] += self.gainFactor
            self.gain = self.gains[self.currentSt]

            for i in range(len(self.tracesArts[self.currentSt])):
                self.tracesArts[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArts[self.currentSt]):
                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

            for i in range(len(self.tracesArtsIn[self.currentSt])):
                self.tracesArtsIn[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):
                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

            self.updatePlotTitle()
            self.figs[self.currentSt].canvas.draw_idle()

            if self.fillSide == 0: self.wigglesOnly()
            elif self.fillSide == -1: self.fillNegative()
            elif self.fillSide == 1: self.fillPositive()

            if self.amplitudeClip == 1: self.amplitudeClip = 0; self.clipAmplitudes()

    def removeGain(self):

        if self.sts:

            if self.gains[self.currentSt] - self.gainFactor >= 1: self.gains[self.currentSt] -= self.gainFactor
            self.gain = self.gains[self.currentSt]

            for i in range(len(self.tracesArts[self.currentSt])):
                self.tracesArts[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArts[self.currentSt]):
                tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                tr.set_xdata(tr.get_xdata())

            for i in range(len(self.tracesArtsIn[self.currentSt])):
                self.tracesArtsIn[self.currentSt][i].set_xdata(self.tracesData[self.currentSt][i]/max(self.tracesData[self.currentSt][i])*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

            for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):
                tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                tr.set_xdata(tr.get_xdata())

            self.updatePlotTitle()
            self.figs[self.currentSt].canvas.draw_idle()

            if self.fillSide == 0: self.wigglesOnly()
            elif self.fillSide == -1: self.fillNegative()
            elif self.fillSide == 1: self.fillPositive()

            if self.amplitudeClip == 1: self.amplitudeClip = 0; self.clipAmplitudes()

    def yLimSet(self):

        if self.sts:

            if self.maxTime:
                self.axs[self.currentSt].set_ylim(min(self.tracesArts[self.currentSt][0].get_ydata()),
                                                  self.maxTime)

            if self.invertedTimeAxis[self.currentSt] == 1: self.axs[self.currentSt].invert_yaxis()

            self.figs[self.currentSt].canvas.draw_idle()

    def yLimUp(self):

        if self.sts:

            self.axs[self.currentSt].set_ylim(min(self.tracesArts[self.currentSt][0].get_ydata()),
                                                  self.axs[self.currentSt].get_ylim()[0]*0.8)

            if self.invertedTimeAxis[self.currentSt] == 1: self.axs[self.currentSt].invert_yaxis()

            self.figs[self.currentSt].canvas.draw_idle()

            self.maxTime = self.axs[self.currentSt].get_ylim()[0]

    def yLimDown(self):

        if self.sts:

            self.axs[self.currentSt].set_ylim(min(self.tracesArts[self.currentSt][0].get_ydata()),
                                                  self.axs[self.currentSt].get_ylim()[0]*1.2)

            if self.invertedTimeAxis[self.currentSt] == 1: self.axs[self.currentSt].invert_yaxis()

            self.figs[self.currentSt].canvas.draw_idle()

            self.maxTime = self.axs[self.currentSt].get_ylim()[0]

    def applyFilters(self):

        if self.sts:

            hp = simpledialog.askfloat("Refrapick","Frequency limit for high pass filter (cancel for none):")

            if hp:

                if hp < 0:

                    messagebox.showinfo('Refrapy','A negative high pass value is not valid: 0.1 Hz will be used instead')
                    hp = 0.1

                elif hp > self.samplingRates[self.currentSt]/2:

                    messagebox.showinfo('Refrapy','Invalid high pass value: greater than the Nyquist limit, %.2f Hz will be used instead'%(-1+self.samplingRates[self.currentSt]/2))
                    hp = -1+self.samplingRates[self.currentSt]/2

            lp = simpledialog.askfloat("Refrapick","Frequency limit for low pass filter (cancel for none):")

            if lp:

                if lp > self.samplingRates[self.currentSt]/2:

                    messagebox.showinfo('Refrapy','Invalid low pass value: greater than the Nyquist limit, %.2f Hz will be used instead'%(self.samplingRates[self.currentSt]/2))
                    lp = self.samplingRates[self.currentSt]/2

            if lp:

                for i, data in enumerate(self.tracesData[self.currentSt]):

                    self.tracesData[self.currentSt][i] = lowpass(data, lp, self.samplingRates[self.currentSt])

                self.filters[self.currentSt][1] = lp

            if hp:

                for i, data in enumerate(self.tracesData[self.currentSt]):

                    self.tracesData[self.currentSt][i] = highpass(data, hp, self.samplingRates[self.currentSt])

                self.filters[self.currentSt][0] = hp

            if lp or hp:

                for i in range(len(self.sts[self.currentSt])):

                    if len(self.fillArts[self.currentSt]) > i:
                        self.fillArts[self.currentSt][:].pop(i).remove()
                        self.fillArtsIn[self.currentSt][:].pop(i).remove()

                del self.fillArts[self.currentSt][:]
                del self.fillArtsIn[self.currentSt][:]

                for i, tr in enumerate(self.tracesArts[self.currentSt]):

                        amp = self.tracesData[self.currentSt][i]
                        tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                        tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                        tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                        tr.set_xdata(tr.get_xdata())

                for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):

                        amp = self.tracesData[self.currentSt][i]
                        tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])

                        tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                        tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                        tr.set_xdata(tr.get_xdata())

                for i in range(len(self.sts[self.currentSt])):

                    fill = self.axs[self.currentSt].fill_betweenx(self.tracesArts[self.currentSt][i].get_ydata(),
                                    self.xalls[self.currentSt][i],
                                    self.tracesArts[self.currentSt][i].get_xdata(),
                                    where = self.tracesArts[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                    color=self.fillColor)
                    self.fillArts[self.currentSt].append(fill)

                    fillIn = self.axins[self.currentSt].fill_betweenx(self.tracesArtsIn[self.currentSt][i].get_ydata(),
                                    self.xalls[self.currentSt][i],
                                    self.tracesArtsIn[self.currentSt][i].get_xdata(),
                                    where = self.tracesArtsIn[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                    color=self.fillColor)
                    self.fillArtsIn[self.currentSt].append(fillIn)

                self.updatePlotTitle()

    def restoreTraces(self):

        if self.sts:

            if messagebox.askyesno("Refrapick", "Restore default traces in %s?"%self.stNames[self.currentSt]):

                self.gains[self.currentSt] = 1

                for i in range(len(self.sts[self.currentSt])):

                    if len(self.fillArts[self.currentSt]) > i:
                        self.fillArts[self.currentSt][:].pop(i).remove()
                        self.fillArtsIn[self.currentSt][:].pop(i).remove()

                del self.fillArts[self.currentSt][:]
                del self.fillArtsIn[self.currentSt][:]

                for i, tr in enumerate(self.tracesArts[self.currentSt]):

                    amp = self.originalTracesData[self.currentSt][i]
                    tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                    tr.set_ydata(self.originalTracesTimes[self.currentSt][i])
                    self.tracesData[self.currentSt][i] = amp
                    self.tracesTime[self.currentSt][i] = self.originalTracesTimes[self.currentSt][i]

                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                for i, tr in enumerate(self.tracesArtsIn[self.currentSt]):

                    amp = self.originalTracesData[self.currentSt][i]
                    tr.set_xdata(amp/max(amp)*self.gains[self.currentSt]+self.xalls[self.currentSt][i])
                    tr.set_ydata(self.originalTracesTimes[self.currentSt][i])
                    self.tracesData[self.currentSt][i] = amp
                    self.tracesTime[self.currentSt][i] = self.originalTracesTimes[self.currentSt][i]

                    tr.get_xdata()[tr.get_xdata() < self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]-((self.dxs[self.currentSt]/2)*0.9)
                    tr.get_xdata()[tr.get_xdata() > self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)] = self.xalls[self.currentSt][i]+((self.dxs[self.currentSt]/2)*0.9)
                    tr.set_xdata(tr.get_xdata())

                for i in range(len(self.sts[self.currentSt])):

                    fill = self.axs[self.currentSt].fill_betweenx(self.tracesArts[self.currentSt][i].get_ydata(),
                                    self.xalls[self.currentSt][i],
                                    self.tracesArts[self.currentSt][i].get_xdata(),
                                    where = self.tracesArts[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                    color=self.fillColor)
                    self.fillArts[self.currentSt].append(fill)

                    fillIn = self.axins[self.currentSt].fill_betweenx(self.tracesArtsIn[self.currentSt][i].get_ydata(),
                                    self.xalls[self.currentSt][i],
                                    self.tracesArtsIn[self.currentSt][i].get_xdata(),
                                    where = self.tracesArtsIn[self.currentSt][i].get_xdata() >= self.xalls[self.currentSt][i],
                                    color=self.fillColor)
                    self.fillArtsIn[self.currentSt].append(fillIn)

                self.filters[self.currentSt][0] = False
                self.filters[self.currentSt][1] = False
                self.samplingRates[self.currentSt] = self.originalSamplingRates[self.currentSt]

                self.axs[self.currentSt].set_title("shot %d/%d | %s | source = %.2f m | dx = %.2f m | traces = %d | sampling = %d Hz | gain = %d"%(
                                                                                                                                     self.currentSt+1,
                                                                                                                                     len(self.sts),
                                                                                                                                     self.stNames[self.currentSt],
                                                                                                                                     self.sources[self.currentSt],
                                                                                                                                     self.dxs[self.currentSt],
                                                                                                                                     self.nchannels[self.currentSt],
                                                                                                                                     self.originalSamplingRates[self.currentSt],
                                                                                                                                     self.gains[self.currentSt]))

                if self.invertedTimeAxis[self.currentSt] == 1:

                    self.axs[self.currentSt].set_ylim(max(self.originalTracesTimes[self.currentSt][0]), min(self.originalTracesTimes[self.currentSt][0]))

                else:
                    self.axs[self.currentSt].set_ylim(min(self.originalTracesTimes[self.currentSt][0]), max(self.originalTracesTimes[self.currentSt][0]))

                self.axs[self.currentSt].set_xlim(self.x1s[self.currentSt]-self.dxs[self.currentSt]/2, self.xends[self.currentSt]+self.dxs[self.currentSt]/2)
                self.figs[self.currentSt].canvas.draw_idle()

    def pick(self):

        self.figs[self.currentSt].canvas.get_tk_widget().config(cursor='cross')

        if self.sts:

            if self.pickMode == False:

                if self.velMode: self.appVelMode()

                self.statusLabel.configure(text="Pick mode enabled!",font=("Arial", 11))
                # messagebox.showinfo(title="Refrapick", message="Pick mode enabled")
                print("Refrapick: Pick mode enabled!")

                # Mouse motion event callback
                def on_move(event):

                    # Return immediately if the mouse is outside the axes
                    if event.xdata is None or event.ydata is None:
                        return

                    # Update the limits of the zoom window to zoom in on the plot around the mouse pointer
                    time_factor = 0.02  # The time window will be 0.01 x the total time of the plot
                    self.axins[self.currentSt].set_xlim(event.xdata - self.dxs[self.currentSt]*1.33, event.xdata + self.dxs[self.currentSt]*1.33)
                    self.axins[self.currentSt].set_ylim(event.ydata - self.originalMaxTime*time_factor, event.ydata + self.originalMaxTime*time_factor)

                    # Reverse the y-axis of the inset
                    self.axins[self.currentSt].invert_yaxis()

                    # Make the zoom window visible
                    self.axins[self.currentSt].set_visible(True)

                    # Redraw the figure
                    self.figs[self.currentSt].canvas.draw_idle()
                    self.figs[self.currentSt].canvas.get_tk_widget().config(cursor='cross')

                def errorPick(t,err=0.1,is_relative=True,min_abs_err=0.5e-3,max_abs_err=5e-3,max_rel_err=None):
                    # t: time (in s)
                    # err: error (in s or fraction of t)
                    # absolute_error: if True, use err as absolute error (in s), else use err as relative error (in fraction of t)
                    # min_abs_err: minimum absolute error (in s)
                    # max_abs_err: maximum absolute error (in s)
                    # max_rel_err: maximum relative error (in fraction of t)

                        if is_relative:
                            err = err*t
                            if max_abs_err is not None:
                                if err>max_abs_err: err = max_abs_err

                            if min_abs_err is not None:
                                if err<min_abs_err: err = min_abs_err
                        else:
                            if max_rel_err is not None:
                                if err>max_rel_err*t: err = max_rel_err*t

                        return err

                def createPick(x,t):

                    for j in range(len(x)):

                        pickline = self.axs[self.currentSt].scatter(x[j], t[j], marker = self.pickMarker, s = self.pickSize*self.dxs[self.currentSt], color=self.pickColor)
                        pickline_inset = self.axins[self.currentSt].scatter(x[j], t[j], marker = self.pickMarker, s = self.pickSize*self.dxs[self.currentSt]*2, color=self.pickColor)

                        self.picksArts[self.currentSt].append(pickline)
                        self.picksArtsIn[self.currentSt].append(pickline_inset)
                        self.xpicks[self.currentSt].append(x[j])
                        self.tpicks[self.currentSt].append(t[j])
                        self.errpicks[self.currentSt].append(errorPick(t[j],*self.errors))

                    if self.pickLineArts[self.currentSt]:

                        self.drawPicksLine()
                        self.pickLineArts[self.currentSt] = False
                        self.drawPicksLine()

                    self.figs[self.currentSt].canvas.draw_idle()
                    self.figs[self.currentSt].canvas.get_tk_widget().config(cursor='cross')

                def reworkPick(x,t):

                    for j in range(len(x)):

                        index2remove = self.xpicks[self.currentSt].index(x[j])
                        self.picksArts[self.currentSt][index2remove].remove()
                        self.picksArtsIn[self.currentSt][index2remove].remove()
                        del self.picksArts[self.currentSt][index2remove]
                        del self.picksArtsIn[self.currentSt][index2remove]
                        del self.xpicks[self.currentSt][index2remove]
                        del self.tpicks[self.currentSt][index2remove]
                        del self.errpicks[self.currentSt][index2remove]
                        createPick([x[j]],[t[j]])

                def removePick(x,t):

                    for j in range(len(x)):

                        index2remove = self.xpicks[self.currentSt].index(x[j])
                        self.picksArts[self.currentSt][index2remove].remove()
                        self.picksArtsIn[self.currentSt][index2remove].remove()
                        del self.picksArts[self.currentSt][index2remove]
                        del self.picksArtsIn[self.currentSt][index2remove]
                        del self.xpicks[self.currentSt][index2remove]
                        del self.tpicks[self.currentSt][index2remove]
                        del self.errpicks[self.currentSt][index2remove]

                def click1(event):

                    if event.button == 1:

                        x = min(self.receiverPositions[self.currentSt], key = lambda x: abs(event.xdata - x))

                        if x not in self.xpicks[self.currentSt]: createPick([x],[event.ydata])
                        else: reworkPick([x],[event.ydata])

                def click2(event):

                    if event.button == 2:

                        x = min(self.receiverPositions[self.currentSt], key = lambda x: abs(event.xdata - x))

                        if x in self.xpicks[self.currentSt]: removePick([x],[event.ydata])

                def click3(event):

                    if event.button == 3:

                        self.click2on = True
                        x = min(self.receiverPositions[self.currentSt], key = lambda x: abs(event.xdata - x))
                        self.pickLine, = self.axs[self.currentSt].plot(x,event.ydata,c=self.pickLineColor,ls=self.pickLineStyle,lw=.7)
                        self.xpickLine = [x]
                        self.tpickLine = [event.ydata]

                        if x not in self.xpicks[self.currentSt]: createPick([x],[event.ydata])
                        else: reworkPick([x],[event.ydata])

                def move(event):

                    if self.click2on:

                        self.xpickLine.append(event.xdata)
                        self.tpickLine.append(event.ydata)
                        self.pickLine.set_data(self.xpickLine,self.tpickLine)
                        self.figs[self.currentSt].canvas.draw_idle()
                        del self.xpickLine[1:-1]
                        del self.tpickLine[1:-1]
                        self.click2on = True

                def release(event):

                    if self.click2on:

                        x = min(self.receiverPositions[self.currentSt], key = lambda x: abs(event.xdata - x))

                        if self.xpickLine[0] < x:

                            f = interp1d([self.xpickLine[0],x],[self.tpickLine[0],event.ydata], kind = "linear")
                            xarray2pick = [j for j in self.receiverPositions[self.currentSt] if j >= self.xpickLine[0] and j <= x]

                        else:

                            f = interp1d([x,self.xpickLine[0]],[event.ydata,self.tpickLine[0]], kind = "linear")
                            xarray2pick = [j for j in self.receiverPositions[self.currentSt] if j >= x and j <= self.xpickLine[0]]

                        tarray2pick = f(xarray2pick)

                        xpicks2create, tpicks2create = [], []
                        xpicks2rework, tpicks2rework = [], []

                        for j, x in enumerate(xarray2pick):

                            if x not in self.xpicks[self.currentSt]: xpicks2create.append(x); tpicks2create.append(tarray2pick[j])
                            else: xpicks2rework.append(x); tpicks2rework.append(tarray2pick[j])

                        if xpicks2create: createPick(xpicks2create,tpicks2create)
                        if xpicks2rework: reworkPick(xpicks2rework,tpicks2rework)

                        self.pickLine.remove()
                        self.figs[self.currentSt].canvas.draw_idle()
                        del self.xpickLine[:]
                        del self.tpickLine[:]
                        self.click2on = False

                for i in range(len(self.sts)):

                    self.click2on = False
                    conPick1 = self.figs[i].canvas.mpl_connect('button_press_event', click1)
                    conPick2 = self.figs[i].canvas.mpl_connect('button_press_event', click2)
                    conPick3 = self.figs[i].canvas.mpl_connect('button_press_event', click3)
                    conMove = self.figs[i].canvas.mpl_connect('motion_notify_event', move)
                    conRelease = self.figs[i].canvas.mpl_connect('button_release_event', release)
                    conOnMove = self.figs[i].canvas.mpl_connect('motion_notify_event', on_move)
                    self.pickConnections[i][0] = conPick1
                    self.pickConnections[i][1] = conPick2
                    self.pickConnections[i][2] = conPick3
                    self.pickConnections[i][3] = conMove
                    self.pickConnections[i][4] = conRelease
                    self.pickConnections[i][5] = conOnMove
                    self.pickMode = True

            else:

                for i in range(len(self.sts)):

                    for con in self.pickConnections[i]: self.figs[i].canvas.mpl_disconnect(con)
                    self.pickConnections[i][0] = False
                    self.pickConnections[i][1] = False
                    self.pickConnections[i][2] = False
                    self.pickConnections[i][3] = False
                    self.pickConnections[i][4] = False
                    self.pickConnections[i][5] = False

                self.pickMode = False
                self.statusLabel.configure(text="Pick mode disabled!",font=("Arial", 11))
                # messagebox.showinfo(title="Refrapick", message="Pick mode disabled!")
                print("Refrapick: Pick mode disabled!")
                self.figs[self.currentSt].canvas.get_tk_widget().config(cursor='arrow')
                # Hide the zoom window
                self.axins[self.currentSt].set_visible(False)
                self.figs[self.currentSt].canvas.draw_idle()

    def drawPicksLine(self):

        if self.sts:

            if self.xpicks[self.currentSt]:

                if self.pickLineArts[self.currentSt] == False:

                    xinds = array(self.xpicks[self.currentSt]).argsort()
                    sortedx = array(self.xpicks[self.currentSt])[xinds]
                    sortedt = array(self.tpicks[self.currentSt])[xinds]
                    sortederr = array(self.errpicks[self.currentSt])[xinds]
                    line, = self.axs[self.currentSt].plot(sortedx,sortedt,c=self.pickLineColor,lw=.7)
                    # line, = self.axs[self.currentSt].errorbar(sortedx,sortedt,yerr=sortederr,c=self.pickLineColor,lw=.7)
                    self.pickLineArts[self.currentSt] = line

                else:

                    self.pickLineArts[self.currentSt].remove()
                    self.pickLineArts[self.currentSt] = False

                self.figs[self.currentSt].canvas.draw_idle()

    def savePicks(self):

        if self.sts:

            allx = []

            for i in range(len(self.sts)):

                for pos in self.receiverPositions[i]:

                    allx.append(pos)

                if self.xpicks[i]: pickPresent = True; break
                else: pickPresent = False

            sgx = list(set(allx+self.sources))

            if pickPresent == False: messagebox.showerror(title="Refrapick", message="There are no picks to be exported!")

            else:

                if messagebox.askyesno("Refrapick", "Load a topography file (x,z)?"):

                    elevFile = filedialog.askopenfilename(title='Open', initialdir = self.projPath+"/gps/", filetypes=[('Text file', '*.txt'),
                                                                                                                    ('CSV file', '*.csv')])

                    if elevFile:

                        xtopo, ztopo = [], []

                        with open(elevFile, "r") as file:

                            lines = file.readlines()

                            for l in lines:

                                pos = l.replace(' ', ',').replace('	',',').replace(';',',').replace('\n','').split(',')[0]
                                elev = l.replace(' ', ',').replace('	',',').replace(';',',').replace('\n','').split(',')[1]
                                xtopo.append(float(pos))
                                ztopo.append(float(elev))

                        f = interp1d(xtopo,ztopo, kind = "cubic", fill_value=(ztopo[0], ztopo[-1]), bounds_error=False)#, fill_value="extrapolate")
                        sgz = f(sgx)
                        xinds = array(sgx).argsort()
                        sgx = array(sgx)[xinds]
                        sgz = array(sgz)[xinds]
                        pickFile = filedialog.asksaveasfilename(title='Save',
                                                                initialdir = self.projPath+"/picks/",
                                                                initialfile=path.basename(self.projPath)+'.sgt',
                                                                filetypes=[('Pick file', '*.sgt')])

                        if pickFile:

                            with open(pickFile, "w") as outFile:

                                outFile.write("%d # shot/geophone points\n#x y\n"%(len(sgx)))

                                for i in range(len(sgx)):

                                    outFile.write("%.2f %.2f\n"%(sgx[i],sgz[i]))

                                nMeasurements = 0

                                for i in range(len(self.sts)): nMeasurements+=len(self.xpicks[i])

                                outFile.write("%d # measurements\n#s g t err\n"%nMeasurements)

                                for i in range(len(self.sts)):

                                    xinds = array(self.xpicks[i]).argsort()
                                    sortedxpicks = array(self.xpicks[i])[xinds]
                                    sortedtpicks = array(self.tpicks[i])[xinds]
                                    sortederrpicks = array(self.errpicks[i])[xinds]

                                    for xpick, tpick, errpick in zip(sortedxpicks, sortedtpicks, sortederrpicks):

                                        #s = where(sgx == self.sources[i])[0][0]+1
                                        #g = where(sgx == xpick)[0][0]+1
                                        s = isclose(array(sgx), array(self.sources[i])).nonzero()[0]+1
                                        g = isclose(array(sgx), array(xpick)).nonzero()[0]+1
                                        t = tpick
                                        err = errpick
                                        outFile.write("%d %d %.6f %.6f\n"%(s,g,t,err))

                            print("Refrapick: The pick file has been saved!")
                        else:
                            print("Refrapick: No pick file saved!")

                else:

                    pickFile = filedialog.asksaveasfilename(title='Save',
                                                            initialdir = self.projPath+"/picks/",
                                                            initialfile=path.basename(self.projPath)+'.sgt',
                                                            filetypes=[('Pick file', '*.sgt')])
                    xinds = array(sgx).argsort()
                    sgx = array(sgx)[xinds]

                    if pickFile:

                        with open(pickFile, "w") as outFile:

                            outFile.write("%d # shot/geophone points\n"%(len(sgx)))
                            outFile.write("#x y\n")

                            for i in range(len(sgx)):

                                outFile.write("%.2f 0.00\n"%sgx[i])

                            nMeasurements = 0

                            for i in range(len(self.sts)): nMeasurements+=len(self.xpicks[i])

                            outFile.write("%d # measurements\n#s g t err\n"%nMeasurements)

                            for i in range(len(self.sts)):

                                xinds = array(self.xpicks[i]).argsort()
                                sortedxpicks = array(self.xpicks[i])[xinds]
                                sortedtpicks = array(self.tpicks[i])[xinds]
                                sortederrpicks = array(self.errpicks[i])[xinds]

                                for xpick, tpick, errpick in zip(sortedxpicks, sortedtpicks, sortederrpicks):

                                    #s = where(sgx == self.sources[i])[0][0]+1
                                    #g = where(sgx == xpick)[0][0]+1
                                    s = isclose(array(sgx), array(self.sources[i])).nonzero()[0]+1
                                    g = isclose(array(sgx), array(xpick)).nonzero()[0]+1
                                    t = tpick
                                    err = errpick
                                    outFile.write("%d %d %.6f %.6f\n"%(s,g,t,err))


                        # messagebox.showinfo(title="Refrapick", message="The pick file has been saved!")
                        print("Refrapick: The pick file has been saved!")
                    else:
                        print("Refrapick: No pick file saved!")

    def setError(self):
        root = Tk()
        root.title("Refrapick - Error parameters")
        root.withdraw()  # hide the main window
        dialog = self.ParameterDialog(root, self)
        if dialog.result is not None: self.errors = dialog.result

    class ParameterDialog(simpledialog.Dialog):
        def __init__(self, parent, main_class):  # accept main_class as an argument
            self.main_class = main_class  # store main_class
            super().__init__(parent)

        def body(self, master):
            Label(master, text="Picking error (in s or fraction of time):").grid(row=0)
            Label(master, text="Is error relative ? (True/False):").grid(row=1)
            Label(master, text="Min. absolute error (in s):").grid(row=2)
            Label(master, text="Max. absolute error (in s):").grid(row=3)

            self.e1 = Entry(master)
            self.e2 = Entry(master)
            self.e3 = Entry(master)
            self.e4 = Entry(master)

            # Set default values
            self.e1.insert(0, self.main_class.errors[0] if self.main_class.errors[0] is not None else "")
            self.e2.insert(0, self.main_class.errors[1] if self.main_class.errors[1] is not None else "")
            self.e3.insert(0, self.main_class.errors[2] if self.main_class.errors[2] is not None else "")
            self.e4.insert(0, self.main_class.errors[3] if self.main_class.errors[3] is not None else "")

            self.e1.grid(row=0, column=1)
            self.e2.grid(row=1, column=1)
            self.e3.grid(row=2, column=1)
            self.e4.grid(row=3, column=1)

            return self.e1  # initial focus

        def grab_set(self):
            # Call the parent class's grab_set method
            super().grab_set()

            # Center the window
            window_width = self.winfo_reqwidth()
            window_height = self.winfo_reqheight()
            position_right = int(self.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(self.winfo_screenheight() / 2 - window_height / 2)

            self.geometry("+{}+{}".format(position_right, position_down))

        def apply(self):
            err = float(self.e1.get())  # convert to float
            is_relative = self.e2.get().lower() == 'true'  # convert to boolean
            min_abs_err = float(self.e3.get()) if self.e3.get().strip() else None
            max_abs_err = float(self.e4.get()) if self.e4.get().strip() else None

            self.result = [err, is_relative, min_abs_err, max_abs_err]

    def clearPicks(self):

        if self.sts:

            if messagebox.askyesno("Refrapick", "Clear picks in %s?"%self.stNames[self.currentSt]):

                if self.xpicks[self.currentSt]:

                    if self.pickLineArts[self.currentSt]:

                        self.pickLineArts[self.currentSt].remove()
                        self.pickLineArts[self.currentSt] = False

                    for pickArt in self.picksArts[self.currentSt]: pickArt.remove()
                    for pickArtIn in self.picksArtsIn[self.currentSt]: pickArtIn.remove()
                    del self.picksArts[self.currentSt][:]
                    del self.picksArtsIn[self.currentSt][:]
                    del self.xpicks[self.currentSt][:]
                    del self.tpicks[self.currentSt][:]
                    del self.errpicks[self.currentSt][:]

                    self.figs[self.currentSt].canvas.draw_idle()
                    messagebox.showinfo(title="Refrapick", message="All picks in %s have been deleted!"%self.stNames[self.currentSt])

    def loadPicks(self):

        if self.sts:

            pickFile = filedialog.askopenfilename(title='Open', initialdir = self.projPath+"/picks/", filetypes=[('Pick file', '*.sgt')])

            if pickFile:

                with open(pickFile, "r") as file:

                    lines = file.readlines()
                    npoints = int(lines[0].split()[0])
                    sgx = [float(i.split()[0]) for i in lines[2:2+npoints]]

                    # Initialize a counter for lines that start with '#'
                    count = 0
                    # Iterate over the lines
                    for i, line in enumerate(lines):
                        # If the line starts with '#'
                        if line.startswith('#'):
                            # Increment the counter
                            count += 1
                            # If this is the second line that starts with '#'
                            if count == 2:
                                # Store the index and break the loop
                                sgtindx = i
                                break
                    # Get the index positions of 's', 'g', and 't', starting from the second character
                    words = lines[sgtindx][1:].split()
                    s_index = words.index('s')
                    g_index = words.index('g')
                    t_index = words.index('t')
                    if 'err' in words:
                        err_index = words.index('err')

                    # sgtindx = lines.index("#s g t err\n")
                    s = [int(i.split()[s_index]) for i in lines[sgtindx+1:]]
                    g = [int(i.split()[g_index]) for i in lines[sgtindx+1:]]
                    t = [float(i.split()[t_index]) for i in lines[sgtindx+1:]]
                    if 'err' in words:
                        err = [float(i.split()[err_index]) for i in lines[sgtindx+1:]]
                    else:
                        err = [0 for _ in range(len(t))]
                    sx = [sgx[i-1] for i in s]
                    gx = [sgx[i-1] for i in g]
                    loaded = False

                    for i in range(len(self.sts)):

                        for j in range(len(sx)):

                            if self.sources[i] == sx[j] and gx[j] in self.receiverPositions[i]:

                                pickline = self.axs[i].scatter(gx[j], t[j], marker = self.pickMarker, s = self.pickSize*self.dxs[self.currentSt], color=self.pickColor)
                                self.picksArts[i].append(pickline)
                                pickline_inset = self.axins[i].scatter(gx[j], t[j], marker = self.pickMarker, s = self.pickSize*self.dxs[self.currentSt], color=self.pickColor)
                                self.picksArtsIn[i].append(pickline_inset)
                                self.xpicks[i].append(gx[j])
                                self.tpicks[i].append(t[j])
                                self.errpicks[i].append(err[j])
                                loaded = True

                        self.figs[i].canvas.draw_idle()

                    if loaded:
                        # messagebox.showinfo(title="Refrapick", message="The pick file has been loaded!")
                        print("Refrapick: The pick file has been loaded!")
                    else:
                        # messagebox.showerror(title="Refrapick", message="The pick file was not loaded: check if you have selected the correct pick file for the opened waveforms!")
                        print("Refrapick: The pick file was not loaded: check the selected pick file!")

    def allPicks(self):

        if self.sts:

            pickExists = False

            for i in range(len(self.sts)):

                if self.xpicks[i]: pickExists = True; break

            if pickExists:

                if len(self.ttArts) == 0:

                    for i in range(len(self.sts)):

                        if self.currentSt != i:

                            xinds = array(self.xpicks[i]).argsort()
                            sortedxpicks = array(self.xpicks[i])[xinds]
                            sortedtpicks = array(self.tpicks[i])[xinds]
                            sortederrpicks = array(self.errpicks[i])[xinds]
                            l, = self.axs[self.currentSt].plot(sortedxpicks,sortedtpicks,ls=self.traveltimesStyle,lw=.7,c=self.traveltimesColor)
                            # l, = self.axs[self.currentSt].errorbar(sortedxpicks,sortedtpicks,yerr=sortederrpicks,ls=self.traveltimesStyle,lw=.7,c=self.traveltimesColor)
                            self.ttArts.append(l)

                else:

                    for ttPlot in self.ttArts: ttPlot.remove()
                    del self.ttArts[:]

                self.figs[self.currentSt].canvas.draw_idle()

    def viewTraveltimes(self):

        if self.sts:

            pickExists = False

            for i in range(len(self.sts)):

                if self.xpicks[i]: pickExists = True; break

            if pickExists:

                ttWindow = Toplevel(self)
                ttWindow.title('Refrapick - View traveltimes')
                ttWindow.configure(bg = "#F0F0F0")
                ttWindow.resizable(0,0)
                # ttWindow.iconbitmap("%s/images/ico_refrapy.ico"%getcwd())

                frame = Frame(ttWindow, width=20, height=20)
                frame.grid(row = 0, column = 0)
                fig = plt.figure(figsize = (14.2,8.62))
                canvas = FigureCanvasTkAgg(fig, frame)
                canvas.draw_idle()
                toolbar = NavigationToolbar2Tk(canvas, frame)
                toolbar.update()
                canvas._tkcanvas.pack()
                ax = fig.add_subplot(111)
                fig.patch.set_facecolor('#F0F0F0')
                ax.set_ylabel("TRAVELTIME [s]")
                ax.set_xlabel("POSITION [m]")
                ax.grid(lw = .5, alpha = .5)
                ax.set_title("Observed data")

                for i in range(len(self.sts)):

                    xinds = array(self.xpicks[i]).argsort()
                    sortedxpicks = array(self.xpicks[i])[xinds]
                    sortedtpicks = array(self.tpicks[i])[xinds]
                    sortederrpicks = array(self.errpicks[i])[xinds]
                    ax.plot(sortedxpicks,sortedtpicks, '-o', label = self.stNames[i])
                    # ax.errorbar(sortedxpicks,sortedtpicks, yerr=sortederrpicks, marker='o', linestyle='-',label = self.stNames[i])
                    ax.scatter(self.sources[i], self.sources[i]*0, marker = "*", s = 150, zorder = 99)

                ax.invert_yaxis()
                ax.legend(loc="best")
                fig.canvas.draw_idle()
                ttWindow.tkraise()

    def appVelMode(self):

        if self.sts:

            if self.velMode == False:

                if self.pickMode: self.pick()

                self.statusLabel.configure(text="Apparent velocity mode enabled!",font=("Arial", 11))
                # messagebox.showinfo(title="Refrapick", message="Apparent velocity mode enabled")
                print("Refrapick: Apparent velocity mode enabled!")

                self.velLines = []
                self.velTexts = []
                self.velLine = None
                self.xvelLine = []
                self.tvelLine = []

                for i in range(len(self.sts)):

                    def click(event):

                        if event.button == 1:

                            self.clickon = True
                            x = min(self.receiverPositions[i], key = lambda x: abs(event.xdata - x))
                            self.velLine, = self.axs[self.currentSt].plot(x,event.ydata,c="b",ls="--",lw=.7)
                            self.xvelLine = [x]
                            self.tvelLine = [event.ydata]
                            self.velLines.append(self.velLine)

                    def move(event):

                        if self.clickon:

                            self.xvelLine.append(event.xdata)
                            self.tvelLine.append(event.ydata)
                            self.velLine.set_data(self.xvelLine,self.tvelLine)
                            self.figs[self.currentSt].canvas.draw_idle()
                            del self.xvelLine[1:-1]
                            del self.tvelLine[1:-1]
                            self.clickon = True

                    def release(event):

                        if self.clickon:

                            x = min(self.receiverPositions[i], key = lambda x: abs(event.xdata - x))

                            if self.xvelLine[0] < x:

                                f = interp1d([self.xvelLine[0],x],[self.tvelLine[0],event.ydata], kind = "linear")
                                xarray2vel = [j for j in self.receiverPositions[i] if j >= self.xvelLine[0] and j <= x]

                            else:

                                f = interp1d([x,self.xvelLine[0]],[event.ydata,self.tvelLine[0]], kind = "linear")
                                xarray2vel = [j for j in self.receiverPositions[i] if j >= x and j <= self.xvelLine[0]]

                            tarray2vel = f(xarray2vel)
                            self.velLine.set_data(xarray2vel,tarray2vel)
                            m, b = polyfit(xarray2vel,tarray2vel, 1)
                            txt = self.axs[self.currentSt].text(xarray2vel[0],tarray2vel[0],"%d m/s"%(abs(1/m)), backgroundcolor = "w")
                            self.velTexts.append(txt)
                            self.clickon = False
                            self.figs[self.currentSt].canvas.draw_idle()

                    self.clickon = False
                    conClick = self.figs[i].canvas.mpl_connect('button_press_event', click)
                    conMove = self.figs[i].canvas.mpl_connect('motion_notify_event', move)
                    conRelease = self.figs[i].canvas.mpl_connect('button_release_event', release)
                    self.velConnections[i][0] = conClick
                    self.velConnections[i][1] = conMove
                    self.velConnections[i][2] = conRelease
                    self.velMode = True

            else:

                for i in range(len(self.sts)):

                    for l in self.velLines: l.remove()
                    for t in self.velTexts: t.remove()
                    del self.velLines[:]
                    del self.velTexts[:]
                    del self.xvelLine[:]
                    del self.tvelLine[:]
                    self.clickon = False
                    for con in self.velConnections[i]: self.figs[i].canvas.mpl_disconnect(con)
                    self.velConnections[i][0] = False
                    self.velConnections[i][1] = False
                    self.velConnections[i][2] = False
                    self.figs[i].canvas.draw_idle()

                self.velMode = False
                self.statusLabel.configure(text="Apparent velocity mode disabled!",font=("Arial", 11))
                # messagebox.showinfo(title="Refrapick", message="Apparent velocity mode disabled!")
                print("Refrapick: Apparent velocity mode disabled!")

app = Refrapick()
app.mainloop()
