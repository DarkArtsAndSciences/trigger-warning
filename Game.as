package {
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.events.*;
	import flash.geom.Point;
	import flash.utils.*;

	public class Game extends MovieClip {
		var startTime:Number;
		var elapsedTime:Number;

		var gameOverTrigger:Trigger;

		public function Game() {
			// main game loop
			addEventListener(Event.ENTER_FRAME, onEnterFrame);

			// controls
			stage.addEventListener(MouseEvent.CLICK, onMouseClick);

			// clock
			startTime = getTimer();
			var clockUpdateTimer = new Timer(1000);
			clockUpdateTimer.addEventListener(TimerEvent.TIMER, updateClock);
			clockUpdateTimer.start();

			// triggers
			var gameOverWarning = new Warning(new SadSound(), "game over in 10s", null);
			var gameOverEffect = new Effect(0, new FailSound(), function(location){gameOver(location);});
			gameOverTrigger = new Trigger(startTime + 2000, gameOverWarning, gameOverEffect);
			gameOverTrigger.locationType = "mouse";
			addChild(gameOverTrigger);

			// boids
			for (var i = 0; i < 50; i++) {
				var b = new Boid();
				addChild(b);
			}
		}

		function onEnterFrame(e:Event):void {
			Trigger.fire(elapsedTime);
		}

		function onMouseClick(e:MouseEvent):void {
			var sound = new CrashSound();
			sound.play();
			Boid.startle(new Point(e.localX, e.localY), 150, 3);
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

		function gameOver(location):void {
			trace("game over at " + location);
			Boid.startle(location, 200, 10);
		}
	}
}
