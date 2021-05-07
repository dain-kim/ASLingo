# Particle Editor

This is a tool used to generate particle graphics for use in Kivy. There are three main functionalities:

- Create and edit a particle system using the editor interface
- Save the particle system configuration to your desired location
- Load a saved configuration to inspect it

## What is a particle system?

A particle system is a computer graphics technique used to emulate fire, explosions, trails, sparks, and other "fuzzy" phenomena. Check out some examples in the `particle` folder by loading them into the editor.

## How to run the editor

Open up a terminal and navigate to the `common/kivyparticle` folder. Run `python editor.py` to start up the editor.

## Editing

On startup, the particle editor will load up a default particle system. Use the **slidebars** on the right to edit specific attributes, or press the **randomize** button to shake things up. You can also use the **texture** button to change the particle's texture (shape), and the **emitter** button to switch between the gravity and radial emitters. You can interact with the particle by clicking or dragging on the viewing window.

## Saving

Once you come up with a configuration that you like, press the **save** button to download the particle configuration to your desired location. This will create a `particle/` folder at the location and save your configuration file (.pex) and texture file (.png) in it. We recommend that you save your particle files in the same directory as the script that uses the particle system.

## Loading

If at any point you want to inspect your particle again or make changes, you can do so by loading up your configuration file. Press the **load** button and select your .pex file. Note that for this to work, you should have both the config file and the texture file in the same directory.

## Using your particle graphics

To use your particle in a system, create a `ParticleSystem` and give the relative path to your configuration file as input. The `particle_paint.py` script in `class3` is a good example on how to do this.



### Notice any bugs?

This is a brand-new project! If you encounter any bugs or unexpected behaviors while using the system, please contact Dain [dainkim@mit.edu] or make a piazza post and I can take a look. Feedback and suggestions are also much appreciated!

