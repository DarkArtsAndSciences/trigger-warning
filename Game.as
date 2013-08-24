package {
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.display.BlendMode;

	public class Game extends MovieClip {
		public function Game() {
			// More blend modes here: http://hyperspatial.com/2009/08/how-to-set-textfield-alpha/
			warningText.blendMode = BlendMode.LAYER;

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
