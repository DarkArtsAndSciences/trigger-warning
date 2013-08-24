package {
	import flash.utils.*;

	public class Trigger {
		var startTime;
		var interval;
		var effect;  // function to be called on fire

		public function Trigger(effectFunction:Function) {
			startTime = getTimer();
			interval = setInterval(fire, 10000);
			effect = effectFunction;
		}

		public function check():Boolean {
			return (getTimer() - startTime) > 10000;
		}

		function fire():void {
			//trace("trigger fired");
			clearInterval(interval);
			effect()
		}
	}
}
