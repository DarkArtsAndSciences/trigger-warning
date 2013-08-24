package {
	import flash.utils.*;
	import Warning;

	public class Trigger {
		var startTime;
		var interval;
		var warning;
		var effect;

		public function Trigger(warning:Warning, effect:Effect) {
			startTime = getTimer();
			interval = setInterval(fire, 10000);
			this.warning = warning;
			this.effect = effect;
		}

		public function check():Boolean {
			return (getTimer() - startTime) > 10000;
		}

		public function warn():void {
			warning.warn();
			effect.warn();
		}

		public function fire():void {
			effect.affect();
			clearInterval(interval);
		}
	}
}
