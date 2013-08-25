package {
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.events.*;
	import flash.geom.Point;
	import flash.utils.*;

	public class Game extends MovieClip {
		var startTime:Number;
		var elapsedTime:Number;
		var isMouseDown = false;

		var gameOverTrigger:Trigger;

		public function Game() {
			// main game loop
			addEventListener(Event.ENTER_FRAME, onEnterFrame);

			// controls
			stage.addEventListener(MouseEvent.MOUSE_DOWN, mouseDown);
			stage.addEventListener(MouseEvent.MOUSE_UP, mouseUp);

			// clock
			startTime = getTimer();
			var clockUpdateTimer = new Timer(1000);
			clockUpdateTimer.addEventListener(TimerEvent.TIMER, updateClock);
			clockUpdateTimer.start();

			// triggers
			var gameOverWarning = new Warning(new SadSound(), "game over", null);
			var gameOverEffect = new Effect(0, new FailSound(), gameOver);
			gameOverTrigger = new Trigger(startTime + 30000, gameOverWarning, gameOverEffect);
			gameOverTrigger.locationType = "center";
			addChild(gameOverTrigger);

			// boids
			for (var i = 0; i < 25; i++) {
				var b = new Boid();
				addChild(b);
			}
		}

		function onEnterFrame(e:Event):void {
			Trigger.fire(elapsedTime);
		}

		function mouseDown(e:MouseEvent):void {
			isMouseDown = true;
		}

		function mouseUp(e:MouseEvent):void {
			isMouseDown = false;
			var sound = new CrashSound();
			sound.play();
			Boid.startle(new Point(e.localX, e.localY), 100, 1, 0.1);
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
			Boid.startle(location, 200, 10, 0.5);
		}
	}
}
