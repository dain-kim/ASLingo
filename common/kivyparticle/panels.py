from particleconfig import format_config, PARTICLE_PARAMETERS, GRAVITY_EMITTER_PARAMETERS, RADIAL_EMITTER_PARAMETERS, START_COLOR_PARAMETERS, END_COLOR_PARAMETERS
from slider import ParamSlider

from kivy.core.image import Image
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.stencilview import StencilView
from kivy.uix.textinput import TextInput

import numpy as np
import random
import math
import shutil
import sys, os

sys.path.insert(0, os.path.abspath('..'))
from kivyparticle import ParticleSystem


def get_param_default(particle, param_name, param_label=None):
    # get the default value of parameter and convert to proper format
    value = getattr(particle, param_name)

    # convert angles into degrees
    if param_name in ['emit_angle', 'emit_angle_variance','start_rotation','start_rotation_variance','end_rotation','end_rotation_variance']:
        value = math.degrees(value)
    # parse RGBA color list
    elif param_name in ['start_color','start_color_variance','end_color','end_color_variance']:
        order = ['R','G','B','A']
        value = value[order.index(param_label)]
    return value


class ViewPanel(StencilView):
    def __init__(self):
        super(ViewPanel, self).__init__()

        # load up the default particle system
        # TODO fix
        self.particle = ParticleSystem(os.path.join('particle','particle.pex'))
        self.particle.emitter_x = -200
        self.particle.emitter_y = -200  # particle will be centered once layout is loaded
        self.particle.start()
        self.add_widget(self.particle)

        # self.texture = parse_texture(self.particle.texture_path)
        self.texture = self.parse_texture()

    def on_touch_down(self, touch):
        # ignore clicks outside screen bounds
        if self.collide_point(*touch.pos):
            self.move_particle(touch.pos)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.move_particle(touch.pos)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.move_particle(touch.pos)

    def move_particle(self, pos):
        # set emitter location based on mouse position
        self.particle.emitter_x = pos[0]
        self.particle.emitter_y = pos[1]

    def center_particle(self, window=None):
        self.particle.emitter_x = self.pos[0] + self.size[0]/2
        self.particle.emitter_y = self.pos[1] + self.size[1]/2

    def parse_texture(self):
        for tex in ['circle','star','blob','heart']:
            if tex in self.particle.texture_path:
                return tex
        # return os.path.basename(self.particle.texture_path).strip('.png')
        return 'circle'

    def update_param(self, param_name, param_value, param_label=None):

        # texture needs to be loaded in manually
        if param_name == 'texture':
            # TODO catch any path errors
            # TODO fix
            self.particle.texture_path = os.path.join(os.getcwd(),'particle',param_value)
            self.particle.texture = Image(self.particle.texture_path).texture
        
        # convert angles from degrees to radians
        elif param_name in ['emit_angle','emit_angle_variance','start_rotation','start_rotation_variance',
                            'end_rotation','end_rotation_variance','rotate_per_second','rotate_per_second_variance']:
            setattr(self.particle, param_name, math.radians(param_value))
        
        # color is stored as a list; update one element of that list
        elif param_name in ['start_color','start_color_variance','end_color','end_color_variance']:
            value = getattr(self.particle, param_name)
            order = ['R','G','B','A']
            value[order.index(param_label)] = param_value
            setattr(self.particle, param_name, value)
        
        else:
            setattr(self.particle, param_name, param_value)

    def load_config(self, config_path):
        # load up new particle system
        self.remove_widget(self.particle)
        self.particle = ParticleSystem(config_path)
        self.center_particle()
        self.particle.start()
        self.add_widget(self.particle)
        self.texture = self.parse_texture()

    def save_config(self, config_name, save_path):

        # save current path so we can return to it later
        old_cwd = os.getcwd()
        # go to location to save config
        os.chdir(save_path)

        # create particle/ directory if it doesn't exist
        if not os.path.isdir('particle'):
            os.mkdir('particle')
        os.chdir('particle')
        # write config file. this will overwrite existing file named config_name
        with open(config_name, 'w') as f:
            f.write(format_config(self.particle))
        f.close()
        # copy over texture file
        if not os.path.exists(os.path.join(os.getcwd(), self.texture+'.png')):
            shutil.copyfile(self.particle.texture_path, os.path.join(os.getcwd(), self.texture+'.png'))

        print('Saved config file to {}'.format(os.getcwd()))

        # switch back to old working directory
        os.chdir(old_cwd)

class SavePopup(Popup):
    def __init__(self, save_callback, pex_error_callback):
        super(SavePopup, self).__init__()

        self.save_callback = save_callback
        self.pex_error_callback = pex_error_callback

        self.content_holder = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserIconView(path=os.getcwd(), size_hint=(1,.8))
        self.config_name = TextInput(hint_text='config.pex', multiline=False, size_hint=(.3,.1))
        self.save_bt = Button(text='Save', size_hint=(.1,.1), 
                              background_normal='button6.png', background_down='button6down.png')
        
        self.filechooser.bind(on_entry_added=self.update_path)
        self.config_name.bind(on_text_validate=self.save)
        self.save_bt.bind(on_release=self.save)

        self.content_holder.add_widget(self.filechooser)
        self.content_holder.add_widget(self.config_name)
        self.content_holder.add_widget(self.save_bt)

        self.title = 'save file to {}'.format(self.filechooser.path)
        self.content = self.content_holder
        self.size_hint=(.7,.7)
        self.pos_hint={'center_x':.5, 'center_y':.5}

    def save(self, *kwargs):
        if self.config_name.text == '':
            config_name = 'config.pex'
        else:
            config_name = self.config_name.text
        if not config_name.endswith('.pex'):
            self.pex_error_callback()
        else:
            self.save_callback(config_name, self.filechooser.path)
            self.dismiss()

    def update_path(self, *kwargs):
        self.title = 'save file to {}'.format(self.filechooser.path)

class LoadPopup(Popup):
    def __init__(self, load_callback, pex_error_callback, error_callback, on_new_config):
        super(LoadPopup, self).__init__()

        self.load_callback = load_callback
        self.pex_error_callback = pex_error_callback
        self.error_callback = error_callback
        self.on_new_config = on_new_config

        self.content_holder = BoxLayout()
        self.filechooser = FileChooserIconView(path=os.getcwd(),size_hint=(.8,.8))
        self.load_bt = Button(text='Select',size_hint=(.1,.1), 
                              background_normal='button6.png', background_down='button6down.png')

        self.filechooser.bind(on_entry_added=self.update_path)
        self.load_bt.bind(on_release=self.load)

        self.content_holder.add_widget(self.filechooser)
        self.content_holder.add_widget(self.load_bt)

        self.title = 'load file from {}'.format(self.filechooser.path)
        self.content = self.content_holder
        self.size_hint = (.7,.7)
        self.pos_hint = {'center_x':.5,'center_y':.5}

    def load(self, *kwargs):
        if self.filechooser.selection != []:
            config_path = self.filechooser.selection[0]

            if not config_path.endswith('.pex'):
                self.pex_error_callback()
                return
            try:
                # hand off config path to particle.load_config
                self.load_callback(config_path)

                # call App to update slider defaults and emitter type
                self.on_new_config()

                # close popup window
                self.dismiss()

            except:
                # config file cannot be loaded
                self.error_callback()

    def update_path(self, *kwargs):
        self.title = 'load file from {}'.format(self.filechooser.path)


class GeneralPanel(BoxLayout):
    def __init__(self, particle, on_new_config, on_randomize):
        super(GeneralPanel, self).__init__()

        self.orientation = 'horizontal'
        self.ps = particle
        self.on_new_config = on_new_config
        self.on_randomize = on_randomize

        # Error messages for popup
        self.pex_error_message = Label(text='Particle system only accepts .pex files',size_hint=(.1,.1))
        self.pex_error_popup = Popup(title='Error', content=self.pex_error_message, size_hint=(.5,.2), pos_hint={'center_x':.5,'center_y':.5})
        self.fail_error_message = Label(text='Config file cannot be loaded',size_hint=(.1,.1))
        self.fail_error_popup = Popup(title='Error', content=self.fail_error_message, size_hint=(.5,.2), pos_hint={'center_x':.5,'center_y':.5})

        # popup for saving file
        self.save_popup = SavePopup(save_callback=self.ps.save_config, pex_error_callback=self.pex_error_popup.open)

        # popup for loading file
        self.load_popup = LoadPopup(load_callback=self.ps.load_config, pex_error_callback=self.pex_error_popup.open, 
                                    error_callback=self.fail_error_popup.open, on_new_config=on_new_config)
        
        # general buttons
        self.save = Button(text='Save',size_hint_y=None,height=150,pos_hint={'top':1}, 
                           background_normal='button6.png', background_down='button6down.png')
        self.save.bind(on_release=self.save_popup.open)
        self.add_widget(self.save)
        
        self.load = Button(text='Load',size_hint_y=None,height=150,pos_hint={'top':1}, 
                           background_normal='button6.png', background_down='button6down.png')
        self.load.bind(on_release=self.load_popup.open)
        self.add_widget(self.load)
        
        self.edit = Button(text='Texture: {}'.format(self.ps.texture),size_hint_y=None,height=150,pos_hint={'top':1}, 
                           background_normal='button6.png', background_down='button6down.png')
        self.edit.bind(on_release=self.change_texture)
        self.add_widget(self.edit)

        self.random = Button(text='Randomize',size_hint_y=None,height=150,pos_hint={'top':1}, 
                           background_normal='button6.png', background_down='button6down.png')
        self.random.bind(on_release=self.on_randomize)
        self.add_widget(self.random)

    def change_texture(self, button):
        textures = ['circle','star','blob','heart']

        # cycle to next texture
        self.ps.texture = textures[(textures.index(self.ps.texture)+1) % 4]
        self.ps.update_param('texture', '{}.png'.format(self.ps.texture))
        button.text = 'Texture: {}'.format(self.ps.texture)

    def randomize(self):
        pass

    def reset_default(self):
        self.edit.text = 'Texture: {}'.format(self.ps.texture)

    def change_font_size(self, size):
        pass


class ParticleConfigPanel(BoxLayout):
    def __init__(self, particle):
        super(ParticleConfigPanel, self).__init__()
        self.orientation = 'vertical'
        self.ps = particle
        self.sliders = []

        self.add_widget(Label(text='Particle Configuration', size_hint_y=None, height=100))
        
        for param in PARTICLE_PARAMETERS:
            slider = ParamSlider(param, default=get_param_default(self.ps.particle, param['name']), callback=self.ps.update_param)
            self.sliders.append(slider)
            self.add_widget(slider)

    def randomize(self):
        for slider in self.sliders:
            value = random.uniform(slider.min, slider.max)
            slider.set_value(value)

    def reset_default(self):
        for slider in self.sliders:
            default = get_param_default(self.ps.particle, slider.name)
            slider.set_value(default)

    def change_font_size(self, size):
        for slider in self.sliders:
            slider.change_font_size(size)


class EmitterConfigPanel(BoxLayout):
    def __init__(self, particle):
        super(EmitterConfigPanel, self).__init__()

        self.orientation = 'vertical'
        self.ps = particle
        self.gravity_sliders = []
        self.radial_sliders = []

        # Gravity emitter config
        self.gravity_dropdown = BoxLayout(orientation='vertical')
        for param in GRAVITY_EMITTER_PARAMETERS:
            slider = ParamSlider(param, default=get_param_default(self.ps.particle, param['name']), callback=self.ps.update_param)
            self.gravity_sliders.append(slider)
            self.gravity_dropdown.add_widget(slider)

        # Radial emitter config
        self.radial_dropdown = BoxLayout(orientation='vertical')
        for param in RADIAL_EMITTER_PARAMETERS:
            slider = ParamSlider(param, default=get_param_default(self.ps.particle, param['name']), callback=self.ps.update_param)
            self.radial_sliders.append(slider)
            self.radial_dropdown.add_widget(slider)

        self.add_widget(Label(text='Emitter Configuration', size_hint_y=None, height=100))

        if self.ps.particle.emitter_type == 0:
            self.emitter_type = 'Gravity'
            self.bt = Button(text='Emitter Type: {}'.format(self.emitter_type), size_hint_y=None, height=100, 
                             background_normal='button6.png', background_down='button6down.png')
            self.add_widget(self.bt)
            self.add_widget(self.gravity_dropdown)
        else:
            self.emitter_type = 'Radial'
            self.bt = Button(text='Emitter Type: {}'.format(self.emitter_type), size_hint_y=None, height=100, 
                             background_normal='button6.png', background_down='button6down.png')
            self.add_widget(self.bt)
            self.add_widget(self.radial_dropdown)
        
        self.bt.bind(on_release=self.switch_emitter_type)

    def switch_emitter_type(self, button=None):
        if self.emitter_type == 'Gravity':
            self.emitter_type = 'Radial'
            self.remove_widget(self.gravity_dropdown)
            self.add_widget(self.radial_dropdown)
            self.ps.update_param('emitter_type',1)
        else:
            self.emitter_type = 'Gravity'
            self.remove_widget(self.radial_dropdown)
            self.add_widget(self.gravity_dropdown)
            self.ps.update_param('emitter_type',0)
        self.bt.text = 'Emitter Type: {}'.format(self.emitter_type)

        self.ps.particle.stop(True)
        self.ps.particle.start()

    def randomize(self):
        for slider in self.gravity_sliders:
            value = random.uniform(slider.min, slider.max)
            slider.set_value(value)
        
        for slider in self.radial_sliders:
            # cap min_radius based on max_radius
            if slider.name == 'min_radius':
                value = random.uniform(slider.min, min(slider.max, self.ps.particle.max_radius))
                slider.set_value(value)
            else:
                value = random.uniform(slider.min, slider.max)
                slider.set_value(value)

    def reset_default(self):
        if self.ps.particle.emitter_type == 0:
            new_emitter_type = 'Gravity'
        else:
            new_emitter_type = 'Radial'
        if new_emitter_type != self.emitter_type:
            self.switch_emitter_type()

        for slider in self.gravity_sliders:
            default = get_param_default(self.ps.particle, slider.name)
            slider.set_value(default)
        for slider in self.radial_sliders:
            default = get_param_default(self.ps.particle, slider.name)
            slider.set_value(default)
    
    def change_font_size(self, size):
        for slider in self.gravity_sliders:
            slider.change_font_size(size)
        for slider in self.radial_sliders:
            slider.change_font_size(size)


class StartColorPanel(BoxLayout):
    def __init__(self, particle):
        super(StartColorPanel, self).__init__()

        self.orientation = 'vertical'
        self.ps = particle
        self.sliders = []
        
        self.add_widget(Label(text='Start Color', size_hint_y=None, height=50))

        for param in START_COLOR_PARAMETERS:
            slider = ParamSlider(param, default=get_param_default(self.ps.particle, param['name'], param['label']), callback=self.ps.update_param)
            self.sliders.append(slider)
            self.add_widget(slider)

            if START_COLOR_PARAMETERS.index(param) == 3:
                self.add_widget(Label(text='Start Color Variance', size_hint_y=None, height=50))

    def randomize(self):
        for slider in self.sliders:
            value = random.uniform(slider.min, slider.max)
            slider.set_value(value)

    def reset_default(self):
        for slider in self.sliders:
            default = get_param_default(self.ps.particle, slider.name, slider.label)
            slider.set_value(default)
    
    def change_font_size(self, size):
        for slider in self.sliders:
            slider.change_font_size(size)


class EndColorPanel(BoxLayout):
    def __init__(self, particle):
        super(EndColorPanel, self).__init__()

        self.orientation = 'vertical'
        self.ps = particle
        self.sliders = []

        self.add_widget(Label(text='End Color', size_hint_y=None, height=50))

        for param in END_COLOR_PARAMETERS:
            slider = ParamSlider(param, default=get_param_default(self.ps.particle, param['name'], param['label']), callback=self.ps.update_param)
            self.sliders.append(slider)
            self.add_widget(slider)

            if END_COLOR_PARAMETERS.index(param) == 3:
                self.add_widget(Label(text='End Color Variance', size_hint_y=None, height=50))
    
    def randomize(self):
        for slider in self.sliders:
            value = random.uniform(slider.min, slider.max)
            slider.set_value(value)

    def reset_default(self):
        for slider in self.sliders:
            default = get_param_default(self.ps.particle, slider.name, slider.label)
            slider.set_value(default)

    def change_font_size(self, size):
        for slider in self.sliders:
            slider.change_font_size(size)
