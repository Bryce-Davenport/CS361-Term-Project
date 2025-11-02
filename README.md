# CS361

For the course project, you'll be designing and implementing software that uses the microservices architecture. In this architecture, software is split into multiple programs that run in different processes. The "microservices" are programs that provide functionality to other programs. Often, microservices are small and have just one purpose. Each microservice is a "black box". Example: The Currency Converter microservice has a function named "convertCurrency", but other programs cannot call that function directly (e.g., they cannot call convertCurrency('USD','GBP',100)). The Currency Converter microservice only accepts indirect requests to use its functionality and those requests must adhere to a particular format.

The course project you design and implement during this course will consist of a main program with a user interface and multiple microservices your main program calls. You and your teammates will work together to create a pool of microservices.

Your course project will have two main pieces:

    A main program that you make. You design and implement your main program ON YOUR OWN (clarification added 10/22/25). Your main program must request data, receive data, and use data from multiple microservices in the pool. It must also have a user interface (ex: command-line / text-based, GUI, voice control, etc.).
    Pool of microservices you help implement, and that are called by your main program. You design and implement the microservices WITH YOUR TEAM (clarification added 10/22/25). The pool will start small ("Small Pool"), then your team will add to it (resulting in the "Big Pool").

For implementation, you get to choose your programming languages. You can even choose to write your main program in a different language than the microservices you implement for your main program to call.
