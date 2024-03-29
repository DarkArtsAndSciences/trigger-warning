package {
	import flash.display.MovieClip;
	import flash.display.BlendMode;
	import flash.geom.Point;
	import flash.text.TextField;
	import flash.events.TimerEvent;
	import flash.utils.Timer;

	public class Trigger extends MovieClip {
		private static var game:Game;
		private static var instances:Array = [];

		var startTime:Number;
		var endTime:Number;
		var warning:Warning;
		var effect:Effect;
		var locationType:String;
		var location:Point;
		var live:Boolean = false;

		public function Trigger(time:Number, warning:Warning, effect:Effect) {
			instances.push(this);
			this.warning = warning;
			this.effect = effect;
			this.startTime = time;
			this.endTime = time + Game.tenSeconds;

			// More blend modes here: http://hyperspatial.com/2009/08/how-to-set-textfield-alpha/
			warningText.blendMode = BlendMode.LAYER;
		}

		public static function registerGame(g:Game) {
			game = g;
		}


		public function pretty():String {
			return "[Trigger at " + Math.floor(startTime/1000) + "s: " + warning.text + "]";
		}

		public function saveLocation():void {
			if (!locationType) location = null;
			if (locationType == "center") location = new Point(400, 300);
			if (locationType == "mouse") location = new Point(mouseX, mouseY);
		}

		public static function timeOffset():Number {
			var offset = 0;
			for (var i in instances)
				if (instances[i].live)
					offset += instances[i].effect.time;
			return offset;
		}

		public static function fire(gameTime:Number):void {
			for (var i in instances) {
				// trigger warning
				if ((!instances[i].live) && (gameTime > instances[i].startTime) && (gameTime < instances[i].endTime)) {
					trace("warning " + instances[i].pretty());
					instances[i].saveLocation();
					instances[i].warning.warn(instances[i].location);
					instances[i].warningText.text = instances[i].warning.text;
					instances[i].warningText.alpha = 1.0;
					var timer = new Timer(100, 100);
					function fade(e:TimerEvent):void {
						instances[i].warningText.alpha -= 0.01;
					}
					function fadeEnd(e:TimerEvent):void {
						timer.stop();
					}
					timer.addEventListener(TimerEvent.TIMER, fade);
					timer.addEventListener(TimerEvent.TIMER_COMPLETE, fadeEnd);
					timer.start();
					instances[i].live = true;
				}

				// trigger effect
				if ((instances[i].live) && (gameTime > instances[i].endTime)) {
					trace("triggering " + instances[i].pretty());
					instances[i].effect.affect(instances[i].location);
					instances[i].live = false;
				}
			}
		}
	}
}
