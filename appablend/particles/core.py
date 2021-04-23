import bpy


### makes particle system settings single-user
def single_user_particle_settings(obj):
    for ps in obj.particle_systems:
        if ps.settings.users > 1:
            setts = ps.settings.copy()
            ps.settings = setts


### reseeds a particle system
def particles_reseed(o, factor=1.1):
    if o is None:
        return

    for ps in o.particle_systems:
        ps.seed = ps.seed * factor


### reseeds all selected particle systems
def particles_reseed_selected(factor=1.1):
    for obj in bpy.context.selected_objects:
        particles_reseed(obj, factor)


### reseeds all particle systems
def particles_reseed_selected(factor=1.1):
    for obj in bpy.data.objects:
        particles_reseed(obj, factor)
