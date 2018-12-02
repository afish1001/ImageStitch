from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from functools import partial
import cv2 as cv
from PIL import Image
from lib import *
import operator
import sys

class GraphicsPixmapItem(QGraphicsPixmapItem):

    def __init__(self,pixmap):
        super(GraphicsPixmapItem, self).__init__(pixmap)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        self.prePos=self.pos()
    # def setSelected(self, bool):
    #     QGraphicsPixmapItem.setSelected(self,bool)
    #     if bool==True:
    #         self.prePos=self.pos()
    #         print('selected pos',self.prePos)
    # def mousePressEvent(self, ev):
    #     QGraphicsPixmapItem.mousePressEvent(self,ev)
    #     self.prePos=self.pos()
    # def mouseMoveEvent(self, ev):
    #     QGraphicsPixmapItem.mouseMoveEvent(self,ev)
    #     print(int(ev.buttons()))
    def parentWidget(self):
        return self.scene().views()[0]
    def contextMenuEvent(self, event):
        wrapped = []
        menu = QMenu(self.parentWidget())
        for text, param in (
                ("置于顶层", 'top'),
                ("置于底层", 'bottom'),
                ("上移一层", 'up'),
                ("下移一层", 'down'),):
            wrapper = partial(self.setLayer, param)
            wrapped.append(wrapper)
            menu.addAction(text, wrapper)
        menu.exec_(event.screenPos())
    def setLayer(self, param=None):
        list = self.scene().items()
        index = list.index(self)
        if index == 0:
            if param in ['up','top']:
                return
        if index == len(list)-1:
            if param in ['down','bottom']:
                return
        if param == 'up':
            list[index - 1].stackBefore(self)
        elif param == 'down':
            self.stackBefore(list[index+1])
        elif param == 'top':
            for i in list[::-1]:
                i.stackBefore(self)
        else:
            for i in list:
                self.stackBefore(i)
        self.scene().update()
        return

class GraphicsView(QGraphicsView):
    def __init__(self):
        super(GraphicsView, self).__init__()
        self.setDragMode(QGraphicsView.RubberBandDrag)#视图选择
        self.setRenderHint(QPainter.Antialiasing)#反走样
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # 视图仿射变换时，使用鼠标位置定位场景坐标eg使用鼠标位置作为缩放中心
        # self.setMouseTracking(True)
        # self.setRubberBandSelectionMode(Qt.ContainsItemShape)#rubberbandselect设置为包含模式
        self.zoom=1.0
        self.itemsMoving=False
    def wheelEvent(self, ev):
        mod=ev.modifiers()
        factor=ev.angleDelta().y()/120.0#一步15度，一度滑动8个单位距离
        if Qt.ControlModifier==int(mod):
            # print(int(mod))
            if factor>0:#放大
                factor=2
            elif self.zoom<0.01:
                return
            else:#缩小
                factor=0.5
            self.zoom = self.zoom * factor
            self.scale(factor,factor)
            pos = self.mapToScene(ev.pos())
            item=self.scene().itemAt(pos, QTransform())
            if item:
                self.ensureVisible(item)
        else:
            super(GraphicsView, self).wheelEvent(ev)
    def keyPressEvent(self, ev):
        key=ev.key()
        items=self.scene().selectedItems()
        if len(items):
            for item in items:
                if key==Qt.Key_Left:
                    # print('left')
                    item.moveBy(-1,0)
                elif key==Qt.Key_Right:
                    # print('right')
                    item.moveBy(1,0)
                elif key==Qt.Key_Up:
                    # print('up')
                    item.moveBy(0,-1)
                elif key==Qt.Key_Down:
                    # print('down')
                    item.moveBy(0,1)
        else:
            QGraphicsView.keyPressEvent(self,ev)
    # def mouseMoveEvent(self, ev):
    #     buttons=ev.buttons()
    #     QGraphicsView.mouseMoveEvent(self,ev)
    #     self.parentWidget().mouseMoveEvent(ev)
    #     pos = self.mapToScene(ev.pos())
    #     if buttons==Qt.LeftButton:#
    #         if self.scene().items():
    #             item = self.scene().itemAt(pos, QTransform())
    #             if item and item.isSelected():
    #                 # print('drag move')
    #                 self.itemsMoving=True
    #TODO
    def mouseReleaseEvent(self, ev):
        QGraphicsView.mouseReleaseEvent(self,ev)
        if self.itemsMoving:
            self.itemsMoving=False
            items=self.scene().selectedItems()
            # for item in items:
                # print(item.pos())
            # self.scene().clearSelection()

class ManualForm(QMainWindow):
    def __init__(self,filepath=None):
        super(QMainWindow,self).__init__()
        self.dirty=False#是否保存操作
        self.filepath=filepath#记录文件路径
        self.suffix='.jpg'#默认图片后缀
        self.nextPoint=QPoint()#下一张图片的位置
        self.undopoints=[]
        # self.setMouseTracking(True)
        self.dirs={
            '0':[-1,0],#左
            '1':[1,0], #右
            '2':[0,-1],#上
            '3':[0,1]  #下
        }
        self.dir=[-1,0]#新图片添加的方向
        self.view=GraphicsView()
        self.scene=QGraphicsScene(self)
        self.view.setScene(self.scene)
        #actions
        action=partial(newAction,self)#默认self为action的parent
        # new=action('New',self.newFile,icon='new',tip='打开新项目')
        # self.directionOps = QComboBox(self)
        # self.directionOps.addItems(['依次向左', '依次向右', '依次向上', '依次向下'])
        # directionMenu = newWidgetAction(self, self.directionOps)
        dirLabel=QLabel('默认新图片顺序：')
        dirLabel.setToolTip('新添加图片相对原始项目的方位')
        add=action('打开',self.addFile,icon='add',tip='添加图片')
        delete=action('删除',self.delete,'delete',icon='delete',tip='删除图片')
        upper = action('上移一层', self.layerUpper)
        lower = action('下移一层', self.layerLower)
        top = action('置于顶层', self.layerTop)
        bottom = action('置于底层', self.layerBottom)
        self.save = action('保存', self.saveFile, 'Ctrl+S', 'save', '保存项目')
        self.full = action("全屏", self.fullScreen, icon='fullScreen')
        self.normal = action('退出全屏', self.fullScreen, 'esc', icon='quit')
        self.undo=action('撤销',self.undoaction,"Ctrl+Z")
        self.tools=self.toolbar('Tools',[add,None,delete,None,self.save,None,upper,None,lower,None,top,None,bottom,None,self.full])
        self.addToolBar(Qt.TopToolBarArea, self.tools)
        #layout
        vbox=QVBoxLayout()
        vbox.addWidget(self.view)
        vbox.setContentsMargins(QMargins(0,0,0,0))
        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        self.resize(self.screenSize().width()/1.5,self.screenSize().height()/1.5)
        # signal-slot
        # self.directionOps.currentIndexChanged.connect(self.dirChanged)
        self.scene.changed.connect(self.conChange)
        self.setWindowTitle('材料显微图像拼接软件')
        self.setWindowIcon(newIcon('icon'))
    def dirChanged(self,s):
        self.dir=self.dirs[str(s)]
    def screenSize(self):
        screen=QDesktopWidget().screenGeometry()
        return screen
    def conChange(self,change):#content改变，dirty置为True
        # self.scene.clearSelection()
        # self.setDirty(True)
        pass
    def undoaction(self):
        pass
    # def mouseMoveEvent(self, e):#同上，但是这个思路不太好用
        # pos = self.view.mapToScene(e.pos())
        # # print('move')
        # if self.scene.items():
        #     item=self.scene.itemAt(pos,QTransform())
        #     if item and item.isSelected():
        #         # print('drag move')
        #         self.setDirty(True)
    def closeEvent(self,e):
        if not self.mayContinue():
            if not self.saveFile():
                e.ignore()
                return
        self.resetState()
        e.accept()
    def fullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.tools.removeAction(self.normal)
            self.tools.addAction(self.full)
        else:
            self.showFullScreen()
            self.tools.removeAction(self.full)
            self.tools.addAction(self.normal)
    def toolbar(self,title,actions=None):
        toolbar=QToolBar(title)
        layout=toolbar.layout()
        layout.setSpacing(8)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        palette=QPalette()
        palette.setColor(QPalette.Button,QColor(100,100,100,60))
        palette.setColor(QPalette.Background, QColor(50,50,50,60))
        toolbar.setAutoFillBackground(True)
        toolbar.setPalette(palette)
        toolbar.setFont(QFont(None,9))
        for action in actions:
            if isinstance(action,QWidget):
                toolbar.addWidget(action)
            elif action is None:
                toolbar.addSeparator()
            else:
                # btn=QToolButton()
                # btn.setDefaultAction(action)
                # btn.setToolButtonStyle(toolbar.toolButtonStyle())
                toolbar.addAction(action)#addWidget(btn)
        return toolbar
    def setDirty(self,dirty=True):
        self.dirty=dirty
        self.save.setEnabled(dirty)
    def resetState(self):
        self.scene.clearSelection()
        items=self.scene.items()
        while items:
            item=items.pop()
            self.scene.removeItem(item)
            del item
        self.setDirty(False)
        self.dir=[-1,0]
    def fitWindow(self):
        '''
        视口自适应大小，计算widget窗口与view的比例，缩放view。
        '''
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        # print('scene', self.scene.sceneRect(), 'itemsBoundingRect; ', self.scene.itemsBoundingRect())
        w1=self.view.width()#绘图区尺寸
        w2=self.scene.width()*self.view.zoom#view尺寸
        # print('窗口',w1,'view',w2)
        scale=w1/w2 if w1<w2 else 1
        self.view.zoom=self.view.zoom*scale
        self.view.scale(scale,scale)
    def position(self,w,h,dx=0,dy=0):
        rect = self.scene.itemsBoundingRect()
        print(rect)
        x, y = rect.x(),rect.y()#0.5是边界值
        if dx==0 and dy==0:
            if operator.eq(self.dir,self.dirs['0']):#水平向左
                self.nextPoint =QPointF(x-w+0.5,y+0.5)
            elif operator.eq(self.dir,self.dirs['1']):#水平向右
                self.nextPoint=QPointF(x+rect.width()-0.5,y+0.5)
            elif operator.eq(self.dir,self.dirs['2']):#垂直向上
                self.nextPoint = QPointF(x+0.5, y+0.5 - h)
            elif operator.eq(self.dir,self.dirs['3']):#垂直向下
                self.nextPoint = QPointF(x+0.5, y + rect.height()-0.5)
            else:
                self.nextPoint=QPointF(x-w,y+rect.height())#left bottom
        else:
           self.nextPoint+=QPointF(dx,dy)
        print('item point', self.nextPoint)
        return self.nextPoint
    def newFile(self):
        if not self.mayContinue():
            if not self.saveFile():
                return
        self.resetState()
        self.addFile()
    def addFile(self):
        images = self.openfileDialog()
        if not images:
            return
        self.scene.clearSelection()
        self.addImages(images)
    def addImages(self,images):
        #images[0]:(path,dx,dy)
        for image in images:
            # print(image)
            if isinstance(image,tuple):
                imageData = self.loadImage(image[0])
                dx=image[1]
                dy=image[2]
                if imageData:
                    pixmap = QPixmap.fromImage(imageData)
                    w = pixmap.width()
                    h = pixmap.height()
                    self.dir=[-1,1]
                    self.createPixmapItem(pixmap, self.position(w,h,dx=dx,dy=dy))
            else:
                imageData = self.loadImage(image)
                if imageData:
                    pixmap = QPixmap.fromImage(imageData)
                    w=pixmap.width()
                    h=pixmap.height()
                    self.createPixmapItem(pixmap, self.position(w,h))
        self.fitWindow()
    def openfileDialog(self):
        path=QFileInfo(self.filepath).path() if self.filepath else '.'
        formats=['*.{}'.format(fmt.data().decode()) for fmt in QImageReader.supportedImageFormats()]
        filters='Image (%s)'%' '.join(formats)
        images,_=QFileDialog.getOpenFileNames(self,
                                             'Choose Images',
                                              path,
                                              filters)
        return images
    def loadImage(self,filename):
        if not QFile.exists(filename):
            return False
        file=read(filename,None)
        imageData=QImage.fromData(file)
        if imageData.isNull():
            return False
        self.filepath = QFileInfo(filename).path() + '/'
        self.suffix = '.' + QFileInfo(filename).suffix()
        return  imageData
    def createPixmapItem(self,pixmap,position=None,transform=QTransform()):
        item=GraphicsPixmapItem(pixmap)
        item.setPos(position)
        item.setTransform(transform)
        self.scene.addItem(item)
        item.setSelected(True)
        self.setDirty(True)
        return item
    def delete(self):
        items=self.scene.selectedItems()
        if (len(items) and QMessageBox.question(self,
                  'Delete',
                   'Delete {0} image{1}?'.format(len(items),
                   's' if len(items)!=1 else ''),
                    QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes):
            while items:
                item=items.pop()
                self.scene.removeItem(item)
                del item
        if len(self.scene.items()):
            self.setDirty(True)
        else:
            self.setDirty(False)
        self.fitWindow()

        # def getItemIndex(self,item):
        # list1=self.scene.collidingItems(item)
        # list2=self.scene.collidingItems(list1[-1])
        # if list2[0]!=list1[0]:
        #     #item位于顶层
        #     return 0
        # list3=self.scene.collidingItems(list1[0])
        # index=list3.index(item)+1
        # print(index)
        # return index
    def layerUpper(self):
        items=self.scene.selectedItems()
        list=self.scene.items()
        for item in items:
            # list=self.scene.collidingItems(item)
            # if len(list)==0:
            #     return
            # elif len(list)==1:
            #     list[0].stackBefore(item)
            # else:
            #     index=self.getItemIndex(item)
            #     if index==0:
            #         return
            #     list[index-1].stackBefore(item)
            index=list.index(item)
            if index==0:#顶层
                return
            else:
                list[index-1].stackBefore(item)
        self.scene.update()
    def layerLower(self):
        items=self.scene.selectedItems()
        list = self.scene.items()
        for item in items:
            # list=self.scene.collidingItems(item)
            # if len(list)==0:
            #     return
            # elif len(list)==1:
            #     item.stackBefore(list[0])
            # else:
            #     index=self.getItemIndex(item)
            #     if index==len(list):
            #         return
            #     item.stackBefore(list[index])
            index=list.index(item)
            if index==len(list)-1:#底层
                return
            else:
                item.stackBefore(list[index+1])
        self.scene.update()
    def layerTop(self):
        items = self.scene.selectedItems()
        list = self.scene.items()
        for item in items:
            # list = self.scene.collidingItems(item)
            for i in list[::-1]:
                i.stackBefore(item)
        self.scene.update()
    def layerBottom(self):
        items = self.scene.selectedItems()
        list = self.scene.items()
        for item in items:
            # list = self.scene.collidingItems(item)
            for i in list:
                item.stackBefore(i)
        self.scene.update()
    def saveFile(self):
        if not self.dirty:#没有可保存的items
            return
        filename = self.saveFileDialog()
        if not filename:
            # print('no file to save ')
            return False
        self.filepath = QFileInfo(filename).path() + '/'
        try:
            print('save rect', self.scene.itemsBoundingRect(), self.scene.sceneRect())
            self.scene.setSceneRect(self.scene.itemsBoundingRect())  # 更新场景的矩形范围，保持和items的边界范围一致
            self.scene.clearSelection()
            #去除边框1px
            # x=self.scene.itemsBoundingRect().x()
            # y=self.scene.itemsBoundingRect().y()
            # w = self.scene.itemsBoundingRect().width()-1
            # h = self.scene.itemsBoundingRect().height()-1
            # image = QImage(w, h, QImage.Format_ARGB32)
            # p = QPainter(image)
            # p.begin(image)
            # # p.setRenderHint(QPainter.HighQualityAntialiasing)
            # # tmp_w=10000
            # # sum=int(w/tmp_w)
            # # i=0
            # # while i<sum:
            # #     self.scene.render(p,target=QRectF(i*tmp_w,0,tmp_w,h),source=QRectF(x+i*tmp_w,y,tmp_w,h))
            # #     print(x+i*tmp_w)
            # #     i+=1
            # # self.scene.render(p,target=QRectF(sum*tmp_w,0,w-sum*tmp_w,h),source=QRectF(x+sum*tmp_w,y,w-sum*tmp_w,h))
            # self.scene.render(p)
            # p.end()
            self.sthread = saveThread(self.scene,filename)
            self.sthread.start()
            # print(image.size())
            # img.save(filename)
            # image.save(filename)
            # self.view.setScene(self.scene)
            # print('save file ',self.scene.isActive(),self.scene.items())
            # self.setDirty(False)
        except IOError as e:
            QMessageBox.warning(self, "Save Error",
                                "Failed to save {0}: {1}".format(self.filename, e))
        return True
    def saveFileDialog(self):
        formats=['*.{}'.format(fmt.data().decode())
                   for fmt in QImageReader.supportedImageFormats()]
        filters = "Image (%s)" % ' '.join(formats)
        default_filename=self.filepath+'manual'+self.suffix
        i=1
        while QFile.exists(default_filename):
            default_filename=self.filepath+'manual_'+str(i)+self.suffix
            i=i+1
        filename, filetype = QFileDialog.getSaveFileName(
            self, 'Save File', default_filename,
            filters)
        return filename
    def mayContinue(self):
        return not (self.dirty and not self.discardChangesDialog())
    def discardChangesDialog(self):
        yes,no=QMessageBox.Yes,QMessageBox.No
        msg='图片未保存，是否保存'
        return no==QMessageBox.warning(self,'Attention',msg,yes|no)
if __name__ =='__main__':
    app=QApplication(sys.argv)
    form=ManualForm()
    form.show()
    sys.exit(app.exec_())