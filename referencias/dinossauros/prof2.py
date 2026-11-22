import sys,time; sys.argv=["x","none"]
exec(open("/home/claude/v/s0.py").read().replace('run("s0"','#'))
s=bpy.context.scene
def T(lbl):
  s.frame_set(150); s.render.filepath="/tmp/p.png"; t=time.time(); bpy.ops.render.render(write_still=True); print("T",lbl,round(time.time()-t,2))
s.render.resolution_x=540; s.render.resolution_y=960
s.cycles.samples=4; T("540-4"); T("540-4b")
D.objects["clouds"].hide_render=True; T("noclouds")
D.objects["atmo"].hide_render=True; T("noatmo")
s.cycles.samples=1; T("1spp")
