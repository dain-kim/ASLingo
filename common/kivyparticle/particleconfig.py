import os
import math

PARTICLE_PARAMETERS = [
    {
        'name':'max_num_particles',
        'label':'Max Particles',
        'min':1,
        'max':1000,
        'step': 1
    },
    {
        'name':'life_span',
        'label':'Lifespan',
        'min':.1,
        'max':10,
        'step': .1
    },
    {
        'name':'life_span_variance',
        'label':'Lifespan Var.',
        'min':.1,
        'max':10,
        'step': .1
    },
    {
        'name':'start_size',
        'label':'Start Size',
        'min':0,
        'max':100,
        'step': 1
    },
    {
        'name':'start_size_variance',
        'label':'Start Size Var.',
        'min':0,
        'max':100,
        'step': 1
    },
    {
        'name':'end_size',
        'label':'End Size',
        'min':0,
        'max':100,
        'step': 1
    },
    {
        'name':'end_size_variance',
        'label':'End Size Var.',
        'min':0,
        'max':100,
        'step': 1
    },
    {
        'name':'emit_angle',
        'label':'Emit Angle',
        'min':0,
        'max':360,
        'step': 1
    },
    {
        'name':'emit_angle_variance',
        'label':'Emit Angle Var.',
        'min':0,
        'max':360,
        'step': 1
    },
    {
        'name':'start_rotation',
        'label':'Start Rotation',
        'min':0,
        'max':360,
        'step': 1
    },
    {
        'name':'start_rotation_variance',
        'label':'Start Rot. Var.',
        'min':0,
        'max':360,
        'step': 1
    },
    {
        'name':'end_rotation',
        'label':'End Rotation',
        'min':0,
        'max':360,
        'step': 1
    },
    {
        'name':'end_rotation_variance',
        'label':'End Rot. Var.',
        'min':0,
        'max':360,
        'step': 1
    }
]

GRAVITY_EMITTER_PARAMETERS = [
    {
        'name':'emitter_x_variance',
        'label':'X Variance',
        'min':0,
        'max':1000,
        'step': 1
    },
    {
        'name':'emitter_y_variance',
        'label':'Y Variance',
        'min':0,
        'max':1000,
        'step': 1
    },
    {
        'name':'speed',
        'label':'Speed',
        'min':0,
        'max':500,
        'step': 1
    },
    {
        'name':'speed_variance',
        'label':'Speed Var.',
        'min':0,
        'max':500,
        'step': 1
    },
    {
        'name':'gravity_x',
        'label':'Gravity X',
        'min':-500,
        'max':500,
        'step': 1
    },
    {
        'name':'gravity_y',
        'label':'Gravity Y',
        'min':-500,
        'max':500,
        'step': 1
    },
    {
        'name':'tangential_acceleration',
        'label':'Tangential Acc.',
        'min':-500,
        'max':500,
        'step': 1
    },
    {
        'name':'tangential_acceleration_variance',
        'label':'Tan. Acc. Var.',
        'min':0,
        'max':500,
        'step': 1
    },
    {
        'name':'radial_acceleration',
        'label':'Radial Acc.',
        'min':-500,
        'max':500,
        'step': 1
    },
    {
        'name':'radial_acceleration_variance',
        'label':'Rad. Acc. Var.',
        'min':0,
        'max':500,
        'step': 1
    }
]

RADIAL_EMITTER_PARAMETERS = [
    {
        'name':'max_radius',
        'label':'Max Radius',
        'min':0,
        'max':500,
        'step': 1
    },
    {
        'name':'max_radius_variance',
        'label':'Max Radius Var.',
        'min':0,
        'max':500,
        'step': 1
    },
    {
        'name':'min_radius',
        'label':'Min Radius',
        'min':0,
        'max':500,
        'step': 1
    },
    # {
    #     'name':'min_radius_variance',
    #     'label':'Min Radius Variance',
    #     'min':0,
    #     'max':500,
    #     'step': 1
    # },
    {
        'name':'rotate_per_second',
        'label':'Deg/Sec',
        'min':-360,
        'max':360,
        'step': 1
    },
    {
        'name':'rotate_per_second_variance',
        'label':'Deg/Sec Var.',
        'min':0,
        'max':360,
        'step': 1
    }
]

START_COLOR_PARAMETERS = [
    {
        'name':'start_color',
        'label':'R',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color',
        'label':'G',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color',
        'label':'B',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color',
        'label':'A',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color_variance',
        'label':'R',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color_variance',
        'label':'G',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color_variance',
        'label':'B',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'start_color_variance',
        'label':'A',
        'min':0,
        'max':1,
        'step': .1
    }
]


END_COLOR_PARAMETERS = [
    {
        'name':'end_color',
        'label':'R',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color',
        'label':'G',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color',
        'label':'B',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color',
        'label':'A',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color_variance',
        'label':'R',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color_variance',
        'label':'G',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color_variance',
        'label':'B',
        'min':0,
        'max':1,
        'step': .1
    },
    {
        'name':'end_color_variance',
        'label':'A',
        'min':0,
        'max':1,
        'step': .1
    }
]

def format_config(particle):
    # Can't think of a more graceful way of doing this
    config = '''<particleEmitterConfig>
  <texture name="{}"/>
  <sourcePosition x="{}" y="{}"/>
  <sourcePositionVariance x="{}" y="{}"/>
  <speed value="{}"/>
  <speedVariance value="{}"/>
  <particleLifeSpan value="{}"/>
  <particleLifespanVariance value="{}"/>
  <angle value="{}"/>
  <angleVariance value="{}"/>
  <gravity x="{}" y="{}"/>
  <radialAcceleration value="{}"/>
  <tangentialAcceleration value="{}"/>
  <radialAccelVariance value="{}"/>
  <tangentialAccelVariance value="{}"/>
  <startColor red="{}" green="{}" blue="{}" alpha="{}"/>
  <startColorVariance red="{}" green="{}" blue="{}" alpha="{}"/>
  <finishColor red="{}" green="{}" blue="{}" alpha="{}"/>
  <finishColorVariance red="{}" green="{}" blue="{}" alpha="{}"/>
  <maxParticles value="{}"/>
  <startParticleSize value="{}"/>
  <startParticleSizeVariance value="{}"/>
  <finishParticleSize value="{}"/>
  <FinishParticleSizeVariance value="{}"/>
  <duration value="-1.00"/>
  <emitterType value="{}"/>
  <maxRadius value="{}"/>
  <maxRadiusVariance value="{}"/>
  <minRadius value="{}"/>
  <minRadiusVariance value="0.00"/>
  <rotatePerSecond value="{}"/>
  <rotatePerSecondVariance value="{}"/>
  <blendFuncSource value="{}"/>
  <blendFuncDestination value="{}"/>
  <rotationStart value="{}"/>
  <rotationStartVariance value="{}"/>
  <rotationEnd value="{}"/>
  <rotationEndVariance value="{}"/>
</particleEmitterConfig>
    '''.format(os.path.basename(particle.texture_path),
        particle.emitter_x,
        particle.emitter_y,
        particle.emitter_x_variance,
        particle.emitter_y_variance,
        particle.speed,
        particle.speed_variance,
        particle.life_span,
        particle.life_span_variance,
        math.degrees(particle.emit_angle),
        math.degrees(particle.emit_angle_variance),
        particle.gravity_x,
        particle.gravity_y,
        particle.radial_acceleration,
        particle.tangential_acceleration,
        particle.radial_acceleration_variance,
        particle.tangential_acceleration_variance,
        particle.start_color[0],
        particle.start_color[1],
        particle.start_color[2],
        particle.start_color[3],
        particle.start_color_variance[0],
        particle.start_color_variance[1],
        particle.start_color_variance[2],
        particle.start_color_variance[3],
        particle.end_color[0],
        particle.end_color[1],
        particle.end_color[2],
        particle.end_color[3],
        particle.end_color_variance[0],
        particle.end_color_variance[1],
        particle.end_color_variance[2],
        particle.end_color_variance[3],
        particle.max_num_particles,
        particle.start_size,
        particle.start_size_variance,
        particle.end_size,
        particle.end_size_variance,

        particle.emitter_type,
        particle.max_radius,
        particle.max_radius_variance,
        particle.min_radius,

        math.degrees(particle.rotate_per_second),
        math.degrees(particle.rotate_per_second_variance),
        particle.blend_factor_source,
        particle.blend_factor_dest,
        math.degrees(particle.start_rotation),
        math.degrees(particle.start_rotation_variance),
        math.degrees(particle.end_rotation),
        math.degrees(particle.end_rotation_variance))


    return config
