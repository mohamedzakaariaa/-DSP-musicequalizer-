def f(n):
    import pyqtgraph as pg
    pg.setConfigOption('background', '#a0f0ff')
    win = pg.GraphicsWindow()
    win_size = 1000
    win.setGeometry(500, 30, win_size, win_size)
    plt = win.addPlot()
    win.setUpdatesEnabled = False
    plt.setUpdatesEnabled = False
    y = range(n)
    x = range(n)
    plt.showGrid(x=True, y=True)
    empty_pen = pg.mkPen((0, 0, 0, 0))
    brush = pg.mkBrush((255, 255, 255))
    for i1 in range(n):
        for i0 in range(n):
            print("i1, i0 =", i1, i0)
            rect = pg.QtGui.QGraphicsRectItem(i0, i1, 0.5, 0.5)
            rect.setPen(empty_pen)
            rect.setBrush(brush)
            plt.addItem(rect)
    pg.QtGui.QApplication.exec_()

f(40)