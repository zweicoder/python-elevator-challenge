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
        self.selected = []
        self.state = None  # The direction our elevator is heading towards, regardless of whether it's moving

    def update_destination(self):
        if not self.ups and not self.downs and not self.selected:
            self.destination_floor = None
            return

        if self.state == UP:
            # prefer up

            # Find smallest up jobs above us
            dest = filter(lambda x: x > self.callbacks.current_floor, self.ups + self.selected)
            if dest:
                self.destination_floor = min(dest)
                return

            job = max(self.selected) if self.selected else None # Jobs selected on the lift
            # Find largest down jobs if we're gonna move down
            if self.downs:
                self.destination_floor = max(max(self.downs), job) if job else max(self.downs)
                return

            # wtf srsly find smallest up job
            if self.ups:
                self.destination_floor = min(min(self.ups), job) if job else min(self.ups)
                return

            if job:
                self.destination_floor = job
                return
        else:
            # prefer down

            # Largest down jobs below us
            dest = filter(lambda x: x < self.callbacks.current_floor, self.downs + self.selected)
            if dest:
                self.destination_floor = max(dest)
                return

            job = min(self.selected) if self.selected else None # Jobs selected on the lift
            # Smallest up jobs
            if self.ups:
                self.destination_floor = min(min(self.ups), job) if job else min(self.ups)
                return

            # Largest down jobs above us
            if self.downs:
                self.destination_floor = max(max(self.downs), job) if job else max(self.downs)
                return

            if job:
                self.destination_floor = job

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
            self.selected.append(floor)
            self.update_destination()
            self.update_state()
            return

        if (floor > self.callbacks.current_floor and self.state == UP) or (
                floor < self.callbacks.current_floor and self.state == DOWN):
            if floor not in self.selected:
                self.selected.append(floor)

        self.update_destination()

    def on_floor_changed(self):
        if self.destination_floor == self.callbacks.current_floor:
            if self.callbacks.current_floor in self.selected:
                # C-C-C-COMBO!
                self.selected.remove(self.callbacks.current_floor) # either way remove selected floor
            if self.state == UP:
                if self.callbacks.current_floor in self.ups:
                    self.ups.remove(self.callbacks.current_floor)
                elif not self.ups and self.callbacks.current_floor in self.downs:
                    self.downs.remove(self.callbacks.current_floor)
                    self.state = DOWN # change direction
            elif self.state == DOWN:
                if self.callbacks.current_floor in self.downs:
                    self.downs.remove(self.callbacks.current_floor)
                elif not self.downs and self.callbacks.current_floor in self.ups:
                    self.ups.remove(self.callbacks.current_floor)
                    self.state = UP

            self.callbacks.motor_direction = None
            self.destination_floor = None
            # self.update_destination()

    def log(self):
        print "Dest: %s" % self.destination_floor
        print "ups: %s" % self.ups
        print "downs: %s" % self.downs
        print "selected: %s" % self.selected

    def on_ready(self):
        self.update_destination()
        # self.log()
        if not self.destination_floor:
            self.callbacks.motor_direction = None
            self.state = None
            return

        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None
            if self.state == UP:
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
