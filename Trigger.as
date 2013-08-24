package {
	import flash.utils.*;
	import Warning;

	public class Trigger {
		var startTime:Number;
		var interval:Number;
		var warning:Warning;
		var effect:Effect;

		public function Trigger(warning:Warning, effect:Effect) {
			startTime = getTimer();
			interval = setInterval(fire, 10000);
			this.warning = warning;
			this.effect = effect;
			warn();
		}

		public function check():Boolean {
			return (getTimer() - startTime) > 10000;
		}

		public function warn():void {
			warning.warn();
		}

		public function fire():void {
			effect.affect();
			clearInterval(interval);
		}
	}
}
