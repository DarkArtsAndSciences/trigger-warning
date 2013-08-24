package {
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.display.BlendMode;
	import flash.events.TimerEvent;
	import flash.utils.*;

	public class Game extends MovieClip {
		var startTime:Number;

		public function Game() {
			startTime = getTimer();
			var clockUpdateTimer = new Timer(1000);
			function updateClock(e:TimerEvent):void {
				var elapsedTime = getTimer() - startTime;
				var seconds = Math.floor(elapsedTime / 1000) % 60;
				var minutes = Math.floor(elapsedTime / 1000 / 60);
				var zero = seconds < 10 ? "0" : "";
				clockText.text = minutes + ":" + zero + seconds;
			}
			clockUpdateTimer.addEventListener(TimerEvent.TIMER, updateClock);
			clockUpdateTimer.start();

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
