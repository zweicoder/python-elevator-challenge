UP = 1
DOWN = 2
FLOOR_COUNT = 6


class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    class Elevator(Elevator):
...     def __init__(self, logic_delegate, starting_floor=1):
...         self._current_floor = starting_floor
...         print "%s..." % starting_floor,
...         self._motor_direction = None
...         self._logic_delegate = logic_delegate
...         self._logic_delegate.callbacks = self.Callbacks(self)
...
...     class Callbacks(object):
...         def __init__(self, outer):
...             self._outer = outer
...
...         @property
...         def current_floor(self):
...             return self._outer._current_floor
...
...         @property
...         def motor_direction(self):
...             return self._outer._motor_direction
...
...         @motor_direction.setter
...         def motor_direction(self, direction):
...             self._outer._motor_direction = direction
    """

    def __init__(self):
        # Feel free to add any instance variables you want.
        self.destination_floor = None
        self.callbacks = None
        self.ups = []  # floors to stop at if it's going up
        self.downs = []  # floors to stop at if it's going down
        self.state = None  # The direction our elevator is heading towards, regardless of whether it's moving

    def update_destination(self):
        """
        if not ups and not downs
            self.destination_floor = None
        if goingUp():
            currentDest = getMin(ups)

        else:
            ditto for max
        """
        if not self.ups and not self.downs:
            self.destination_floor = None
            return

        if self.state == UP:
            # prefer up
            if self.ups:
                self.get_up()
            else:
                self.get_down()

        else:
            #prefer down
            if self.downs:
                self.get_down()
            else:
                self.get_up()
        self.log()
    def get_up(self):
        self.destination_floor = min(self.ups)

    def get_down(self):
        self.destination_floor = max(self.downs)

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down

        Pseudocode:
        if floor == current_floor:
        	return

    	if not moving:
    	    goTo(floor)
    	    return

    	if sameDirection(direction):
    	    assignToSameDirection(direction)
    	else:
    	    assignToOppDirection(direction)

    	if floor not in preferred:
    		preferred.insert(floor)

    	self.update_destination()
        """
        if floor == self.callbacks.current_floor:
            return

        if not self.state:
            if direction == UP:
                self.ups.append(floor)
            elif direction == DOWN:
                self.downs.append(floor)
            self.update_destination()
            self.update_state()
            return

        if self.state == direction:
            preferred = self.ups if direction == UP else self.downs
        else:
            preferred = self.downs if direction == UP else self.ups

        if floor not in preferred:
            preferred.append(floor)

        self.update_destination()

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested

        Pseudocode:
        if sameFloor:
            return
        if not moving:
            goTo(floor)
            return

        if floor > currentFloor and goingUp:
            ups.append(floor)
        elif floor < currentFloor and goingDown:
            downs.append(floor)
        else:
            ignore
        self.update_destination()
        """
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
            self.ups.append(floor)
        elif floor < self.callbacks.current_floor and self.state == DOWN:
            self.downs.append(floor)

        self.update_destination()

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        if self.destination_floor == self.callbacks.current_floor:
            # Clean up jobs
            if self.state == UP:
                if not self.ups:
                    # Only way ups is empty is when we are moving up for a downs job
                    self.downs.remove(self.destination_floor)
                else:
                    # Remove completed job in ups
                    self.ups.remove(self.destination_floor)
            elif self.state == DOWN:
                if not self.downs:
                    self.ups.remove(self.destination_floor)
                else:
                    self.downs.remove(self.destination_floor)

            # Change state
            if self.state == UP:
                if not self.ups:
                    if self.downs:
                        self.state = DOWN
                    else:
                        # No more jobs
                        self.state = None
            elif self.state == DOWN:
                if not self.downs:
                    if self.ups:
                        self.state = UP
                    else:
                        # No more jobs
                        self.state = None
            self.callbacks.motor_direction = None
            self.destination_floor = None
            self.update_destination()
    def log(self):
        print "Dest: %s" % self.destination_floor
        print "Current: %s" % self.callbacks.current_floor
        print "ups: %s"% self.ups
        print "downs: %s" % self.downs
    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        self.update_destination()
        # self.log()
        if not self.destination_floor:
            self.callbacks.motor_direction = None
            self.state = None
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
