import bpy,time
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32)
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-1))
bpy.ops.object.light_add(type='SUN',location=(3,-3,3))
bpy.ops.object.camera_add(location=(0,-5,0),rotation=(1.5708,0,0)); s.camera=bpy.context.object
s.world=bpy.data.worlds.new("w")
s.render.resolution_x=720;s.render.resolution_y=1280
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=8
for f in range(3):
  s.frame_set(f+1); s.render.filepath=f"/tmp/e{f}.png"; t=time.time(); bpy.ops.render.render(write_still=True); print("EV",time.time()-t)
s.render.engine='CYCLES'; s.cycles.samples=6; s.cycles.use_denoising=True; s.render.resolution_x=540;s.render.resolution_y=960
for f in range(2):
  s.render.filepath=f"/tmp/c{f}.png"; t=time.time(); bpy.ops.render.render(write_still=True); print("CY",time.time()-t)
