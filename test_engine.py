"""Run:  py test_engine.py   (no server needed)"""
from engine import Engine, WARN_AFTER, OFF_AFTER

t = 1000.0
e = Engine(now=t)
r102 = e.room(2)

assert e.state(t)["rooms"][1]["status"] == "empty_lights_on"       # empty, lights on = red
t += WARN_AFTER + 1; e.tick(t)
assert e.state(t)["rooms"][1]["status"] == "warning"               # then warning
t += (OFF_AFTER - WARN_AFTER); e.tick(t)
assert e.state(t)["rooms"][1]["status"] == "switched_off"          # then auto switch-off
before = e.saved_kwh
t += 10; e.tick(t)
assert e.saved_kwh > before                                        # savings counter rises
e.set_persons(2, 1, t); e.tick(t)
assert e.state(t)["rooms"][1]["status"] == "occupied"              # person returns, lights on
assert r102.lights_on and not r102.auto_off
print("All engine tests passed")
