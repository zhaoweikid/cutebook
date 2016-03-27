# coding: utf-8
import sys, string, os, types
basepath = os.path.dirname(os.path.abspath(sys.argv[0]))
import pygame, locale, types, pickle, time, math, traceback
from pygame.locals import *
from logger import logfile, charset
import netbook

VERSION = 'CuteBook 1.0'

class FilePanel:
    DIR_CHANGE_UP   = 1
    DIR_CHANGE_DOWN = 2
    DIR_CHANGE_NOW  = 3
    DIR_CHANGE_NO   = 4
    def __init__(self, win, font, fontsize):
        self.window = win
        self.window_size = win.get_size()
        #print 'win size:', self.window_size
        self.font_size   = fontsize
        self.font = font
        self.sf = pygame.Surface(self.window_size)

        self.current_path = os.getcwd()
        self.linehi = self.font_size + 5
        self.fileline = (self.window_size[1] / self.linehi) - 1

        self.path_sf = pygame.Surface((self.window_size[0], self.linehi))
        #self.file_sf = pygame.Surface((self.window_size[0], self.window_size[1] - self.linehi)) 
        self.file_sf = None
        self.content_sf = pygame.Surface((self.window_size[0], self.window_size[1] - self.linehi)) 

        self.cursor_sf = pygame.Surface((self.font_size, self.font_size))
        self.cursor_sf.fill((255, 0, 0))

        self.cursor_pos = 0

        self.display_files = []
        self.dir_changed = True
 
        # 显示的滑动窗口
        self.scroll_win = [0, self.fileline]

        self.lastdir = ''
        
        self.win_drives = []
        if sys.platform.startswith('win'):
            import win32api
            self.win_drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]

    def display(self):
        #print 'display file panel'
        self.sf.fill((0,0,0))
        self.content_sf.fill((0,0,0))
        self.draw_path()
        self.draw_files()
        self.draw_cursor()
        
        self.window.blit(self.sf, self.sf.get_rect())

    def draw_path(self):
        textsf  = self.font.render(u'文件路径: ' + self.current_path, 1, (255,0,0))
        textpos = textsf.get_rect()
        
        self.sf.blit(textsf, self.sf.get_rect())

    def draw_files(self):
        if self.dir_changed != self.DIR_CHANGE_NO:
            # 获取到需要显示的目录和文件
            if self.current_path == '' and self.win_drives:
                files = self.win_drives
            else:
                files = os.listdir(self.current_path)
            self.display_files = []

            for filename in files:
                #print 'filename:', filename
                fpath = os.path.join(self.current_path, filename)
                if not filename.startswith('.') and os.path.isdir(fpath):
                    if filename.endswith(':\\'):
                        newfilename = filename
                    else:
                        newfilename = filename + '/'
                    if type(filename) != types.UnicodeType:
                        self.display_files.append(unicode(newfilename, charset))
                    else:
                        self.display_files.append(newfilename)
                else:
                    if filename.lower().endswith('.txt'):
                        if type(filename) != types.UnicodeType:
                            self.display_files.append(unicode(filename, charset))
                        else:
                            self.display_files.append(filename)
            num = len(self.display_files)
            if num > 0: 
                self.file_sf = pygame.Surface((self.window_size[0], self.linehi * num))
            else:
                self.file_sf = pygame.Surface(self.window_size)
                self.file_sf.fill((0,0,0))
        
            area = pygame.Rect(self.font_size + 20, 0, self.window_size[0], self.linehi)
            for i in range(0, len(self.display_files)):
                x = self.display_files[i]
                textsf  = self.font.render(x, 1, (255,0,0))
                textpos = textsf.get_rect()
                area.top = i * self.linehi
                self.file_sf.blit(textsf, area, textpos)
            
            #self.content_sf.blit(self.file_sf, self.content_sf.get_rect())
            if self.dir_changed == self.DIR_CHANGE_UP and self.lastdir:
                try:
                    pos = self.display_files.index(self.lastdir+'/')
                    #print 'file pos:', pos
                except:
                    logfile.info('nof found dir name:', self.lastdir)
                else:
                    self.cursor_pos = pos
                    if self.cursor_pos >= self.scroll_win[1]:
                        scrollnum = self.cursor_pos / self.fileline 
                        self.scroll_win[0] = scrollnum * self.fileline
                        self.scroll_win[1] = self.scroll_win[0] + self.fileline
            self.dir_changed = self.DIR_CHANGE_NO
        
        area = pygame.Rect(0, self.scroll_win[0] * self.linehi, 
                        self.window_size[0], self.scroll_win[1] * self.linehi)
        self.content_sf.blit(self.file_sf, self.content_sf.get_rect(), area)

        area = pygame.Rect(0, self.linehi, self.window_size[0], self.window_size[1] - self.linehi)
        self.sf.blit(self.content_sf, area, self.content_sf.get_rect())

    def draw_cursor(self):
        area = (10, (self.cursor_pos - self.scroll_win[0]) * self.linehi + self.linehi, self.linehi, self.linehi)
        self.sf.blit(self.cursor_sf, area, self.cursor_sf.get_rect())
        
    def get_value(self):
        logfile.info('path:', self.current_path, 'pos:', self.cursor_pos, 'display_files:', len(self.display_files))
        if len(self.display_files) == 0:
            return ''
        return os.path.join(self.current_path, self.display_files[self.cursor_pos])


    def dir_up(self):
        if self.current_path.endswith(':\\') and self.win_drives:
            self.lastdir = self.current_path
            self.current_path = ''
        else:
            self.lastdir = os.path.basename(self.current_path)
            self.current_path = os.path.dirname(self.current_path)
        self.dir_changed = True
        self.cursor_pos = 0
        self.scroll_win = [0, self.fileline]

    def dir_down(self, name):
        logfile.info('dir name:', name)
        self.current_path = os.path.join(self.current_path, name.strip('/'))
        self.dir_changed = True
        self.cursor_pos = 0
        self.scroll_win = [0, self.fileline]

    def event(self, evt):
        #print 'cursor:', self.cursor_pos, len(self.display_files), self.scroll_win
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_UP:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    if self.cursor_pos < self.scroll_win[0]:
                        self.scroll_win[0] -= 1
                        self.scroll_win[1] -= 1
            elif evt.key == pygame.K_DOWN:
                if self.cursor_pos < len(self.display_files) - 1:
                    self.cursor_pos += 1
                    if self.cursor_pos >= self.scroll_win[1]:
                        self.scroll_win[0] += 1
                        self.scroll_win[1] += 1
            elif evt.key == pygame.K_LEFT:
                self.dir_up()
            elif evt.key == pygame.K_RIGHT or \
                 evt.key == pygame.K_RETURN or evt.key == pygame.K_KP_ENTER:
                filepath = self.get_value()
                filename = os.path.basename(filepath.rstrip('/'))
                logfile.info('in dir:', filepath, filename)
                if filepath:
                    logfile.info('is filename:', os.path.join(self.current_path, filename))
                    if os.path.isfile(os.path.join(self.current_path, filename)):
                        return 'text'
                    netfile = os.path.join(self.current_path, filename, 'cutebook_index')
                    if os.path.isfile(netfile):
                        return 'netbook'
                    self.dir_down(filename)

        return None


class LogoPanel:
    def __init__(self, win, font, fontsize, fontpath):
        self.window = win
        self.window_size = win.get_size()
        self.font_size = fontsize
        self.font = font

        self.font_path = fontpath
        self.bigfont = pygame.font.Font(self.font_path, self.font_size * 2)
        
    def display(self):
        self.window.fill((0,0,0))
        textsf  = self.bigfont.render(VERSION, 1, (255,0,0))
        textpos = textsf.get_rect()
        textpos.centerx = self.window.get_rect().centerx        
        textpos.centery = self.window.get_rect().centery - self.font_size
        self.window.blit(textsf, textpos)

        authorsf = self.font.render('by: zhaoweikid', 1, (255, 0, 0))
        apos = authorsf.get_rect()
        apos.centerx = self.window.get_rect().centerx
        apos.centery = self.window.get_rect().centery + self.font_size * 2 - self.font_size
        self.window.blit(authorsf, apos)

        s = [u"<-(左方向键) 选择目录(目录选择中也用上下左右方向键)", 
             u"->(右方向键) 打开最近阅读",
             u"任何时候按 Esc键 结束程序"]
        for i in range(0, len(s)):
            helpsf = self.font.render(s[i], 1, (255, 0, 0))
            dstarea = pygame.Rect(10, self.window_size[1] - self.font_size - 5, 
                self.window_size[0], self.font_size)
            x = helpsf.get_rect()
            x.top = self.window_size[1] - (self.font_size + 5) * (len(s) - i)
            self.window.blit(helpsf, x)

    def event(self, evt):
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_LEFT:
                return 'file'
            elif evt.key == pygame.K_RIGHT:
                return 'text'
        return None

class TextPanel:
    # 显示下一页
    DISPLAY_NEXT = 1
    # 显示上一页
    DISPLAY_PREV = 2
    # 显示当前页
    DISPLAY_CURR = 3
    # 不改变当前显示
    DISPLAY_NO   = 4

    def __init__(self, win, font, fontsize):
        self.window = win
        self.window_size = win.get_size()
        self.font_size = fontsize
        self.font = font
        self.zone = pygame.Surface((200,200))
        
        # 行间距
        self.linesp = 5
        pygame.draw.rect(self.zone, (10, 10, 10), (0,0,200,200))
        # 每行显示的字数 
        self.linews = self.window_size[0] / self.font_size
        # 一屏显示的行数
        self.rows = self.window_size[1] / (self.font_size + self.linesp) - 1

        self.uprect = (self.window_size[0]-220, 20, 200,200)
        self.downrect = (self.window_size[0]-220, self.window_size[1]-220, 200,200)
        
        self.foot = pygame.Surface((self.font_size + self.linesp, self.window_size[1]))

        self.clear()
        
        self.book_history = self.load()

    def clear(self):
        # 文章内的字符偏移，用来生成行列表的时候使用
        self.startpos = 0
        # 当前行
        self.lineno = 0
        
        # 当前翻页动作
        self.display_cur = self.DISPLAY_CURR
         
        self.bookname = ''
        self.bookpath = ''
        # 文章内容
        self.lines = []

    def load(self):
        filename = os.path.join(basepath, 'cutebook_history')
        if not os.path.isfile(filename):
            return {}
        f = open(filename, 'r')
        s = f.read()
        f.close()
        x = pickle.loads(s)
        
        return x
        
    def dump(self):
        if not self.bookname:
            return
        filename = os.path.join(basepath, 'cutebook_history')
        
        self.book_history[self.bookname] = {'path':self.bookpath, 'lineno':self.lineno, 
                    'lasttime':int(time.time())}
        self.book_history['__lastbook'] = self.bookname
        
        s = pickle.dumps(self.book_history)
        f = open(filename, 'w')
        f.write(s)
        f.close()
        
    def is_in_rect(self, pos, rect):
        if rect[0] < pos[0] < rect[0] + rect[2] and \
           rect[1] < pos[1] < rect[1] + rect[3]:
            return True
        return False   
    
    def openbook(self, filename):
        self.bookpath = filename
        self.bookname = os.path.basename(filename)
        f = open(filename, 'r')
        s = f.read()
        f.close()
        
        self.content = unicode(s, 'gbk', 'ignore')
        s = None
        self.lines = []
        
        while True:
            if self.startpos >= len(self.content):
                break
            line = self.content[self.startpos:self.startpos + self.linews]
            pos = line.find('\n')
            if pos >= 0:
                s = line[:pos+1].strip()
                self.startpos += pos + 1
            else:
                s = line
                self.startpos += self.linews
            self.lines.append(s)    

        #print 'history:', self.book_history, 'check:', filename, 'rows:', self.rows
        if self.book_history.has_key(self.bookname):
            x = self.book_history[self.bookname]
            self.lineno = x['lineno']

        self.content = None
        self.display_cur = self.DISPLAY_CURR

    def draw_foot(self):
        allpages = math.ceil(float(len(self.lines)) / self.rows)
        if allpages == 0:
            allpages = 1
        page = math.ceil(float(self.lineno) / self.rows) + 1
        rate = round(float(page)/allpages, 2) * 100
        s1 = u"%d-%02d-%02d %02d:%02d:%02d " % time.localtime()[:6]
        s2 = u"页数:%d/%d 已阅读:%d%% " % (page, allpages, rate)
        s = s1 + s2
        #print 'foot:', s
        self.foot.fill((0,0,0))
        textsf  = self.font.render(s, 1, (150,150,150))
        
        area = pygame.Rect(0, (self.font_size + self.linesp) * (self.rows), 
                    self.window_size[0], self.font_size+self.linesp)
        self.window.fill((0,0,0), area)
        self.window.blit(textsf, area, textsf.get_rect())

    def display(self):        
        if self.display_cur != self.DISPLAY_NO:            
            if self.display_cur == self.DISPLAY_PREV:
                self.lineno -= self.rows
                if self.lineno < 0:
                    self.lineno = 0
            elif self.display_cur == self.DISPLAY_NEXT:
                self.lineno += self.rows
                if self.lineno >= len(self.lines):
                    self.lineno -= self.rows
            
            self.window.fill((0,0,0))
            
            #self.window.blit(self.zone, pygame.Rect(self.uprect[0], self.uprect[1], self.uprect[2], self.uprect[3]))
            #self.window.blit(self.zone, pygame.Rect(self.downrect[0], self.downrect[1], self.downrect[2], self.downrect[3]))
            # 接下来要显示的行数 
            count = min(self.rows, len(self.lines) - self.lineno)
            for i in range(0, count):
                s = self.lines[self.lineno + i]        
                textsf  = self.font.render(s, 1, (255,255,255))
                textpos = textsf.get_rect()
                textpos.top += i * (self.font_size + self.linesp)
                self.window.blit(textsf, textpos)
            self.display_cur = self.DISPLAY_NO
    
            self.draw_foot()


    def event(self, event):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.display_cur = self.DISPLAY_NEXT
            elif event.key == pygame.K_UP:
                self.display_cur = self.DISPLAY_PREV
            elif event.key == pygame.K_DOWN:
                self.display_cur = self.DISPLAY_NEXT
            elif event.key == pygame.K_LEFT:
                self.dump()
                self.clear()
                return 'file'
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()                  
            if self.is_in_rect(pos, self.uprect):
                self.display_cur = self.DISPLAY_PREV
            elif self.is_in_rect(pos, self.downrect):
                self.display_cur = self.DISPLAY_NEXT

        return None

class NetbookPanel:
    # 显示下一页
    DISPLAY_NEXT = 1
    # 显示上一页
    DISPLAY_PREV = 2
    # 显示当前页
    DISPLAY_CURR = 3
    # 不改变当前显示
    DISPLAY_NO   = 4

    def __init__(self, win, font, fontsize):
        self.window = win
        self.window_size = win.get_size()
        self.font_size = fontsize
        self.font = font
        self.zone = pygame.Surface((200,200))
        
        # 行间距
        self.linesp = 5
        pygame.draw.rect(self.zone, (10, 10, 10), (0,0,200,200))
        # 每行显示的字数 
        self.linews = self.window_size[0] / self.font_size
        # 一屏显示的行数
        self.rows = self.window_size[1] / (self.font_size + self.linesp) - 1
        
        self.content_size = self.window_size[1] - (self.font_size + self.linesp)
        self.uprect = (self.window_size[0]-220, 20, 200,200)
        self.downrect = (self.window_size[0]-220, self.window_size[1]-220, 200,200)
        
        self.foot = pygame.Surface((self.font_size + self.linesp, self.window_size[1]))

        self.clear()
        self.chapter_pos = 0
        
    def clear(self):
        # 当前行
        self.lineno = 0
        
        # 当前翻页动作
        self.display_cur = self.DISPLAY_CURR
         
        self.bookname = ''
        self.bookpath = ''
        # 文章内容
        self.lines = []

        self.book_index = None
        self.lastchapter = ''

        self.imagesf = []
        self.imagerect = pygame.Rect(0, 0, self.window_size[0], self.window_size[1])
        self.image_pos = 0

    def dump(self):
        if not self.bookname or not self.lastchapter:
            return
        filename = os.path.join(self.bookpath, 'cutebook_index')
        self.book_index['lastchapter'] = self.lastchapter
        
        s = pickle.dumps(self.book_index)
        f = open(filename, 'w')
        f.write(s)
        f.close()
        
    def is_in_rect(self, pos, rect):
        if rect[0] < pos[0] < rect[0] + rect[2] and \
           rect[1] < pos[1] < rect[1] + rect[3]:
            return True
        return False   
    
    def openbook(self, dirname):
        self.clear()

        self.bookpath = dirname
        filename = os.path.join(dirname, 'cutebook_index').encode(charset)

        f = open(filename, 'r')
        s = f.read()
        f.close()
        self.book_index = pickle.loads(s)

        self.bookname = self.book_index['name']
        self.lastchapter = self.book_index['lastchapter']
        
        if not self.lastchapter and len(self.book_index['chapterlist']) > 0:
            self.lastchapter = self.book_index['chapterlist'][0][0]
        logfile.info('lastchapter:', self.lastchapter)
        
        chlist = self.book_index['chapterlist']
        for i in range(0, len(chlist)):
            x = chlist[i]
            if x[0] == self.lastchapter:
                self.chapter_pos = i
                break
        
        self.openchapter()

    def openchapter(self):
        chlist = self.book_index['chapterlist']
        if len(chlist) == 0:
            return
        if self.chapter_pos >= len(chlist):
            return
        chapter = chlist[self.chapter_pos]
        cns = chapter[1]

        self.imagesf = []
        for x in cns:
            logfile.info('open chapter:', x)
            if x.endswith('.txt'):
                self.openchapter_txt(x)
            else:
                self.openchapter_img(x)
        self.chapter_pos += 1 
        self.lastchapter = chapter[0]
        
        self.display_cur = self.DISPLAY_CURR

    def openchapter_txt(self, filename):
        self.imagesf = []
        self.imagerect.top = 0

        #filename = os.path.join(self.bookpath, name)
        f = open(filename, 'r')
        s = f.read()
        f.close()

        self.content = unicode(s, 'gbk', 'ignore')
        s = None
        self.lines = []
        
        startpos = 0
        while True:
            if startpos >= len(self.content):
                break
            line = self.content[startpos:startpos + self.linews]
            pos = line.find('\n')
            if pos >= 0:
                s = line[:pos+1].strip()
                startpos += pos + 1
            else:
                s = line
                startpos += self.linews
            self.lines.append(s)    

        self.lineno = 0
        self.content = None
        #self.display_cur = self.DISPLAY_CURR


    def openchapter_img(self, filename):
        isf = pygame.image.load(filename)
        self.imagesf.append(isf)
        self.imagerect.top = 0
        self.image_pos = 0


    def draw_foot(self):
        allchapters = len(self.book_index['chapterlist'])
        if allchapters == 0:
            rate = 0
        else:
            rate = round(float(self.chapter_pos)/allchapters, 2) * 100
        s1 = u"%d-%02d-%02d %02d:%02d:%02d " % time.localtime()[:6]
        s2 = u"章数:%d/%d 已阅读:%d%% " % (self.chapter_pos, allchapters, rate)
        s = s1 + s2
        #print 'foot:', s
        self.foot.fill((0,0,0))
        textsf  = self.font.render(s, 1, (150,150,150))
        
        area = pygame.Rect(0, (self.font_size + self.linesp) * (self.rows), 
                    self.window_size[0], self.font_size+self.linesp)
        self.window.fill((0,0,0), area)
        self.window.blit(textsf, area, textsf.get_rect())

    def display(self):
        if self.imagesf:
            self.display_image()
        else:
            self.display_txt()

    def display_txt(self):        
        if self.display_cur != self.DISPLAY_NO:            
            if self.display_cur == self.DISPLAY_PREV:
                self.lineno -= self.rows
                if self.lineno < 0:
                    self.lineno = 0
            elif self.display_cur == self.DISPLAY_NEXT:
                self.lineno += self.rows
                if self.lineno >= len(self.lines):
                    self.lineno -= self.rows
            
            self.window.fill((0,0,0))
            
            # 接下来要显示的行数 
            count = min(self.rows, len(self.lines) - self.lineno)
            for i in range(0, count):
                s = self.lines[self.lineno + i]        
                textsf  = self.font.render(s, 1, (255,255,255))
                textpos = textsf.get_rect()
                textpos.top += i * (self.font_size + self.linesp)
                self.window.blit(textsf, textpos)
            self.display_cur = self.DISPLAY_NO
    
            self.draw_foot()

    def display_image(self):
        logfile.info('image pos:', self.image_pos)
        if self.image_pos >= len(self.imagesf):
            return

        if self.display_cur != self.DISPLAY_NO:            
            self.window.fill((233,250,255))
            if self.display_cur == self.DISPLAY_PREV:
                self.imagerect.top -= self.content_size
                if self.imagerect.top < 0:
                    self.imagerect.top = 0
                isf = self.imagesf[self.image_pos]
                self.window.blit(isf, isf.get_rect(), self.imagerect)
            elif self.display_cur == self.DISPLAY_NEXT:
                self.imagerect.top += self.content_size
                iheight = self.imagesf[0].get_height()
                if self.imagerect.top >= iheight: 
                    self.image_pos += 1
                    self.imagerect.top = 0
                    if self.image_pos >= len(self.imagesf):
                        return

                isf = self.imagesf[self.image_pos]
                self.window.blit(isf, isf.get_rect(), self.imagerect)
            else:
                isf = self.imagesf[self.image_pos]
                self.window.blit(isf, isf.get_rect(), self.imagerect)
               
            

            self.display_cur = self.DISPLAY_NO
    
            self.draw_foot()
    
    def draw_update(self, num, count, name):
        self.window.fill((0,0,0)) 
        s = '%d/%d %s' % (count, num, name)

        textsf  = self.font.render(s, 1, (150,150,150))
        textpos = textsf.get_rect()
        textpos.centerx = self.window.get_rect().centerx        
        textpos.centery = self.window.get_rect().centery - self.font_size
        self.window.blit(textsf, textpos)
        
        pygame.display.update()

 

    def update(self):
        logfile.info('update ...')
        bookname = self.bookname
        self.dump()
        nb = netbook.NetBook(self.bookpath, self.draw_update)
        nb.download(bookname)

        self.openbook(self.bookpath)
        nb = None

    def event(self, event):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.display_cur = self.DISPLAY_NEXT
            elif event.key == pygame.K_UP:
                self.display_cur = self.DISPLAY_PREV
            elif event.key == pygame.K_DOWN:
                if (self.imagesf and self.image_pos >= len(self.imagesf) - 1) or \
                    (not self.imagesf and self.lineno + self.rows >= len(self.lines)):
                    self.openchapter()
                else:
                    self.display_cur = self.DISPLAY_NEXT
            elif event.key == pygame.K_LEFT:
                self.dump()
                self.clear()
                return 'file'
            elif event.key == pygame.K_RIGHT:
                self.update()
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()                  
            if self.is_in_rect(pos, self.uprect):
                self.display_cur = self.DISPLAY_PREV
            elif self.is_in_rect(pos, self.downrect):
                self.display_cur = self.DISPLAY_NEXT

        return None


class CuteBook:
    def __init__(self):
        pygame.init()
        if sys.platform.startswith('win'):
            self.window_size = (800, 480)
            self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        elif sys.platform == 'darwin':
            self.window_size = (800, 480)
            self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        else:
            f = open('/etc/issue', 'r')
            s = f.read()
            f.close()

            self.window_size = (800, 480)
            if s.find('maemo') >= 0:
                self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.NOFRAME)
            else:
                self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
                
        pygame.display.set_caption(VERSION)
        self.font_size = 20
        
        self.font_path = self.find_font()
        #print 'font_path:', self.font_path
        self.font = pygame.font.Font(self.font_path, self.font_size)

       
        self.panels = {'logo':LogoPanel(self.window, self.font, self.font_size, self.font_path), 
                       'file':FilePanel(self.window, self.font, self.font_size),
                       'text':TextPanel(self.window, self.font, self.font_size),
                       'netbook':NetbookPanel(self.window, self.font, self.font_size)}

        self.panel_pos = 'logo'

    def font_in_dir(self, checkdir):
        if os.path.isdir(checkdir):
            files = os.listdir(checkdir)
            for fname in files:
                if fname.endswith(('.ttc', '.ttf')):
                    return os.path.join(checkdir, fname)
        return ''
           
    def find_font(self):
        if sys.platform.startswith('win'):
            return 'C:\\WINDOWS\\Fonts\\simsun.ttc'
        elif sys.platform == 'darwin':
            return '/System/Library/Fonts/华文细黑.ttf'
        elif sys.platform.startswith('linux'):
            fontdir = '/usr/share/fonts'
            
            fopath = self.font_in_dir(os.path.join(fontdir, 'chinese'))
            if fopath:
                return fopath
            checkdir = os.path.join(fontdir, 'zh_CN')
            if os.path.isdir(checkdir):
                fopath = self.font_in_dir(os.path.join(checkdir, 'TrueType'))
                if fopath:
                    return fopath

        fopath = self.font_in_dir(os.path.join(os.getcwd(), 'fonts'))
        if fopath:
            return fopath

        raise IOError, 'not found chinese font' 
        
    def apply_event(self, event):
        if event.type == pygame.QUIT:
            self.apply_exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.apply_exit()

        newpanel = self.panels[self.panel_pos].event(event)        
        if newpanel:
            if newpanel == 'text':
                filename = self.panels['file'].get_value()
                #print 'openbook:', filename
                panel = self.panels[newpanel]
                if filename:
                    panel.openbook(filename)
                else:
                    #print 'lastbook:', panel.book_history['__lastbook']
                    panel.openbook(panel.book_history[panel.book_history['__lastbook']]['path'])

            elif newpanel == 'netbook':
                dirname = self.panels['file'].get_value()
                panel = self.panels[newpanel]
                if dirname:
                    panel.openbook(dirname)

            self.panel_pos = newpanel

    def apply_exit(self):
        self.panels['text'].dump()
        self.panels['netbook'].dump()
        sys.exit()

    def run(self):
        while True:
            self.panels[self.panel_pos].display()
            pygame.display.update()
            event = pygame.event.wait()
            self.apply_event(event)
            
def main():            
    try:
        cb = CuteBook()
        cb.run()
    except:
        traceback.print_exc(file=logfile.log)
                                                                        
if __name__ == '__main__':
    main()


