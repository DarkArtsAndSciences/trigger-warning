package {
	import flash.utils.*;

	public class Trigger {
		var startTime;
		var interval;

		public function Trigger() {
			startTime = getTimer();
			interval = setInterval(fire, 10000);
		}

		public function check():Boolean {
			return (getTimer() - startTime) > 10000;
		}

		function fire():void {
			trace("trigger fired");
			clearInterval(interval);
		}
	}
}
