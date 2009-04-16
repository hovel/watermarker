import Tkinter as Tk
import tkFileDialog
import os, sys, time
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance
except:
    import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance


class pwm:
    """Begin a Tkinter-based application"""
    # ------- INLINE CONFIG (DEFAULT VALUES)-------
    TEXT = 'marketing-research.ru'
    FONT_SIZE = 25
    FONT_SCALE = 0.05
    # ------------------
    def __init__(self, root):
        """initializer for Tkinter-based application"""
        self.root=root
        self.root.title("Picture WaterMarker")
        NoticeFrame = Tk.Frame(self.root)
        NoticeFrame.pack()
        headertext = u"""
        Picture Watermarker
        \U000000A9 2009 Zhukov Pavel
        """
        Tk.Label(NoticeFrame,text=headertext).pack()
        ButtonFrame = Tk.Frame(self.root)
        ButtonFrame.pack()       
        SelButton = Tk.Button(ButtonFrame, 
            text="Select Directory", command=self.select)
        SelButton.pack(side="left")
        QuitButton = Tk.Button(ButtonFrame, text="Quit", 
            command=self.quit)
        QuitButton.pack(side="left")

        OptionsFrame = Tk.Frame(self.root)
        OptionsFrame.pack()
        self.EXIFvar = Tk.IntVar()
        self.EXIFvar.set(1)
        self.EXIFCheckbox = Tk.Checkbutton(
            OptionsFrame,
            text="Preserve EXIF (requires JHead)",
            variable = self.EXIFvar)
        self.EXIFCheckbox.pack(side="top")
        self.Progressvar = Tk.IntVar()        
        self.ProgressCheckbox = Tk.Checkbutton(
            OptionsFrame,
            text="Show progress",
            variable = self.Progressvar)
        self.ProgressCheckbox.pack(side="left")
               
        self.StatusFrame = Tk.Frame(self.root)
        self.StatusFrame.pack()
        self.ImageLabel = Tk.Label(self.StatusFrame)
        self.ImageLabel.pack()
        self.FilenameLabel = Tk.Label(self.StatusFrame)
        self.FilenameLabel.pack()
        self.ProgressCheckbox.toggle()

    def select(self):
        dirname = tkFileDialog.askdirectory()
        if dirname != '':
            os.path.walk(dirname, self.process_files, None)
            print "PROCESSING COMPLETED.  SELECT MORE FILES OR QUIT."
        else:
            print "NO DIRECTORY SELECTED."
        return
    
    def quit(self):
        print "EXITING."
        sys.exit()

    def process_files(self, junk, dirpath, namelist):
        for filename in namelist:
            marked_filename = self.getmarkedfilename(filename)
            if marked_filename is not None:
                if os.path.isfile(os.path.join(dirpath,marked_filename)):
                    print "FILE EXISTS, SKIPPING:", marked_filename
                else:
                    self.updatestatus(dirpath, filename)
                    try:
                        watermark_dyn_size(dirpath, filename, marked_filename, self.TEXT, self.FONT_SCALE)
                        print('Watermarking successful: %s' % filename )
                    except:
                        raise
                        print('Something is wrong while watermarking: %s' % filename )
                    
    def updatestatus(self,dirpath,filename):
        im=Image.open(os.path.join(dirpath, filename))
        print time.asctime(), "thumbnailing...", filename, im.mode, im.size
        im.thumbnail((100,75))
        print time.asctime(), "showing...", filename, im.mode, im.size
        #im.show()
        self.Tkimage = ImageTk.PhotoImage(im)
        print "created"
        self.ImageLabel.config(image=self.Tkimage)
        self.ImageLabel.pack()
        self.FilenameLabel.config(text=filename)
        self.FilenameLabel.pack()
        self.StatusFrame.pack()
        self.root.update()
    def getmarkedfilename(self, filename):
        fn, ft = os.path.splitext(filename)
        if ft.upper() in [".JPG", ".JPEG", ".PNG"] and \
               not (fn.upper().endswith("-MARKED")):
            return fn + "-marked" + ft
        else:
            return None

def watermark_fix_size(dirpath, original_filename, new_filename, text, font_size=25, font_name='tahoma.ttf', color=(0,0,0)):
    full_original_filename = os.path.join(dirpath, original_filename)
    full_new_filename = os.path.join(dirpath, new_filename)
    im = Image.open(full_original_filename)
    im0 = watermarkit(im, text, font_size, font_name)
    im0.save(full_new_filename)
    return text

def watermark_dyn_size(dirpath, original_filename, new_filename, text, font_scale=0.05, font_name='tahoma.ttf', color=(0,0,0)):
    full_original_filename = os.path.join(dirpath, original_filename)
    full_new_filename = os.path.join(dirpath, new_filename)
    im = Image.open(full_original_filename)
    width, height = im.size
    font_size = int(font_scale*height)
    im0 = watermarkit(im, text, font_size, font_name)
    im0.save(full_new_filename)
    return text

    
def watermarkit(image, text, font_size=90, font_name = 'tahoma.ttf', color=(0,0,0)):
    font=ImageFont.truetype(font_name, font_size)
    im0 = Imprint(image, text, font=font, opacity=0.6, color=color)
    return im0

def GetFileDate(file):
    """
    Returns the date associated with a file.
    For JPEG files, it will use the EXIF data, if available
    """
    try:
        import EXIF
        # EXIF.py from http://home.cfl.rr.com/genecash/digital_camera.html
        f = open(file, "rb")
        tags = EXIF.process_file(f)
        f.close()
        return str(tags['Image DateTime'])
    except (KeyError, ImportError):
        # EXIF not installed or no EXIF date available
        import os.path, time
        return time.ctime(os.path.getmtime(file))

def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """

    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def Imprint(im, inputtext, font=None, color=None, opacity=.6, margin=(30,30)):
    """
    imprints a PIL image with the indicated text in lower-right corner
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    textlayer = Image.new("RGBA", im.size, (0,0,0,0))
    textdraw = ImageDraw.Draw(textlayer)
    textsize = textdraw.textsize(inputtext, font=font)
    textpos = [im.size[i]-textsize[i]-margin[i] for i in [0,1]]
    textdraw.text(textpos, inputtext, font=font, fill=color)
    if opacity != 1:
        textlayer = ReduceOpacity(textlayer,opacity)
    return Image.composite(textlayer, im, textlayer)
        
            
root = Tk.Tk()
myapp = pwm(root)
root.mainloop()

