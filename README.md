# kawapai

Python library for interfacing with Kawasaki D, E and F series controllers

Warning: API is in experimental stage

Example:

```python
from kawapai import robot

E_controller_robot = robot.KawaBot(host="127.0.0.1", port=10000)

E_controller_robot.abort_kill_all()

E_controller_robot.motor_power_off()
E_controller_robot.reset_error()
E_controller_robot.load_as_file("kawasaki_side.as")
E_controller_robot.motor_power_on()

E_controller_robot.initiate_kawabot()
E_controller_robot.connect_to_movement_server()

E_controller_robot.jmove(0,0,0,0,0,0)

time.sleep(1)

E_controller_robot.jmove(76,43,0,100,3,50)

E_controller_robot.close_movement_server() 
E_controller_robot.disconnect()

```