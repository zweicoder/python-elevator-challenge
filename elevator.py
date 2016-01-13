UP = 1
DOWN = 2
FLOOR_COUNT = 6


class ElevatorLogic(object):
    def __init__(self):
        # Feel free to add any instance variables you want.
        self.destination_floor = None
        self.callbacks = None
        self.ups = []  # floors to stop at if it's going up
        self.downs = []  # floors to stop at if it's going down
        self.state = None  # The direction our elevator is heading towards, regardless of whether it's moving

    def update_destination(self):
        if not self.ups and not self.downs:
            self.destination_floor = None
            return

        if self.state == UP:
            # prefer up

            # Find smallest up jobs above us
            dest = filter(lambda x: x > self.callbacks.current_floor, self.ups)
            if dest:
                self.destination_floor = min(dest)
                return

            # Find largest down jobs below us if we're gonna move down
            dest = self.downs
            if dest:
                self.destination_floor = max(dest)
                return

            # wtf srsly
            dest = self.ups
            if dest:
                self.destination_floor = min(dest)
                return

        else:
            #prefer down

            # Largest down jobs below us
            dest = filter(lambda x: x < self.callbacks.current_floor, self.downs)
            if dest:
                self.destination_floor = max(dest)
                return

            # Smallest up jobs above us
            dest = self.ups
            if dest:
                self.destination_floor = min(dest)
                return

            # Largest down jobs above us
            dest = self.downs
            if dest:
                self.destination_floor = max(dest)
                return

    def on_called(self, floor, direction):
        if direction == UP:
            if floor not in self.ups:
                self.ups.append(floor)
        elif direction == DOWN:
            if floor not in self.downs:
                self.downs.append(floor)

        self.update_destination()
        if not self.state:
            self.update_state()

    def on_floor_selected(self, floor):
        if floor == self.callbacks.current_floor:
            return

        if not self.state:
            if floor > self.callbacks.current_floor:
                self.ups.append(floor)
            elif floor < self.callbacks.current_floor:
                self.downs.append(floor)
            self.update_destination()
            self.update_state()
            return

        if floor > self.callbacks.current_floor and self.state == UP:
            if floor not in self.ups:
                self.ups.append(floor)
        elif floor < self.callbacks.current_floor and self.state == DOWN:
            if floor not in self.downs:
                self.downs.append(floor)

        self.update_destination()

    def on_floor_changed(self):
        if self.destination_floor == self.callbacks.current_floor:
            # Clean up jobs
            if self.state == UP:
                if not self.ups:
                    # Only way ups is empty is when we are moving up for a downs job
                    self.downs.remove(self.destination_floor)
                    self.state = DOWN
                else:
                    # Remove completed job in ups
                    self.ups.remove(self.destination_floor)
                    # Someone called the lift to go up on this floor
                    self.state = UP

            elif self.state == DOWN:
                if not self.downs:
                    self.ups.remove(self.destination_floor)
                    self.state = UP
                else:
                    self.downs.remove(self.destination_floor)
                    self.state = DOWN
            # self.log()
            self.callbacks.motor_direction = None
            self.destination_floor = None
            # self.update_destination()

    def log(self):
        print "Dest: %s" % self.destination_floor
        print "ups: %s"% self.ups
        print "downs: %s" % self.downs

    def on_ready(self):
        self.update_destination()
        self.log()
        if not self.destination_floor:
            self.callbacks.motor_direction = None
            self.state = None
            return

        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None
            if self.state == UP :
                self.state = DOWN
                self.downs.remove(self.destination_floor)
            elif self.state == DOWN:
                self.state = UP
                self.ups.remove(self.destination_floor)
            return

        self.update_state()
        if self.destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif self.destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN

    def update_state(self):
        if self.destination_floor > self.callbacks.current_floor:
            self.state = UP
        elif self.destination_floor < self.callbacks.current_floor:
            self.state = DOWN
