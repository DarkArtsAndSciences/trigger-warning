package {
	import Warning;

	public class Trigger {
		static var tenSeconds = 10000;
		static var instances:Array = [];

		var startTime:Number;
		var endTime:Number;
		var warning:Warning;
		var effect:Effect;
		var live:Boolean = false;

		public function Trigger(time:Number, warning:Warning, effect:Effect) {
			instances.push(this);
			this.warning = warning;
			this.effect = effect;
			this.startTime = time;
			this.endTime = time + tenSeconds;
		}

		public function toString():String {
			return "[Trigger " + startTime + "-" + endTime + "]";
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
				if ((!instances[i].live) && (gameTime > instances[i].startTime) && (gameTime < instances[i].endTime)) {
					trace("warning " + instances[i]);
					instances[i].warning.warn();
					instances[i].live = true;
				}
				if ((instances[i].live) && (gameTime > instances[i].endTime)) {
					trace("triggering " + instances[i]);
					instances[i].effect.affect();
					instances[i].live = false;
				}
			}
		}
	}
}
