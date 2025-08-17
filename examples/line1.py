from psim import Model, connect
from psim.blocks import Source, Process, Buffer, Sink
from psim.dists import Exponential, Triangular

# The README shows time units like "2h", "80h".
# For the MVP, the engine uses simple floats. We will assume a base unit (e.g., minutes).
# 2h = 120 minutes, 80h = 4800 minutes.
UNTIL = 4800.0
WARMUP = 120.0

# 1. Define the model container
m = Model(seed=7, warmup=WARMUP, until=UNTIL)

# 2. Define the simulation blocks
src = Source(name="Source", interarrival_dist=Exponential(mean=30))
mac = Process(name="M1", service_dist=Triangular(low=20.0, mode=25.0, high=35.0), capacity=1)
buf = Buffer(name="Buf", capacity=50)
snk = Sink(name="Sink")

# 3. Connect the blocks
connect(src, mac)
connect(mac, buf)
connect(buf, snk)

# 4. Register the blocks with the model
m.register(src, mac, buf, snk)

# 5. Add layout information for the viewer
# (This is optional and only used if the GUI is launched)
src.pos = (50, 150)
mac.pos = (200, 150)
buf.pos = (350, 150)
snk.pos = (500, 150)

# 5. Run the simulation
# (This will be done by the CLI runner, but we can add it here for direct execution)
if __name__ == "__main__":
    m.run()
