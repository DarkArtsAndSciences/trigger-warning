package {
	import flash.display.MovieClip;
	import flash.text.TextField;

	public class Game extends MovieClip {
		public function Game() {
			var crashWarning = new Warning(crashWarningFunction, new CrashSound(), "crash", warningText);
			function crashWarningFunction() {
				trace("crash warning");
			}

			var failEffect = new Effect(action, new FailSound());
			function action() {
				trace("failure");
			}

			var t = new Trigger(crashWarning, failEffect);
		}
	}
}
