package {
	import flash.media.Sound;

	public class Effect {
		var action:Function;
		var sound:Sound;
		var time:Number = 0;

		public function Effect(action:Function, sound:Sound, time:Number) {
			this.action = action;
			this.sound = sound;
			this.time = time;
		}

		public function affect():void {
			sound.play();
			action();
		}
	}
}
