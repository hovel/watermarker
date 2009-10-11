#!/usr/bin/env python
# vim:fileencoding=utf-8
# ---------------------------------------
from Tkinter import *
import tkMessageBox
import tkFileDialog
import os, sys, time
import pyexiv2
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance
except:
    import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance


class pwm(Frame):
    """Begin a Tkinter-based application"""
    # ------- INLINE CONFIG (DEFAULT VALUES)-------
    DTEXT = 'marketing-research.ru'
    DFONT_SIZE = 25
    DFONT_SCALE = '5%'
    # ------------------
    def __init__(self, master=None):
        """initializer for Tkinter-based application"""
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        
    def createWidgets(self):
        self.title = "Picture WaterMarker"
        # Header Text
        headertext = u"""
        Picture Watermarker
        \U000000A9 2009 Zhukov Pavel
        """
        Header=Label(self,text=headertext,)
        Header.grid(row=0, column=0, columnspan=2)
        #Text
        Label(self, text = "Text:").grid(row=1, column=0, sticky=N+E+S+W)
        self.Text = Entry(self)
        self.Text.grid(row=1, column=1, sticky=N+E+S+W, pady=5)
        self.Text.insert(0,self.DTEXT)
        #Font Size
        Label(self, text = '% of image\n or font size:').grid(row=2, column=0, sticky=N+E+S+W)
        self.Size = Entry(self)
        self.Size.grid(row=2, column=1, sticky=N+E+S+W, pady=10)
        self.Size.insert(0,self.DFONT_SCALE)
        #Buttons
        self.Doit = Button(self, text=u"Select Directory (Watermark)", command=self.select)
        self.Doit.grid(row=4, column=0, columnspan=2, sticky=N+E+S+W)
        self.Save =Button(self, text="Save settings", command=self.save)
        self.Save.grid(row=5, column=0, sticky=N+E+S+W)
        self.Quit = Button (self, text="Quit", command=self.quit )
        self.Quit.grid(row=5, column=1, sticky=N+E+S+W)
        #Preview
        self.ImageLabel = Label(self)
        self.ImageLabel.grid(row=6, column=0,columnspan=2, sticky=N+E+S+W)
        self.FilenameLabel = Label(self)
        self.FilenameLabel.grid(row=7, column=0,columnspan=2, sticky=N+E+S+W)
    def save(self):
        pass
    def select(self):
        #Prepare:
        sfont = self.Size.get()
        if '%' in sfont:
            self.Type = 'scale'
            try:
                self.FONT_SCALE = int(sfont[:-1])/100.
            except:
                tkMessageBox.showerror('Error','Wrong font scale')
                return 
        else:
            self.Type = 'size'
            try:
                self.FONT_SIZE = int(sfont)
            except:
                tkMessageBox.showerror('Error','Wrong font size')
                return 
        
        dirname = tkFileDialog.askdirectory()
        if dirname != '':
            os.path.walk(dirname, self.process_files, None)
            tkMessageBox.showinfo('Info', 'PROCESSING COMPLETED.  SELECT MORE FILES OR QUIT.')
        else:
            tkMessageBox.showerror('Error',"NO DIRECTORY SELECTED.")
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
                        if self.Type == 'scale':
                            watermark_dyn_size(dirpath, filename, marked_filename, self.Text.get(), self.FONT_SCALE)
                        else:
                            watermark_fix_size(dirpath, filename, marked_filename, self.Text.get(), self.FONT_SIZE)
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
        #self.ImageLabel.pack()
        self.FilenameLabel.config(text=filename)
        #self.FilenameLabel.pack()
        #self.pack()
        self.master.update()
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
    e = jpeg.getExif(open(full_original_filename,'rb'))
    im = Image.open(full_original_filename)
    im0 = watermarkit(im, text, font_size, font_name)
    im0.save(full_new_filename)
    jpeg.setExif(e, open(full_new_filename,'wb'))
    return text

def watermark_dyn_size(dirpath, original_filename, new_filename, text, font_scale=0.05, font_name='tahoma.ttf', color=(0,0,0)):
    full_original_filename = os.path.join(dirpath, original_filename)
    full_new_filename = os.path.join(dirpath, new_filename)
    
    im = Image.open(full_original_filename)
    width, height = im.size
    font_size = int(font_scale*height)
    im0 = watermarkit(im, text, font_size, font_name)
    im0.save(full_new_filename)
    try:
        im = pyexiv2.Image(full_original_filename)
        im.readMetadata()
        im2 = pyexiv2.Image(full_new_filename)
        im2.readMetadata()
        copyMetadataTo(im,im2)
        im2.writeMetadata()
        #im2 = pexif.JpegFile.fromFile(full_new_filename)
        #im2._segments.insert(0, e1)
        #im2.writeFile('test.jpeg')
    except:
        raise
    return text

def copyMetadataTo(srcImage, destImage):
    for key in srcImage.exifKeys():
        try:
            if ('Photo' in key) or ('Image' in key):
                print(key)
                destImage[key] = srcImage[key]
            else:
                print('no: %s' % key)
        except:
            print('error')
    for key in srcImage.iptcKeys():
        try:
            destImage[key] = srcImage[key]
        except:
            pass

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
        import EXIFL
        # EXIF.py from http://home.cfl.rr.com/genecash/digital_camera.html
        f = open(file, "rb")
        tags = EXIFL.process_file(f)
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

def Imprint(im, inputtext, font=None, color=None, opacity=0.6, margin=(30,30)):
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
        
if __name__ == '__main__':
    watermarker = pwm()
    watermarker.mainloop()

