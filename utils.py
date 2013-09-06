import inspect  # get function arguments in log_function_call()
import datetime  # timestamps in log_function_call()

"""
Debugging
"""
def log_function_call(message=""):
	"""Print the calling function's name and arguments."""
	caller_frame = inspect.stack()[1]
	function_name = caller_frame[3]
	args, vargs, kwargs, values = inspect.getargvalues(caller_frame[0])
	pretty_args = ', '.join(['{}={}'.format(arg, repr(values[arg])) for arg in args])
	timestamp = datetime.datetime.now()
	print '{}: {}({}) {}'.format(timestamp, function_name, pretty_args, message)
