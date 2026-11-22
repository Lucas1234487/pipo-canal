import bpy,time
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32)
bpy.ops.object.light_add(type='SUN',location=(3,-3,3))
bpy.ops.object.camera_add(location=(0,-5,0),rotation=(1.5708,0,0)); s.camera=bpy.context.object
s.world=bpy.data.worlds.new("w")
s.render.resolution_x=720;s.render.resolution_y=1280
for eng in ['BLENDER_EEVEE','CYCLES']:
  try:
    s.render.engine=eng
    if eng=='CYCLES': s.cycles.samples=16; s.cycles.use_denoising=True
    s.render.filepath=f"/tmp/t_{eng}.png"; t=time.time(); bpy.ops.render.render(write_still=True); print(eng,time.time()-t)
  except Exception as e: print(eng,"ERR",e)
