import sys,time; sys.argv=["x","none"]
exec(open("/home/claude/v/s0.py").read().replace('run("s0"','#'))
s=bpy.context.scene
def T(lbl):
  s.frame_set(150); s.render.filepath="/tmp/p.png"; t=time.time(); bpy.ops.render.render(write_still=True); print("T",lbl,round(time.time()-t,2))
T("base"); T("base2")
s.compositing_node_group=None; T("nobloom")
s.cycles.use_denoising=False; T("nodenoise")
s.cycles.samples=4; T("4spp")
