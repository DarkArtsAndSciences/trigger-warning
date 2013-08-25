package {
	import flash.media.Sound;

	public class Effect {
		var time:Number = 0;
		var sound:Sound;
		var action:Function;

		public function Effect(time:Number, sound:Sound, action:Function) {
			this.action = action;
			this.sound = sound;
			this.time = time;
		}

		public function affect(location):void {
			sound.play();
			action(location);
		}
	}
}
