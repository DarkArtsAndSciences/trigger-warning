package {
	import flash.display.MovieClip;
	import flash.display.BlendMode;
	import flash.text.TextField;
	import flash.events.*;
	import flash.geom.Point;
	import flash.utils.*;

	public class Game extends MovieClip {
		public static var tenSeconds:Number = 10 * 1000;

		// perFrame * once per frame * ten seconds = 1.0
		// Something that happens once per frame will finish in ten seconds.
		// At 30fps, perFrame == 1/300 or .00333
		public static var perFrame:Number;

		var startTime:Number;
		var elapsedTime:Number;
		var isMouseDown = false;
		var markers:Array = [];
		var gameOverTrigger:Trigger;

		public function Game() {
			// give other classes easy access to this instance
			Boid.registerGame(this);
			Trigger.registerGame(this);
			Warning.registerGame(this);
			Effect.registerGame(this);

			// calculate perFrame from frame rate
			perFrame = 1/stage.frameRate * 1/10;

			// mouse controls
			stage.addEventListener(MouseEvent.MOUSE_DOWN, function (e:MouseEvent):void {
				isMouseDown = true;
			});
			stage.addEventListener(MouseEvent.MOUSE_UP, function (e:MouseEvent):void {
				isMouseDown = false;
				var sound = new CrashSound();
				sound.play();
				Boid.startle(new Point(e.localX, e.localY), 100, 1, 0.2);
			});

			// clock
			startTime = getTimer();
			var clockUpdateTimer = new Timer(1000);  // once per second
			clockUpdateTimer.addEventListener(TimerEvent.TIMER, function updateClock(e:TimerEvent):void {
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
			});
			clockUpdateTimer.start();

			// triggers
			var startWarning = new Warning(new CrashSound(), "game starting", function () {
				trace("game starting");
			});
			var startGameEffect = new Effect(0, new SweepSound(), function () {
				// set game time to zero
				startTime = getTimer();
			});

			// add on collision
			var edgeTrigger = new Trigger(startTime + tenSeconds, startWarning, startGameEffect);
			addChild(edgeTrigger);

			var gameOverWarning = new Warning(new SadSound(), "game over", null);
			var gameOverEffect = new Effect(0, new FailSound(), gameOver);
			gameOverTrigger = new Trigger(startTime + 3*tenSeconds, gameOverWarning, gameOverEffect);
			gameOverTrigger.locationType = "center";
			addChild(gameOverTrigger);

			// boids
			for (var i = 0; i < 25; i++) {
				var b = new Boid();
				addChild(b);
			}

			// onEnterFrame
			addEventListener(Event.ENTER_FRAME, function (e:Event):void {
				Trigger.fire(elapsedTime);
				for (var m in markers) {
					markers[m].alpha - perFrame;
				}
			});
		}

		function gameOver(location):void {
			Boid.startle(location, 200, 10, 0.1);
		}

		function mark(location):void {
			var marker = new Avoid();
			marker.x = location.x;
			marker.y = location.y;
			marker.blendMode = BlendMode.LAYER;
			addChild(marker);
			markers.add(marker);
		}
	}
}
