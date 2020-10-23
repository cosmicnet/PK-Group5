import pkmodel as pk
#
# Solution class
# Want users to be able to add multiple pairs of models and protocols
# want these to then have ODE solutions that are accessible via plots
# or as array

import numpy
import scipy.integrate

class Solution:
    """The Solution class structures access to the SciPy ODE solver.
    It also contains methods to visualise the solutions for the central compartment,
    in side-by-side or overlay views. The user can add or remove the models and protocols
    to be solved. 
    """
    def __init__(self):
        """Initialises a Solution object, which holds a list of model objects
        and a list of protocol objects. These initialise as empty lists.
        Further documentation on the Model and Protocol classes can be found under
        their methods.
        Args:
            None
        """
        self.models = []
        self.protocols = []

    def add(self, model, protocol):
        """Adds a pair of model and protocol objects to the solution object.
        The attributes and methods of the Model and Protocol classes can be 
        found in their documentation.

        Args:
            model (pkmodel Model): the model object containing the parameters for
                the ODE solver
            protocol (pkmodel Protocol): the protocol object containing the parameters
                of the dose and time span for the ODE solver
        """
        # Verify the type of the model and protocol arguments
        if type(model) != pk.Model:
            raise TypeError('The model must be a pkmodel Model')
        if type(protocol) != pk.Protocol:
            raise TypeError('The protocol must be a pkmodel Protocol')
        # Add the model and protocol to their lists
        self.models.append(model)
        self.protocols.append(protocol)

    @property
    def list_compartments(self):
        """Returns a list of tuples of (model, protocol) combinations
        in the solution object.

        Args:
           None
        """
        out = []
        # We assume protocols same length as methods, because the user only adds
        # them as a pair.
        for i in range(0, len(self.models)):  
            out.append((self.models[i], self.protocols[i]))
        return out 

    def remove(self, index: int):
        """Removes a model and protocol pair from the models and
        protocols lists in the solution class. Choose which pair to
        remove by finding its index in Solution.list_compartments().
        Pair should have the same index as they can only be added together.

        Args:
            index (int): the index of the model and protocol pair to be removed.
                As given in Solution.list_compartments().
        """
        if type(index) != int:
            raise TypeError('The index must be an integer')
        del self.models[index]
        del self.protocols[index]

    def ode_system(self, q, t, model, protocol):
        """Takes as input an array-like list of variables q, a float time t, 
        a Model object and a Protocol object, then returns the system of ODEs 
        for this pair.

        Args:
            q (array-like object of variables q)
            t (float): time [hours]
            model (Model object)
            protocol (Protocol object)

        Returns: 
            1-D list of functions of ordinary differential equations 
        """
        dose_fn = protocol.dose()

        if model.delivery_mode == 'iv':
            num_variables = len(model.list_compartments())
        elif model.delivery_mode == 'sc':
            num_variables = len(model.list_compartments()) + 1
        
        # in the iv case, q0=qc
        # in the sc case, q0=input compartment, and q1=qc

        # get the global model parameters
        v_c = model.v_c
        cl = model.cl
        ka = model.ka
        # get the parameters for each compartment
        # this is a list which
        compartment_parameters = model.list_compartments()
        # now extract the ones we need
        q_p = [qp for (v, qp) in compartment_parameters]
        v_p = [vp for (vp, q) in compartment_parameters]

        # create a list of transitions

        transitions = [q_p[i] * ((q[0] / v_c) - (q[i] / v_p[i])) for i in range(1, num_variables)]

        if model.delivery_mode == 'iv':
            central = dose_fn(q, t) - (q[0] / v_c) * cl  # need to pass this dose_fn q,t as we need it in float type
            # now update central to include transitions
            for transition in transitions:
                central += transition
            return [central].append(transitions)

        elif model.delivery_mode == 'sc':
            input = dose_fn(q, t) - ka * q[0]
            central = ka * q[0] - (q[1] / v_c) * cl
            for transition in transitions:
                central += transitions
            return [input, central].append(transitions)

    def solution(self, model, protocol, time):
        """Calcuates the ODE solution for a specific model and protocol
        using SciPy .odeint(). 

        Args:
            model (Model object)
            protocol (Protocol object)
            time (tuple: t0, tmax): t0 start of the integration and tmax the end

        Returns: 
            numpy (ndarray): the numerical solutions to the system
        """
        if model.delivery_mode == 'iv':
            num_variables = len(model.list_compartments()) + 1
        elif model.delivery_mode == 'sc':
            num_variables = len(model.list_compartments()) + 2

        y0 = numpy.zeros((num_variables), dtype=float)
        # Set the first element of the initial conditions array y0
        # to be the initial value of the 0th compartment, which is the 
        # compartment in which we get drug delivery (central for intravenous)
        if model.delivery_mode == 'iv':
            y0[0] = protocol.initial_dose
        elif model.delivery_mode == 'sc':
            y0[1] = protocol.initial_dose
        # Now we need to define the model in terms of ODEs
        system = lambda t, q: self.ode_system(q, t, model=model,
            protocol=protocol)
        
        time_span = [time[0], time[-1]]
        numerical_solution = scipy.integrate.solve_ivp(fun=system, y0=y0,
            t_span=time_span, t_eval=time)
        print("Numerical soln is")
        print(numerical_solution)

        # need to unpack the t and y arrays from numerical_solution

        time = numerical_solution.t
        numerical_solution = numerical_solution.y # cut down the output to just the integrated solution

        # TODO: update this to the new model modes
        if model.delivery_mode == 'iv':
            return numerical_solution[0]  # the numerical solution for intravenous dosing
        elif model.delivery_mode == 'sc':
            return numerical_solution[1]  # the numerical solution for subcutaneous dosing
        else:
            raise ValueError("Model delivery mode incorrectly defined. Options are: 'intravenous', or 'subcutaneous'.")

    def visualise(self, layout='overlay', time_res=100):
        """Plots the ODE solutions of the model using Matplotlib.
        Layout can be chosen to be overlay or side-by-side.
        Currently supports up to two side-by-side plots.
        Time resolution defaults to 100 time steps but can be changed
        by the user as desired.

        Args:
            layout (str): either 'overlay' or 'side_by_side,' defaults
               to 'overlay.' Specifies if the solutions are shown overlaying
               each other on one plot or as independent subplots side by side.
            time_res (int): the time resolution, specified as the number of 
                elements in the time and ODE solution array used for plotting.
        """
        # Generate tuples with (model, protocol) pairs as a list of tuples
        inputs = self.list_compartments()
        # Generate figures to be populated with 'overlay' or 'side-by-side' plots
        if (layout == 'overlay') or (layout == 'side_by_side' and len(inputs) == 1): #make empty figure
            fig = matplotlib.pyplot.figure(figsize=(10.0, 3.0))
        if layout == 'side_by_side' and len(inputs) == 2:
            fig = matplotlib.pyplot.figure(figsize=(10.0, 3.0))
            plot1 = fig.add_subplot(1, 2, 1)
            plot2 = fig.add_subplot(1, 2, 2)
        else:
            raise ValueError('Solution.Visualise() supports overlay or side-by-side plots with max of 2 inputs')
        # Loop over (model, protocol) objects to solve and then plot each
        for input in inputs:
            i = 0
            model = input[0]  # the model object is the first in the tuple
            protocol = input[1]  # the protocol object is the second in the tuple
            time = numpy.linspace(0, protocol.time_span, time_res) # generate time array
            ODE_solution = self.solution(model, protocol, time_res) # a function of the time array
            if (layout == 'overlay') or (layout == 'side_by_side' and len(inputs == 1)):
                fig.plot(time, ODE_solution)
            if layout == 'side_by_side' and len(inputs) == 2:
                if i == 0:
                    plot1.plot(time, ODE_solution)
                if i == 1:
                    plot2.plot(time, ODE_solution)
            i = i + 1
        matplotlib.pyplot.show()
