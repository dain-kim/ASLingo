import sys, os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from panels import ViewPanel, GeneralPanel, ParticleConfigPanel, EmitterConfigPanel, StartColorPanel, EndColorPanel


class ParticleEditor(App):

    """
    Handles the macro layout.

    The editor screen is laid out on a 3x2 grid.
    Ratio is roughly 6:2:2 (cols), 7:3 (rows)


    |ViewPanel   |ParticleConfigPanel|EmitterConfigPanel|
    -----------------------------------------------------
    |GeneralPanel|StartColorPanel    |EndColorPanel     |
    
    """
    def build(self):

        root = GridLayout(cols=3,rows=2,spacing=(10,10),
                cols_minimum={0:Window.width*.55,1:Window.width*.2,2:Window.width*.2},
                rows_minimum={0:Window.height*.65,1:Window.height*.3})
        
        self.ps = ViewPanel()
        self.panels = [ ParticleConfigPanel(self.ps),
                        EmitterConfigPanel(self.ps),
                        GeneralPanel(self.ps, on_new_config=self.on_new_config, on_randomize=self.on_randomize),
                        StartColorPanel(self.ps),
                        EndColorPanel(self.ps)]
        
        root.add_widget(self.ps)
        for panel in self.panels:
            root.add_widget(panel)


        Window.bind(on_resize=self.on_window_resize)
        # Window.top = 0
        # Window.left = 0

        # center particle after the next frame, once the layout is loaded
        Clock.schedule_once(self.ps.center_particle)

        # on_draw works like on_update for BaseWidget
        # Window.bind(on_draw=self.on_update)

        return root

    def on_window_resize(self, window, width, height):
        Clock.schedule_once(self.ps.center_particle)
        for panel in self.panels:
            panel.change_font_size(max(20, int(height/60)))

    def on_new_config(self):
        for panel in self.panels:
            panel.reset_default()

    def on_randomize(self, button=None):
        for panel in self.panels:
            panel.randomize()

        # restart particle to clear canvas and prevent "sticking" particles
        self.ps.particle.stop(True)
        self.ps.particle.start()

    def on_update(self, window):
        pass


if __name__ == '__main__':
    ParticleEditor().run()