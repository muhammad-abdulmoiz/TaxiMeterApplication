import time
import math
from pynput import keyboard

# Constants for fare calculation (in dollars)
FARE_RATE_PER_KM = 3.0
FARE_RATE_PER_MIN_WAIT = 1.0
SPEED_CHANGE_IN_MPS = 5.0
DISTANCE_CONVERSION_FACTOR = 1000.0
UPDATE_INTERVAL_IN_SEC = 1


class TaxiMeter:
    def __init__(self):
        # Starting speed is set to 20 mps
        self.speed_in_mps = 20.0
        self.distance_in_meters = 0.0
        self.ride_time_in_sec = 0.0
        self.wait_time_in_sec = 0.0
        # Ride status can be 'stopped', 'driving', or 'waiting'
        self.ride_status = 'stopped'
        self.last_update_timestamp = time.time()

    def start_ride(self):
        if self.ride_status == "stopped":
            self.last_update_timestamp = time.time()
            self.ride_status = "driving"
            print("\nRide started.")
            self._display_speed()

    def pause_ride(self):
        if self.ride_status == "driving":
            self.speed_in_mps = 0.0
            self._update_metrics()
            self.ride_status = "waiting"
            print("\nRide paused.")
            self._display_speed()

    def _update_metrics(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_timestamp
        if self.ride_status == "driving":
            self.distance_in_meters += self.speed_in_mps * elapsed_time
            self.ride_time_in_sec += elapsed_time
        elif self.ride_status == "waiting":
            self.wait_time_in_sec += elapsed_time
        self.last_update_timestamp = current_time

    def resume_ride(self):
        if self.ride_status == "waiting":
            self.speed_in_mps = 20.0
            self._update_metrics()
            self.ride_status = "driving"
            print("\nRide resumed.")
            self._display_speed()

    def _display_speed(self):
        print(f"Current Speed: {self.speed_in_mps:.2f} m/s")

    def end_ride(self):
        if self.ride_status == "driving" or self.ride_status == "waiting":
            self._update_metrics()
        self.ride_status = "stopped"
        self._display_full_status()
        print("\nRide ended. Press 'S' to start a new ride.")

    def _display_full_status(self):
        distance_km = math.floor(self.distance_in_meters /
                                 DISTANCE_CONVERSION_FACTOR)
        distance_m = self.distance_in_meters % DISTANCE_CONVERSION_FACTOR
        ride_time_minutes, ride_time_seconds = divmod(
            self.ride_time_in_sec, 60)
        wait_time_minutes, wait_time_seconds = divmod(
            self.wait_time_in_sec, 60)
        fare = self._calculate_fare()
        average_speed = self.distance_in_meters / self.ride_time_in_sec

        print(
            f"\nRide Time: {int(ride_time_minutes)} Minutes"
            f" {int(ride_time_seconds)} Seconds")
        print(f"Distance: {int(distance_km)} KM {int(distance_m)} Meters")
        print(f"Speed: {average_speed:.2f} m/s")
        print(f"Fare: ${fare:.2f}")
        print(
            f"Wait Time: {int(wait_time_minutes)} Minutes"
            f" {int(wait_time_seconds)} Seconds\n")

    def _calculate_fare(self):
        distance_km = self.distance_in_meters / DISTANCE_CONVERSION_FACTOR
        wait_time_min = self.wait_time_in_sec / 60.0
        fare = (distance_km * FARE_RATE_PER_KM) + (
                    wait_time_min * FARE_RATE_PER_MIN_WAIT)
        return fare

    def increase_speed(self):
        if self.ride_status == "driving":
            self._update_metrics()
            self.speed_in_mps = min(200, self.speed_in_mps +
                                    SPEED_CHANGE_IN_MPS)
            print(f"Speed increased to {self.speed_in_mps:.2f} m/s.")
            self._display_speed()

    def decrease_speed(self):
        if self.ride_status == "driving":
            self._update_metrics()
            self.speed_in_mps = max(0, self.speed_in_mps - SPEED_CHANGE_IN_MPS)
            print(f"Speed decreased to {self.speed_in_mps:.2f} m/s.")
            self._display_speed()

    def run(self):
        print(
            "Taxi Meter is live. Use 'S' to start, 'U' to increase speed, "
            "'D' to decrease speed. Press 'P' to pause, 'R' to resume, "
            "and 'E' to end the ride.")

        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        try:
            if key.char.lower() == 's' and self.ride_status == 'stopped':
                self.start_ride()
            elif key.char.lower() == 'p' and self.ride_status == 'driving':
                self.pause_ride()
            elif key.char.lower() == 'r' and self.ride_status == 'waiting':
                self.resume_ride()
            elif key.char.lower() == 'e' and self.ride_status != 'stopped':
                self.end_ride()
                self.reset()
                print("Ready for a new ride. Press 'S' to start.")
            elif key.char.lower() == 'u' and self.ride_status == 'driving':
                self.increase_speed()
            elif key.char.lower() == 'd' and self.ride_status == 'driving':
                self.decrease_speed()
        except AttributeError:
            # Ignore non-character key presses
            pass

    def reset(self):
        self.speed_in_mps = 20.0
        self.distance_in_meters = 0.0
        self.ride_time_in_sec = 0.0
        self.wait_time_in_sec = 0.0
        self.ride_status = 'stopped'
        self.last_update_timestamp = time.time()


def main():
    taxi_meter = TaxiMeter()
    taxi_meter.run()


if __name__ == "__main__":
    main()
