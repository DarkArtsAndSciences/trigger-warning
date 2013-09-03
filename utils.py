import inspect  # get function arguments in log_function_call()

"""
Debugging
"""
def log_function_call(message=""):
	"""Print the calling function's name and arguments."""
	caller_frame = inspect.stack()[1]
	function_name = caller_frame[3]
	args, vargs, kwargs, values = inspect.getargvalues(caller_frame[0])
	pretty_args = ', '.join(['{}={}'.format(arg, values[arg]) for arg in args])
	print '{}({}) {}'.format(function_name, pretty_args, message)
