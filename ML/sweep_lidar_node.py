import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import serial
import pigpio
import time


# This is a node used by a ROS driver ("tfmini_plus_driver")
# I didn't add the environment or driver, but can if needed!
#
# NOTE: The code used the original LiDAR (the Benewake TFMini Plus) and is now legacy
class SweepLidarNode(Node):
    def __init__(self, altitude_servo_pin=17, azimuth_servo_pin=18, altitude_min=90,
                 altitude_max=145, azimuth_min=0, azimuth_max=180, sweep_speed=1, az_speed=1,
                 num_readings_to_average=5, num_scan_repeats=3, log_file_path="lidar_scan_data.csv",
                 serial_port_path="/dev/ttyAMA0", serial_baudrate=115200):
        super().__init__("sweep_lidar_node")
        self.publisher_ = self.create_publisher(Range, "/tfminiplus/range", 10)

        try: 
            # Benewake TFMini Plus connection (over UART)
            self.serial_port = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)
            self.get_logger().info("TF Mini Plus node started.")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open serial port {serial_port_path}: {e}")
            raise

        # Setting up hobby servos - No encoders at this time--just PWM
        self.pi = pigpio.pi()

        if not self.pi.connected:
            self.get_logger().error("Pigpio connection failed. Ensure daemon is running.")
            raise ConnectionRefusedError("Pigpio daemon not running")
        
        # SERVO 1 - ALTITUDE (Vertical Angle)
        self.altitude_servo_pin = altitude_servo_pin
        self.pi.set_mode(self.altitude_servo_pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.altitude_servo_pin, 50)

        # SERVO 2 - AZIMUTH (Horizontal Angle)
        self.azimuth_servo_pin = azimuth_servo_pin
        self.pi.set_mode(self.azimuth_servo_pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.azimuth_servo_pin, 50)

        # Raster Scan Parameters
        # In this version, it blindly just does a full nod, then
        # shakes its head a degree, then does a full nod, and etc
        # 
        # These parameters allow you to set the minimum and maximum values
        # for the scan
        self.altitude_min = altitude_min
        self.altitude_max = altitude_max
        self.azimuth_min = azimuth_min
        self.azimuth_max = azimuth_max
        self.altitude_angle = self.altitude_min
        self.azimuth_angle = self.azimuth_min

        # These two are used by the servos to tell
        # which direction they should head next
        self.altitude_direction = 1
        self.azimuth_direction = 1

        # Both of these are the number of degrees per step
        self.sweep_speed = sweep_speed 
        self.az_speed = az_speed
    
        # Attempted to increase scan density, but increased
        # the time it took to scan.
        # SOLVED IN NEW VERSION: Uses more TOF to gather more points
        # per each scan.
        self.num_readings_to_average = num_readings_to_average
        self.num_scan_repeats = num_scan_repeats

        self.current_scan_repeat = 0

        self.log_file_path = log_file_path
        self.log_file = open(self.log_file_path, "w")

        self.log_file.write("timestamp,distance_cm,altitude_angle_deg,azimuth_\n")

        # Heartbeat
        # We need to increase the timer frequency to allow for multiple readings per position
        self.timer = self.create_timer(0.01, self.timer_callback)

        self.get_logger().info("Setting servos to start position")
        self.set_servo_angle(self.altitude_servo_pin, self.altitude_min)
        self.set_servo_angle(self.azimuth_servo_pin, self.azimuth_min)

        time.sleep(1)
    
    def set_servo_angle(self, pin, angle):
        # Make sure it's between 0 and 180
        angle = max(0, min(180, angle))

        current_pulse = self.pi.get_servo_pulsewidth(pin)
        
        if current_pulse == 0:
            current_angle = angle
        else:
            current_angle = (current_pulse - 500) * 180 / 2000
        
        steps = 10

        for step in range(1, steps+1):
            intermediate_angle = current_angle + (angle - current_angle) * step / steps
            pulse_width = int(500 + intermediate_angle * (2000 / 180))
            self.pi.set_servo_pulsewidth(pin, pulse_width)
            time.sleep(0.01)

    def read_tfmini_data(self):
        try:
            if self.serial_port.in_waiting >= 9:
                if self.serial_port.read(1) == b'\x59':
                    if self.serial_port.read(1) == b'\x59':
                        data = self.serial_port.read(7)
                        distance_cm = data[0] + data[1] *256
                        return distance_cm
        except Exception as e:
            self.get_logger().error(f"Failed to read TF Mini: {e}")
        return None
    
    def timer_callback(self):
        # Originally this read one point per scan, but I tried to
        # get it to average multiple readings per scan to get a more
        # accurate read; it only made the scan longer though.
        # SOLVED BY USING the multi-channel scan head.
        readings_to_average = []

        for _ in range(self.num_readings_to_average):
            distance_cm = self.read_tfmini_data()

            if distance_cm is not None:
                readings_to_average.append(distance_cm)
            
            # Benewake ToF is slow, so we have to wait for it
            time.sleep(0.005)
        
        if readings_to_average:
            average_distance_cm = sum(readings_to_average) / len(readings_to_average)
            current_timestamp = self.get_clock().now().nanoseconds / 1e9
            log_line = f"{current_timestamp},{average_distance_cm},{self.altitude_angle},{self.azimuth_angle}\n"
            self.log_file.write(log_line)
            self.log_file.flush()
            self.get_logger().info(f"Logged: {current_timestamp}, Dist = {average_distance_cm} cm, Alt = {self.altitude_angle} deg, Az = {self.azimuth_angle} deg\n")

        # Altitude Sweep
        self.altitude_angle += self.altitude_direction * self.sweep_speed
        self.altitude_angle = max(self.altitude_min, min(self.altitude_angle, self.altitude_max))
        self.set_servo_angle(self.altitude_servo_pin, self.altitude_angle)

        # Azimuth Sweep
        if self.altitude_angle == self.altitude_max or self.altitude_angle == self.altitude_min:
            # Flip alitutude direction for next pass
            self.altitude_direction *= -1 
            self.azimuth_angle += self.azimuth_direction * self.az_speed
            self.azimuth_angle = max(self.azimuth_min, min(self.azimuth_angle, self.azimuth_max))
            self.set_servo_angle(self.azimuth_servo_pin, self.azimuth_angle)

            # Check if one full scan is complete
            if self.azimuth_angle == self.azimuth_max or self.azimuth_angle == self.azimuth_min:
                self.current_scan_repeat += 1
                self.get_logger().info(f"Scan {self.current_scan_repeat} of {self.num_scan_repeats} complete.")

                if self.current_scan_repeat >= self.num_scan_repeats:
                    self.get_logger().info("All scans complete")
                    self.timer.cancel()
                    self.destroy_node()
        
    def destroy_node(self):
        self.get_logger().info("Cleaning up resources and shutting down")

        try:
            if self.log_file and not self.log_file.closed:
                self.log_file.close()
        except Exception as e:
            self.get_logger().error(f"Error closing log file: {e}")

        self.pi.set_servo_pulsewidth(self.altitude_servo_pin, 0)
        self.pi.set_servo_pulsewidth(self.azimuth_servo_pin, 0)
        self.pi.stop()
        super().destroy_node()
        

def main(args=None):
    rclpy.init(args=args)
    sweep_lidar_node = None

    try:
        sweep_lidar_node = SweepLidarNode()
        rclpy.spin(sweep_lidar_node)
    except KeyboardInterrupt:
        pass
    finally:
        if sweep_lidar_node:
            sweep_lidar_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

