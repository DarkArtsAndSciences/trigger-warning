import Trigger;

var w = new Warning(warning, new CrashSound(), "crash");
function warning() {
	trace("warning function");
}

var e = new Effect(action, new FailSound());
function action() {
	trace("action");
}

var t = new Trigger(w, e);
