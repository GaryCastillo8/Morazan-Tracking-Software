from matplotlib.backends.backend_qt5 import NavigationToolbar2QT

class Toolbar(NavigationToolbar2QT):

    def __init__(self, canvas, applicationWindow):
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            # ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            # ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )
        super(Toolbar, self).__init__(canvas, applicationWindow)
