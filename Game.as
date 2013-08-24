package {
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.display.BlendMode;
	import flash.events.*;
	import flash.utils.*;

	public class Game extends MovieClip {
		var startTime:Number;
		var elapsedTime:Number;

		public function Game() {
			addEventListener(Event.ENTER_FRAME, onEnterFrame);

			startTime = getTimer();
			var clockUpdateTimer = new Timer(1000);
			clockUpdateTimer.addEventListener(TimerEvent.TIMER, updateClock);
			clockUpdateTimer.start();

			// More blend modes here: http://hyperspatial.com/2009/08/how-to-set-textfield-alpha/
			warningText.blendMode = BlendMode.LAYER;

			var crashWarning = new Warning(crashWarningFunction, new CrashSound(), "crash", warningText);
			function crashWarningFunction() {
				trace("crash warning");
			}

			var failEffect = new Effect(action, new FailSound(), 0);
			function action() {
				trace("failure");
			}

			var t1 = new Trigger(startTime + 1000, crashWarning, failEffect);
			var t2 = new Trigger(startTime + 7000, crashWarning, failEffect);

			for (var i = 0; i < 25; i++) {
				var b = new Boid();
				addChild(b);
			}
		}

		function onEnterFrame(e:Event):void {
			Trigger.fire(elapsedTime);
		}

		function updateClock(e:TimerEvent):void {
			var timeOffset = Trigger.timeOffset();
			var flooredOffset = Math.floor(timeOffset/1000);
			var sign = flooredOffset > 0 ? "+" : "";
			offsetText.text = flooredOffset != 0 ? sign + flooredOffset : "";

			elapsedTime = getTimer() + timeOffset - startTime;
			var minutes = Math.floor(elapsedTime / 1000 / 60);
			sign = minutes < 0 ? "-" : "";
			if (minutes < 0) minutes++;
			var seconds = Math.abs(Math.floor(elapsedTime / 1000) % 60);
			var zero = seconds < 10 ? "0" : "";
			clockText.text = sign + minutes + ":" + zero + seconds;
		}
	}
}
